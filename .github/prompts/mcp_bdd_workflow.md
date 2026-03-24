# MCP-Driven BDD Page Object Model Creation Workflow

## Overview
This prompt template enables QA engineers to leverage the Playwright MCP browser tool to automatically generate Page Object Model (POM) locators and step implementations from Gherkin BDD scenarios.

---

## Template: BDD Step-to-POM Code Generator

### Instructions for QA Engineer

Copy and paste the following template into GitHub Copilot, customize the placeholders, and execute:

```
You are a Principal QA Automation Architect. Your mission is to generate production-ready Page Object Model code from BDD Gherkin scenarios.

**TASK:** Convert the following Gherkin step into Python Page Object Model code.

**STEP 1: Identify the Gherkin Scenario**
- Feature File: `tests/features/ui/<FEATURE_FILE_NAME>.feature`
- Specific Step: <PASTE_THE_GHERKIN_STEP_HERE>
- Page Target: Sauce Demo (https://www.saucedemo.com)

**STEP 2: Use Playwright MCP Tool**
1. Navigate to the Sauce Demo application
2. Perform the user action described in the Gherkin step
3. Inspect the DOM using Playwright MCP to identify:
   - The exact CSS selector or XPath for the element
   - Element type (button, input, link, dropdown, etc.)
   - Any dynamic attributes or data-testid values
   - Parent/sibling context if needed for uniqueness

**STEP 3: Document Your Findings**
Provide:
- Element locator (CSS selector or XPath)
- Alternative locators (if applicable)
- Element description (what it does, its role)
- Accessibility attributes (aria-label, role, etc.)

**STEP 4: Generate Python Page Object Model Code**
Create or update the appropriate file in `src/pages/` following this structure:

```python
from page_base import BasePage

class <PageClassName>(BasePage):
    """
    Page Object Model for <Page Description>
    """
    
    # Locators
    <ELEMENT_NAME>_LOCATOR = "<SELECTOR_OR_XPATH>"
    
    def <interaction_method>(self):
        """<Method description>"""
        self.page.locator(self.<ELEMENT_NAME>_LOCATOR).click()
        # OR: self.page.locator(self.<ELEMENT_NAME>_LOCATOR).fill("<input_value>")
        # OR: self.page.locator(self.<ELEMENT_NAME>_LOCATOR).get_text()
```

**STEP 5: Generate the BDD Step Implementation**
Create or update the corresponding file in `steps/` following this structure:

```python
from behave import given, when, then
from src.pages.<page_module> import <PageClassName>

@when('user <action_verb> <element_description>')
def step_user_action(context, action_verb, element_description):
    """
    Implementation: <Full step description>
    """
    page = <PageClassName>(context.page)
    page.<interaction_method>()
    # Add assertions as needed
```

---

## Constraints & Best Practices

1. **Locator Priority:**
   - Prefer `data-testid` attributes
   - Then CSS selectors (most robust)
   - Then XPath (least preferred, but acceptable for complex elements)
   - Avoid index-based selectors (e.g., `nth-child()`)

2. **Naming Conventions:**
   - Page classes: `PascalCase` (e.g., `LoginPage`, `CheckoutPage`)
   - Locators: `snake_case` with `_LOCATOR` suffix
   - Methods: `snake_case` with verb prefix (e.g., `click_`, `fill_`, `verify_`)

3. **Reusability:**
   - Extract common actions into base page methods
   - Use parameterized methods when multiple similar interactions exist

4. **Documentation:**
   - Include docstrings for all methods
   - Explain complex locators or workarounds

---

## Example Execution

**Gherkin Step:**
```gherkin
When user clicks on the Add to Cart button for the "Sauce Labs Backpack" product
```

**Prompt Customization:**
```
You are a Principal QA Automation Architect...

STEP 1: Identify the Gherkin Scenario
- Feature File: tests/features/ui/inventory_and_sorting.feature
- Specific Step: When user clicks on the Add to Cart button for the "Sauce Labs Backpack" product
- Page Target: Sauce Demo (https://www.saucedemo.com)

STEP 2: Use Playwright MCP Tool
[Navigate to Sauce Demo, find the Backpack product, inspect the Add to Cart button]

...continue with remaining steps
```

---

## Workflow Summary

1. **Paste template** into Copilot
2. **Customize placeholders** with your specific feature file and step
3. **Let Copilot use Playwright MCP** to inspect the page
4. **Review generated code** for accuracy and best practices
5. **Copy-paste results** into your codebase:
   - Page Object: `src/pages/<page_name>.py`
   - Step Implementation: `steps/<step_type>_steps.py`
6. **Verify integration** by running the BDD tests

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Locator returns multiple elements | Refine selector with parent class or data attributes |
| Dynamic locator (changes per test run) | Use partial matching or attribute-based selectors |
| Element not found in DOM initially | Add explicit wait in BasePage method |
| Gherkin step too vague | Break into smaller, more specific steps |

---

## Related Resources

- **Page Object Model Base:** `src/pages/base_page.py`
- **Existing Pages:** `src/pages/` directory
- **Step Implementations:** `steps/` directory
- **Feature Files:** `tests/features/ui/` directory
- **Browser Configuration:** `config/env_config.py`
