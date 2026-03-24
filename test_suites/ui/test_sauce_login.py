import pytest
from typing import Dict
from core.data_engine.json_data_provider import JsonUserProvider


class TestSauceLogin:
    """Test class for Sauce Demo login functionality."""

    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.parametrize("user", JsonUserProvider().load_users(), ids=lambda u: u['username'])
    def test_login_scenarios(self, login_page, user: Dict[str, str]) -> None:
        """Test various login scenarios based on user data."""
        # Navigate to login page
        login_page.navigate_to(login_page.config.base_url)

        # Perform login
        login_page.login(user['username'], user['password'])

        # Assert based on expected status
        if user['expected_status'] == 'success':
            assert login_page.is_login_successful(), f"Login should succeed for {user['username']}"
        elif user['expected_status'] == 'locked':
            error_msg = login_page.get_error_message()
            assert user['expected_message'] in error_msg, f"Expected error message for locked user: {user['expected_message']}"
        elif user['expected_status'] == 'error':
            error_msg = login_page.get_error_message()
            assert user['expected_message'] in error_msg, f"Expected error message for invalid user: {user['expected_message']}"