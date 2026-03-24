import requests
from typing import Dict, Any, Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from core.config.runtime_config import EnvConfig
from core.reporting.telemetry_client import get_logger


class BaseAPIClient:
    """
    Base API client using requests with retry and timeout configuration.
    """

    def __init__(self, config: EnvConfig, base_url: Optional[str] = None) -> None:
        """
        Initialize the API client.

        Args:
            config: Environment configuration.
            base_url: Base URL for API calls. Falls back to config.api_url.
        """
        self.config = config
        self.base_url = base_url or config.api_url
        self.logger = get_logger(self.__class__.__name__)
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request with timeout.

        Args:
            method: HTTP method.
            endpoint: API endpoint.
            **kwargs: Additional request parameters.

        Returns:
            Response object.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        timeout = kwargs.pop('timeout', self.config.default_action_timeout_ms / 1000)  # Convert to seconds
        response = self.session.request(method, url, timeout=timeout, **kwargs)
        self.logger.info(f"{method} {url} - Status: {response.status_code}")
        return response

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """
        Perform GET request.

        Args:
            endpoint: API endpoint.
            params: Query parameters.
            **kwargs: Additional parameters.

        Returns:
            Response object.
        """
        response = self._make_request('GET', endpoint, params=params, **kwargs)
        return response

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """
        Perform POST request.

        Args:
            endpoint: API endpoint.
            data: Form data.
            json: JSON data.
            **kwargs: Additional parameters.

        Returns:
            Response object.
        """
        response = self._make_request('POST', endpoint, data=data, json=json, **kwargs)
        return response

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """
        Perform PUT request.

        Args:
            endpoint: API endpoint.
            data: Form data.
            json: JSON data.
            **kwargs: Additional parameters.

        Returns:
            Response object.
        """
        response = self._make_request('PUT', endpoint, data=data, json=json, **kwargs)
        return response

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Perform DELETE request.

        Args:
            endpoint: API endpoint.
            **kwargs: Additional parameters.

        Returns:
            Response object.
        """
        response = self._make_request('DELETE', endpoint, **kwargs)
        return response