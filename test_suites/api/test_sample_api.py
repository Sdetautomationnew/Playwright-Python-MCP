import pytest
from app.api.clients.base_api_client import BaseAPIClient


class TestSampleAPI:
    """Placeholder test class for API tests."""

    @pytest.mark.api
    def test_sample_api_call(self, env_config) -> None:
        """Sample API test."""
        # This is a placeholder - in real scenario, create a specific API client
        client = BaseAPIClient(env_config, base_url="https://jsonplaceholder.typicode.com")
        response = client.get("/posts/1")
        payload = response.json()
        assert payload["id"] == 1