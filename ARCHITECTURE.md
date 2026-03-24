# Architecture

The repo now uses these primary packages:

- `core/` for config, engine, reporting, integrations, and data services
- `app/` for UI, API, workflows, and domain-level automation code
- `test_suites/` for UI, API, and BDD test intent
- `tools/` for MCP and CLI utilities
- `environments/` for environment templates
- `pipelines/` for CI/CD pipeline notes/templates

Important note:

- the original idea used a top-level `platform/` package, but in Python that collides with the standard library `platform` module
- to keep the repo executable, the implementation uses `core/` instead

Naming note:

- the reusable kernel was originally called `framework/`, but `core/` is shorter and clearer in imports
- the Sauce Demo interaction layer was originally called `automation/`, but `app/` better signals that this package holds product-facing UI and API code
