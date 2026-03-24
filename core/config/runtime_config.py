import os
from typing import Dict, Optional

from dotenv import load_dotenv


class EnvConfig:
    _instance: Optional['EnvConfig'] = None
    _env_override: Optional[str] = None

    def __new__(cls, env_override: Optional[str] = None) -> 'EnvConfig':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, env_override: Optional[str] = None) -> None:
        if self._initialized:
            return
        self._env_override = env_override
        load_dotenv()
        self._initialized = True

    @property
    def current_env(self) -> str:
        return self._env_override or os.getenv('ENV', 'staging')

    @property
    def base_url(self) -> str:
        return os.getenv('BASE_URL', 'https://www.saucedemo.com')

    @property
    def api_url(self) -> str:
        return os.getenv('API_URL', '')

    @property
    def mcp_server_url(self) -> str:
        return os.getenv('MCP_SERVER_URL', 'ws://localhost:8080')

    @property
    def mcp_enabled(self) -> bool:
        return os.getenv('MCP_ENABLED', 'false').lower() == 'true'

    @property
    def default_action_timeout_ms(self) -> int:
        return int(os.getenv('DEFAULT_ACTION_TIMEOUT_MS', '10000'))

    @property
    def default_navigation_timeout_ms(self) -> int:
        return int(os.getenv('DEFAULT_NAVIGATION_TIMEOUT_MS', '30000'))

    @property
    def custom_viewport_width(self) -> int:
        return int(os.getenv('CUSTOM_VIEWPORT_WIDTH', '390'))

    @property
    def custom_viewport_height(self) -> int:
        return int(os.getenv('CUSTOM_VIEWPORT_HEIGHT', '844'))

    @property
    def custom_device_scale_factor(self) -> float:
        return float(os.getenv('CUSTOM_DEVICE_SCALE_FACTOR', '3'))

    @property
    def credentials(self) -> Dict[str, str]:
        return {
            'jira_api_token': os.getenv('JIRA_API_TOKEN', ''),
            'jira_project_key': os.getenv('JIRA_PROJECT_KEY', ''),
            'testrail_api_key': os.getenv('TESTRAIL_API_KEY', ''),
            'testrail_run_id': os.getenv('TESTRAIL_RUN_ID', ''),
        }

    def get_env_var(self, key: str, default: str = '') -> str:
        return os.getenv(key, default)


def get_env_config(env_override: Optional[str] = None) -> EnvConfig:
    return EnvConfig(env_override)


RuntimeConfig = EnvConfig

__all__ = ['EnvConfig', 'RuntimeConfig', 'get_env_config']
