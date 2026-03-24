import pytest
import time
import uuid
from typing import Generator, Optional
from datetime import datetime
from pathlib import Path

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
from core.reporting.test_report_manager import get_test_report_manager
from core.integrations.jira_gateway import JiraGateway as JiraClient
from core.integrations.testrail_gateway import TestRailGateway as TestRailClient

# â­ MCP optional import
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
    parser.addoption("--env", action="store", default=None, help="Execution environment (matches environments/<name>.env)")
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
def context(browser: Browser, pytestconfig, request) -> Generator[BrowserContext, None, None]:
    debug_mode = pytestconfig.getoption("--debug-mode")
    
    # Create unique per-test video directory (prevents parallel collisions)
    execution_date = datetime.now().strftime("%Y-%m-%d")
    video_dir = Path(f"reports/{execution_date}/temp_videos/{uuid.uuid4().hex}")
    video_dir.mkdir(parents=True, exist_ok=True)

    # Attach to the test item for later organization in pytest_runtest_protocol
    request.node.video_source_dir = video_dir

    context = browser.new_context(
        record_video_dir=str(video_dir),
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
# â­ MCP CLIENT FIXTURE (MAIN INTEGRATION POINT)
# =========================================================

@pytest.fixture(scope="function")
def mcp_client(pytestconfig, env_config) -> Optional["MCPClient"]:
    """
    Optional MCP execution layer.
    Returns None when MCP disabled â†’ framework falls back to POM.
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
# FAILURE HOOK - CUSTOM SCREENSHOT & VIDEO NAMING
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
                # Get test report manager
                report_manager = get_test_report_manager()
                test_name = item.nodeid.split("::")[-1].split("[")[0]
                
                # Save screenshot with proper naming and folder structure
                test_folder = report_manager.get_test_folder(test_name)
                screenshot_filename = report_manager.get_screenshot_filename(test_name)
                screenshots_dir = test_folder / "screenshots"
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = screenshots_dir / screenshot_filename
                
                page.screenshot(path=str(screenshot_path), full_page=True)

                trace = None
                if context and getattr(context, "_codex_tracing_started", False):
                    trace = f"reports/traces/{test_name}_{uuid.uuid4().hex[:8]}.zip"
                    context.tracing.stop(path=trace)
                    context._codex_tracing_started = False

                logger = get_logger("FailureHook")
                logger.error(f"FAILED: {item.nodeid}")
                logger.error(f"Screenshot â†’ {screenshot_path}")
                logger.error(f"Report Structure: {report_manager.date_folder}")

                if jira_client:
                    jira_client.create_issue(
                        summary=f"Automation Failure: {item.nodeid}",
                        description=f"Env: {env_config.current_env}\nError: {call.excinfo}",
                        attachments=[str(path) for path in (screenshot_path, trace) if path],
                        labels=["automation", "failure"],
                        env_metadata={"env": env_config.current_env}
                    )

        except Exception as e:
            logger = get_logger("FailureHook")
            logger.error(f"Failure hook error: {e}")


# =========================================================
# VIDEO ORGANIZATION HOOK
# =========================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """Hook to organize videos with proper naming after test execution."""
    outcome = yield
    
    try:
        # Get test name
        test_name = item.nodeid.split("::")[-1].split("[")[0]
        report_manager = get_test_report_manager()

        # Determine source directory for this test
        video_source_dir = getattr(item, "video_source_dir", None)
        if not video_source_dir:
            execution_date = datetime.now().strftime("%Y-%m-%d")
            video_source_dir = Path(f"reports/{execution_date}/videos")

        if video_source_dir and video_source_dir.exists():
            video_files = list(video_source_dir.glob("*.webm"))
            if video_files:
                test_folder = report_manager.get_test_folder(test_name)
                videos_folder = test_folder / "videos"
                videos_folder.mkdir(parents=True, exist_ok=True)

                for video_file in video_files:
                    video_filename = report_manager.get_video_filename(test_name)
                    video_destination = videos_folder / video_filename

                    retries = 3
                    for attempt in range(retries):
                        try:
                            video_file.replace(video_destination)
                            logger = get_logger("VideoOrganization")
                            logger.info(f"Video saved: {video_destination}")
                            break
                        except (PermissionError, OSError) as exc:
                            if attempt == retries - 1:
                                logger = get_logger("VideoOrganization")
                                logger.warning(f"Video move failed after {retries} attempts: {exc}")
                            else:
                                time.sleep(0.2)
                                continue

                # Clean up temporary source directories after successful moves
                try:
                    if not any(video_source_dir.iterdir()):
                        video_source_dir.rmdir()
                except OSError as cleanup_exc:
                    logger = get_logger("VideoOrganization")
                    logger.warning(f"Failed to cleanup temp source folder: {cleanup_exc}")

        # global temp cleanup of stale empty subfolders
        try:
            execution_date = datetime.now().strftime("%Y-%m-%d")
            temp_videos_root = Path(f"reports/{execution_date}/temp_videos")
            if temp_videos_root.exists():
                for sub in temp_videos_root.iterdir():
                    if sub.is_dir() and not any(sub.iterdir()):
                        sub.rmdir()
                if not any(temp_videos_root.iterdir()):
                    temp_videos_root.rmdir()
        except Exception as cleanup_exc:
            logger = get_logger("VideoOrganization")
            logger.warning(f"Temp video root cleanup failed: {cleanup_exc}")

    except Exception as e:
        logger = get_logger("VideoOrganization")
        logger.warning(f"Video organization error: {e}")
