# QA Automation Platform

A **Playwright + pytest** automation framework for Sauce Demo with comprehensive UI, API, E2E, and BDD testing.

> 👉 **New to this?** Read [README_NONTECHNICAL.md](README_NONTECHNICAL.md) for a complete non-technical guide!

## Features

- ✅ **UI Testing** — Imperative Playwright tests with Page Object Model
- ✅ **API Testing** — Direct backend endpoint validation
- ✅ **E2E Testing** — Complete user journey workflows
- ✅ **BDD Testing** — Business-readable Gherkin scenarios
- ✅ **Multi-Format Reporting** — HTML, JUnit, Allure, screenshots, videos
- ✅ **Retry Logic** — Automatic test retry on transient failures
- ✅ **CI/CD Integration** — GitHub Actions and Jenkins pipelines
- ✅ **Data-Driven** — JSON-based test data management
- ✅ **MCP Support** — Optional Model Context Protocol integration
- ✅ **Smart Wrappers** — Robust element interaction with explicit waits

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
python -m playwright install

# Run all tests (headless)
pytest

# Run tests with visible browser
pytest --headed

# Run E2E tests only
pytest test_suites/e2e/ --headed -v
```

## Running Tests

### Test Execution Modes

| Command | Mode | Use Case |
|---------|------|----------|
| `pytest` | Headless | Fast batch runs, CI/CD pipelines |
| `pytest --headed` | Headed | Development, debugging, learning |
| `pytest --headed -v` | Verbose + Headed | Detailed output with visible browser |
| `pytest --headed -s` | Verbose + Print statements | Debug with console output |

### Test Selection

```bash
# All tests
pytest

# Specific test file
pytest test_suites/ui/test_sauce_login.py --headed

# Specific test function
pytest test_suites/e2e/test_purchase_flow.py::test_purchase_flow --headed

# By marker
pytest -m smoke --headed          # Only smoke tests
pytest -m e2e --headed            # Only E2E tests
pytest -m api --headed            # Only API tests
pytest -m regression --headed     # Full regression suite

# By keyword
pytest -k "login" --headed        # Only tests with "login" in name
pytest -k "not api" --headed      # All tests except API tests
```

### debugging & Troubleshooting

```bash
# Short error output
pytest --tb=short

# No traceback
pytest --tb=no

# Full traceback
pytest --tb=long

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Re-run failed tests only
pytest --lf

# Run N times (for flaky tests)
pytest --count=3

# Debug mode (headed + video + trace + slowmo)
pytest --debug-mode --headed
```

### Test Organization

```
test_suites/
├── ui/              # User interface tests
├── api/             # Backend API tests
├── e2e/             # End-to-end workflows
└── bdd/             # Business-readable scenarios
```

## Why This Structure

The current codebase is organized into four working layers:

- `core/` is the reusable kernel. It owns configuration, reporting, integrations, execution helpers, and data services.
- `app/` is the application interaction layer. It owns page objects, reusable UI components, API clients, and business workflows.
- `test_suites/` is the test intent layer. It owns the runnable tests, BDD features, glue files, and shared step definitions.
- `tools/` holds operational helpers such as the MCP client, MCP stub server, and CLI helpers.

Important note:

- the original target structure used a top-level package named `platform/`
- Python already ships a standard library module named `platform`
- to avoid import conflicts and broken pytest startup, this implementation uses `core/` instead

## Structural Diagram

```text
qa-automation-platform/
  core/
    config/
    data_engine/
    engine/
    integrations/
    reporting/
  app/
    ui/
      pages/
      components/
      workflows/
    api/
      clients/
      service_facades/
    domain/
      models/
      validators/
      transformers/
  test_suites/
    ui/
    api/
    bdd/
      features/
        ui/
        api/
      step_definitions/
      hooks/
    conftest.py
  tools/
    cli/
    mcp/
  data/
  environments/
  pipelines/
  .github/workflows/
  Jenkinsfile
  pytest.ini
  README.md
```

How to read it:

- `core/` is the reusable engine layer
- `app/` is the Sauce Demo interaction layer
- `test_suites/` is the runnable test intent layer
- `tools/` is the operational helper layer

## Root Folder Guide

`core/`
- shared framework code used by tests and automation objects
- this is where the reusable kernel lives

`app/`
- app-specific automation code for Sauce Demo
- this is where pages, components, workflows, API clients, and domain helpers live

`test_suites/`
- all active pytest discovery now starts here
- this folder contains the real runnable suites and `conftest.py`

`tools/`
- operational helpers that support the framework but are not test cases themselves

`data/`
- raw JSON test data used by the data engine

`environments/`
- environment templates and env-style configuration files

`pipelines/`
- supporting pipeline notes and placeholders
- tool-native pipeline entrypoints still remain where the tools expect them: `.github/workflows/` and `Jenkinsfile`

`.github/workflows/`
- GitHub Actions pipeline definitions

`Jenkinsfile`
- Jenkins pipeline entrypoint for Pipeline from SCM

`pytest.ini`
- central pytest discovery, markers, and report output configuration

`ARCHITECTURE.md`
- short note explaining the `core/` naming decision

Legacy duplicate folders such as `src/`, `config/`, and `scripts/` were removed. The active implementation now runs from `core/`, `app/`, `test_suites/`, and `tools/`.

## Detailed Folder Responsibilities

`core/config/`
- `runtime_config.py` loads environment variables, exposes runtime settings, and acts as the main configuration object for the framework
- `environment_manager.py` provides the convenience wrapper around runtime config creation
- `secrets_resolver.py` is a lightweight helper for reading secret values from environment variables

`core/data_engine/`
- `data_provider_interface.py` defines the base data-provider contract
- `json_data_provider.py` contains the live JSON-backed providers used by fixtures and test flows
- `synthetic_data_factory.py` provides generated test payloads for future expansion
- `testdata_cache.py` is a simple cache utility for data reuse

`core/engine/`
- `browser_engine.py` holds a reusable Playwright launch abstraction
- `session_manager.py` centralizes browser-context and page creation helpers
- `execution_controller.py` converts high-level suite names such as `ui`, `api`, or `smoke` into pytest arguments
- `retry_orchestrator.py` is a generic retry helper for framework-level retry logic

`core/reporting/`
- `telemetry_client.py` provides the active framework logger
- `html_report_adapter.py` describes the pytest HTML report location
- `allure_adapter.py` describes the Allure results location
- `report_manager.py` centralizes report output metadata

`core/integrations/`
- `jira_gateway.py` is the Jira adapter
- `testrail_gateway.py` is the TestRail adapter
- `slack_notifier.py` is currently a lightweight notifier scaffold
- `ci_metadata_provider.py` collects CI environment metadata when available

Integration status:
- Jira and TestRail now fail soft when not configured, instead of trying to call placeholder endpoints with empty credentials
- Jira uses `JIRA_BASE_URL`, `JIRA_API_TOKEN`, and `JIRA_PROJECT_KEY`
- TestRail uses `TESTRAIL_BASE_URL`, `TESTRAIL_API_KEY`, and `TESTRAIL_RUN_ID`
- Slack is still only a scaffold logger right now; it is not yet wired to a real webhook call

`app/ui/pages/`
- page object models for the core screens: login, inventory, cart, and checkout
- tests and workflows use these classes instead of raw Playwright selectors in test bodies

`app/ui/components/`
- reusable UI fragments such as the cart widget, checkout form, filter and sort controls, header, and product cards
- components help avoid repeating small UI interaction logic across pages and tests

`app/ui/workflows/`
- business-flow orchestration layer
- `authentication_workflow.py` owns login-style flows
- `cart_workflow.py` owns cart-centric flows
- `purchase_workflow.py` owns checkout and purchase orchestration
- this layer is where multi-page business journeys belong

`app/api/clients/`
- low-level API interaction classes
- `base_api_client.py` owns shared HTTP behavior
- `sauce_demo_api_client.py` owns Sauce Demo endpoint-specific methods

`app/api/service_facades/`
- place for higher-level API orchestration helpers that sit above raw clients

`app/domain/`
- holds domain-level helpers such as models, validators, and transformers
- these are useful when the automation layer starts modeling business objects more explicitly

`test_suites/ui/`
- imperative UI tests
- good for direct validation without Gherkin overhead

`test_suites/api/`
- imperative API tests
- good for low-friction backend validation

`test_suites/bdd/features/ui/`
- UI feature files plus their feature-local glue modules

`test_suites/bdd/features/api/`
- API BDD feature files plus glue modules

`test_suites/bdd/step_definitions/`
- shared reusable BDD step definitions registered through `test_suites/conftest.py`

`test_suites/bdd/hooks/`
- place for future BDD-specific hook logic

`tools/mcp/`
- `mcp_client.py` owns the MCP execution and fallback behavior
- `mcp_stub_server.py` provides a local development stub for MCP connectivity testing

`tools/cli/run_tests.py`
- allows suite-style execution such as `all`, `ui`, `api`, `smoke`, and `regression`

## How The Framework Works

### 1. Startup Flow
- pytest reads `pytest.ini`
- pytest discovers tests from `test_suites/`
- `test_suites/conftest.py` loads shared plugins, fixtures, browser setup, data providers, and optional integrations
- `core/config/runtime_config.py` reads the environment and builds the active runtime configuration

### 2. UI Test Flow
- a test from `test_suites/ui/` requests fixtures such as `page`, `login_page`, `inventory_page`, or `cart_widget`
- `test_suites/conftest.py` creates the browser, context, and page objects
- page objects from `app/ui/pages/` perform stable UI interactions
- reusable UI pieces come from `app/ui/components/`
- broader business journeys can be moved into `app/ui/workflows/` to keep tests readable

### 3. BDD Flow
- Gherkin feature files live in `test_suites/bdd/features/`
- each feature has a local glue module that imports scenarios into pytest
- shared BDD steps live in `test_suites/bdd/step_definitions/`
- those shared step modules are registered through `pytest_plugins` in `test_suites/conftest.py`
- step definitions use page objects, components, workflows, fixtures, and providers just like imperative tests do

### 4. API Flow
- tests or BDD steps call `app/api/clients/`
- `base_api_client.py` provides session and request behavior
- `sauce_demo_api_client.py` exposes Sauce Demo specific endpoint methods
- optional higher-level coordination can live in `app/api/service_facades/`

### 5. MCP Flow
- MCP is opt-in through `--use-mcp` or `MCP_ENABLED=true`
- the `mcp_client` fixture in `test_suites/conftest.py` tries to connect to `MCP_SERVER_URL`
- if MCP is enabled and reachable, MCP-tagged flows can execute through the MCP path
- if MCP is enabled but unreachable, MCP-only scenarios skip instead of failing the full suite
- `tools/mcp/mcp_stub_server.py` can be used locally to simulate MCP connectivity

### 6. Failure and Reporting Flow
- pytest writes HTML, JUnit, and Allure raw outputs automatically through `pytest.ini`
- on failure, `test_suites/conftest.py` captures screenshots and optional traces
- the failure hook can hand metadata to Jira when the integration is configured
- logs go through `core/reporting/telemetry_client.py` into `reports/logs/`

### 7. CI Flow
- GitHub Actions uses `.github/workflows/playwright_ci.yml`
- Jenkins uses `Jenkinsfile`
- both pipelines execute pytest against `test_suites/` and archive the generated reports
- manual suite targeting is supported through suite names such as `ui`, `api`, `ui-bdd`, `api-bdd`, `smoke`, and `regression`

## Setup

1. Create and activate a virtual environment
2. Install dependencies from `requirements.txt`
3. Install Playwright Chromium
4. Copy `.env.example` to `.env`
5. Fill in any optional integration values you actually use
6. Install pre-commit hooks (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env
pre-commit install  # Optional: install pre-commit hooks
```

Example environment values:

```env
ENV=staging
BASE_URL=https://www.saucedemo.com
API_URL=
JIRA_BASE_URL=
JIRA_API_TOKEN=
JIRA_PROJECT_KEY=
TESTRAIL_BASE_URL=
TESTRAIL_API_KEY=
TESTRAIL_RUN_ID=
SLACK_WEBHOOK_URL=
MCP_ENABLED=false
MCP_SERVER_URL=ws://localhost:8080
DEFAULT_ACTION_TIMEOUT_MS=10000
DEFAULT_NAVIGATION_TIMEOUT_MS=30000
```

## Running Tests

Run the full suite:

```bash
python -m pytest
```

Run individual suite slices:

```bash
python -m pytest test_suites\ui -v
python -m pytest test_suites\api -v
python -m pytest test_suites\bdd\features\ui -v
python -m pytest test_suites\bdd\features\api -v
```

Run by marker:

```bash
python -m pytest -m smoke
python -m pytest -m regression
python -m pytest -m api
python -m pytest -m negative
python -m pytest -m edge
python -m pytest -m mcp
```

Helpful commands:

```bash
python -m pytest --collect-only -q
python -m pytest --headed -v
python -m pytest --debug-mode -v
python -m pytest -m mcp --use-mcp -v
python tools\cli\run_tests.py all
python tools\cli\run_tests.py ui
python tools\cli\run_tests.py smoke
```

MCP stub example:

```bash
venv\Scripts\python.exe tools\mcp\mcp_stub_server.py
python -m pytest test_suites\bdd\features\ui\test_end_to_end_purchase.py -k mcpassisted --use-mcp -v
```

## Reports

Pytest writes reports automatically:

- HTML report: `reports/report.html`
- JUnit XML: `reports/junit-report.xml`
- Allure raw results: `reports/allure-results/`
- logs: `reports/logs/`
- screenshots: `reports/screenshots/` on failure
- traces: `reports/traces/` when tracing is enabled

### Email Report (Optional)
You can email a summary plus attach a zip of the generated report artifacts (including `reports/logs/`) at the end of a pytest run.

Enable it in your `.env` (copy from `.env.example`) by setting:
- `EMAIL_ENABLED=true`
- `EMAIL_TO` (comma-separated recipients)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`

The email is sent automatically by the `pytest_sessionfinish` hook when `EMAIL_ENABLED=true`.

Generate the Allure HTML site if you have the Allure CLI installed:

```bash
allure generate reports\allure-results -o reports\allure-report --clean
```

## CI and CD

GitHub Actions:
- workflow file: `.github/workflows/qa-automation-ci.yml`
- runs smoke tests, regression tests, and staging E2E tests
- uploads test results as artifacts
- supports parallel execution with pytest-xdist

Jenkins:
- pipeline file: `Jenkinsfile`
- supports Windows and Linux agents
- publishes JUnit results and archives reports
- can publish pytest HTML and Allure data when the matching plugins are installed

## Environment Selection

The framework supports multiple environments through configuration files in the `environments/` folder:

```bash
# Run tests in development environment
pytest --env dev

# Run tests in staging environment
pytest --env staging

# Run tests in production environment
pytest --env prod
```

Environment files override base settings:
- `environments/base.env` — Shared defaults
- `environments/dev.env` — Development overrides
- `environments/staging.env` — Staging overrides
- `environments/prod.env` — Production overrides
- `.env` — Local overrides (not committed)

## MCP Mode (Local/Remote E2E)

The framework supports optional Model Context Protocol (MCP) integration for AI-assisted test execution:

### Local MCP Mode
```bash
# Start local MCP stub server
python tools/mcp/mcp_stub_server.py

# Run MCP-enabled tests
pytest --use-mcp -v
```

### Remote MCP Mode
```bash
# Configure remote MCP server
echo "MCP_SERVER_URL=ws://your-mcp-server:8080" >> .env
echo "MCP_ENABLED=true" >> .env

# Run tests with remote MCP
pytest --use-mcp -v
```

MCP features:
- AI-assisted element interactions
- Automatic fallback to POM when MCP unavailable
- Configurable via `MCP_ENABLED` and `MCP_SERVER_URL`
- Graceful degradation when MCP server is unreachable

## Report Organization

Test reports are organized by date and test case:

```
reports/
├── 2026-03-24/                    # Date-based folder
│   ├── test_login_standard_user/  # Test case folder
│   │   ├── screenshots/
│   │   │   └── test_login_standard_user_20260324_143015_123.png
│   │   └── videos/
│   │       └── test_login_standard_user_20260324_143015_123.webm
│   ├── test_add_to_cart/
│   │   ├── screenshots/
│   │   │   └── test_add_to_cart_20260324_143020_456.png
│   │   └── videos/
│   │       └── test_add_to_cart_20260324_143020_456.webm
│   └── ...
├── report.html                   # Pytest HTML report
├── junit-report.xml              # JUnit XML for CI
└── allure-results/               # Allure raw data
```

## Failure Triage Steps

When tests fail, follow this systematic approach:

### 1. Check HTML Report
```bash
# Open main report
start reports/report.html
```
- Shows test status, duration, and error messages
- Links to screenshots and videos

### 2. Review Screenshots
- Located in `reports/YYYY-MM-DD/test_name/screenshots/`
- Automatic capture on test failure
- Shows browser state at failure point

### 3. Review Videos
- Located in `reports/YYYY-MM-DD/test_name/videos/`
- Full test execution recording
- Helps understand user flow and timing issues

### 4. Check Allure Report (if available)
```bash
# Generate Allure HTML (requires Allure CLI)
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```
- Detailed test execution timeline
- Step-by-step breakdown
- Historical trends and comparisons

### 5. Debug Locally
```bash
# Run failed test with debugging
pytest --lf --headed -v -s

# Run with debug mode (slow motion + tracing)
pytest --debug-mode --headed -k "failed_test_name"
```

### 6. Common Failure Patterns
- **Selector issues**: Check page objects in `app/ui/pages/`
- **Timing issues**: Review wait strategies in components
- **Data issues**: Verify test data in `data/` folder
- **Environment issues**: Check `.env` configuration
- **MCP issues**: Ensure MCP server is running or disable MCP

## Pre-commit Setup

Install pre-commit hooks for code quality:

```bash
pip install pre-commit
pre-commit install
```

Run manually:
```bash
pre-commit run --all-files
```

Pre-commit checks include:
- **Black**: Code formatting
- **Flake8**: Style and error checking
- **MyPy**: Type checking
- **Trailing whitespace**: Cleanup
- **Large files**: Prevent accidental commits

## Known Caveats

- `core/integrations/slack_notifier.py` is still only a scaffold logger; it does not yet send a real webhook request
- Jira and TestRail adapters are integration-ready but still need real base URLs and credentials in `.env` or CI secrets
- `tools/mcp/mcp_client.py` still emits websocket deprecation warnings and should be cleaned up in a future pass

## Current Validation

Latest local checks after the cleanup:

- `venv\Scripts\python.exe -m compileall core app tools test_suites` succeeded
- `venv\Scripts\python.exe -m pytest --collect-only -q` collected 45 tests
- `venv\Scripts\python.exe -m pytest -q` resulted in 27 passed and 18 skipped
- the skipped tests are expected when `API_URL` is blank or MCP is not enabled

## Source of Truth

If documentation and code drift apart, trust these files first:

- `pytest.ini`
- `test_suites/conftest.py`
- `core/config/runtime_config.py`
- `.github/workflows/playwright_ci.yml`
- `Jenkinsfile`
