import pytest
import uuid
from typing import Generator, Optional

from playwright.sync_api import Browser, BrowserContext, Page
from core.config.runtime_config import EnvConfig
from core.config.environment_manager import get_env_config

from core.data_engine.json_data_provider import JsonUserProvider
from core.data_engine.json_data_provider import JsonCheckoutProvider

from app.ui.pages.login_page import LoginPage
from app.ui.pages.inventory_page import InventoryPage
from app.ui.pages.cart_page import CartPage
from app.ui.pages.checkout_page import CheckoutPage

from app.ui.components.cart_widget_component import CartWidgetComponent

from core.reporting.telemetry_client import get_logger
from core.integrations.jira_gateway import JiraGateway as JiraClient
from core.integrations.testrail_gateway import TestRailGateway as TestRailClient

# ⭐ MCP optional import
try:
    from tools.mcp.mcp_client import MCPClient
    MCP_AVAILABLE = True
except Exception:
    MCP_AVAILABLE = False
    MCPClient = None

pytest_plugins = (
    "test_suites.bdd.step_definitions.api_steps",
    "test_suites.bdd.step_definitions.auth_steps",
    "test_suites.bdd.step_definitions.cart_steps",
    "test_suites.bdd.step_definitions.checkout_steps",
    "test_suites.bdd.step_definitions.common_steps",
    "test_suites.bdd.step_definitions.inventory_steps",
    "test_suites.bdd.step_definitions.mcp_steps",
)


# =========================================================
# CLI OPTIONS
# =========================================================

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="staging", help="Execution environment")
    parser.addoption("--debug-mode", action="store_true", help="Headed + slowmo + tracing")
    parser.addoption("--use-mcp", action="store_true", help="Enable AI MCP execution mode")


# =========================================================
# ENV CONFIG
# =========================================================

@pytest.fixture(scope="session")
def env_config(request) -> EnvConfig:
    env_override = request.config.getoption("--env")
    return get_env_config(env_override)


# =========================================================
# BROWSER FIXTURE
# =========================================================

@pytest.fixture(scope="session")
def browser(pytestconfig, env_config) -> Generator[Browser, None, None]:
    from playwright.sync_api import sync_playwright

    debug_mode = pytestconfig.getoption("--debug-mode")
    headed = pytestconfig.getoption("--headed") or debug_mode
    headless = not headed

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        yield browser
        browser.close()


# =========================================================
# CONTEXT FIXTURE
# =========================================================

@pytest.fixture(scope="function")
def context(browser: Browser, pytestconfig) -> Generator[BrowserContext, None, None]:
    debug_mode = pytestconfig.getoption("--debug-mode")

    context = browser.new_context(
        record_video_dir="reports/videos",
        record_video_size={"width": 1280, "height": 720},
        ignore_https_errors=True
    )
    context._codex_tracing_started = False

    if debug_mode:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        context._codex_tracing_started = True

    yield context

    if debug_mode and context._codex_tracing_started:
        trace_name = f"reports/traces/debug_{uuid.uuid4().hex[:8]}.zip"
        context.tracing.stop(path=trace_name)
        context._codex_tracing_started = False

    context.close()


# =========================================================
# PAGE FIXTURE
# =========================================================

@pytest.fixture(scope="function")
def page(context: BrowserContext, env_config) -> Generator[Page, None, None]:
    page = context.new_page()
    page.set_default_timeout(env_config.default_navigation_timeout_ms)
    yield page


# =========================================================
# ⭐ MCP CLIENT FIXTURE (MAIN INTEGRATION POINT)
# =========================================================

@pytest.fixture(scope="function")
def mcp_client(pytestconfig, env_config) -> Optional["MCPClient"]:
    """
    Optional MCP execution layer.
    Returns None when MCP disabled → framework falls back to POM.
    """

    cli_flag = pytestconfig.getoption("--use-mcp")
    mcp_enabled = env_config.mcp_enabled or cli_flag

    if not mcp_enabled:
        pytest.skip("MCP not enabled. Use --use-mcp or set MCP_ENABLED=true.")

    if not MCP_AVAILABLE:
        pytest.skip("MCP requested but MCP client library not installed")

    client = MCPClient(env_config)

    if not client.connect():
        pytest.skip(f"MCP requested but server not reachable at {env_config.mcp_server_url}")

    yield client
    client.disconnect()


# =========================================================
# PAGE OBJECT FIXTURES
# =========================================================

@pytest.fixture
def login_page(page: Page, env_config) -> LoginPage:
    return LoginPage(page, env_config)


@pytest.fixture
def inventory_page(page: Page, env_config) -> InventoryPage:
    return InventoryPage(page, env_config)


@pytest.fixture
def cart_page(page: Page, env_config) -> CartPage:
    return CartPage(page, env_config)


@pytest.fixture
def checkout_page(page: Page, env_config) -> CheckoutPage:
    return CheckoutPage(page, env_config)


@pytest.fixture
def cart_widget(page: Page, env_config) -> CartWidgetComponent:
    return CartWidgetComponent(page, env_config)


# =========================================================
# DATA PROVIDERS
# =========================================================

@pytest.fixture(scope="session")
def user_provider() -> JsonUserProvider:
    return JsonUserProvider()


@pytest.fixture(scope="session")
def checkout_provider() -> JsonCheckoutProvider:
    return JsonCheckoutProvider()


# =========================================================
# INTEGRATION CLIENTS
# =========================================================

@pytest.fixture(scope="session")
def jira_client(env_config) -> JiraClient:
    return JiraClient(env_config)


@pytest.fixture(scope="session")
def testrail_client(env_config) -> TestRailClient:
    return TestRailClient(env_config)


# =========================================================
# FAILURE HOOK
# =========================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        try:
            page = item.funcargs.get("page")
            context = item.funcargs.get("context")
            env_config = item.funcargs.get("env_config")
            jira_client = item.funcargs.get("jira_client")

            if page:
                safe_name = item.nodeid.replace("/", "_").replace("::", "_")
                uid = uuid.uuid4().hex[:8]

                screenshot = f"reports/screenshots/{safe_name}_{uid}.png"
                page.screenshot(path=screenshot, full_page=True)

                trace = None
                if context and getattr(context, "_codex_tracing_started", False):
                    trace = f"reports/traces/{safe_name}_{uid}.zip"
                    context.tracing.stop(path=trace)
                    context._codex_tracing_started = False

                logger = get_logger("FailureHook")
                logger.error(f"FAILED: {item.nodeid}")
                logger.error(f"Screenshot -> {screenshot}")

                if jira_client:
                    jira_client.create_issue(
                        summary=f"Automation Failure: {item.nodeid}",
                        description=f"Env: {env_config.current_env}\nError: {call.excinfo}",
                        attachments=[path for path in (screenshot, trace) if path],
                        labels=["automation", "failure"],
                        env_metadata={"env": env_config.current_env}
                    )

        except Exception as e:
            logger = get_logger("FailureHook")
            logger.error(f"Failure hook error: {e}")
