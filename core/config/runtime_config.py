import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import dotenv_values

_ORIGINAL_ENV = dict(os.environ)


class EnvConfig:
	_loaded_keys: set[str] = set()

	def __init__(self, env_override: Optional[str] = None):
		self.project_root = Path(__file__).resolve().parents[2]
		self.environments_dir = self.project_root / 'environments'
		self.root_env_file = self.project_root / '.env'
		self.root_local_env_file = self.project_root / '.env.local'
		self._env_override = self._normalize_env_name(env_override)
		self._root_env_values = self._read_env_file(self.root_env_file)
		self._current_env = self._resolve_env_name()
		self._loaded_files = self._resolve_env_files()
		self._values = self._load_values()
		self._apply_to_process_environment()

	@staticmethod
	def _normalize_env_name(value):
		return (value or '').strip().lower()

	def _read_env_file(self, path: Path):
		if not path.exists():
			return {}
		values = dotenv_values(path)
		return {key: value for key, value in values.items() if value is not None}

	def _available_env_names(self):
		if not self.environments_dir.exists():
			return []
		return sorted(
			path.stem.lower()
			for path in self.environments_dir.glob('*.env')
			if path.stem.lower() != 'base'
		)

	def _resolve_env_name(self):
		for candidate in (
			self._env_override,
			self._normalize_env_name(_ORIGINAL_ENV.get('ENV')),
			self._normalize_env_name(self._root_env_values.get('ENV')),
			'staging',
		):
			if candidate:
				return candidate
		return 'staging'

	def _resolve_env_files(self):
		env_file = self.environments_dir / f'{self._current_env}.env'
		if not env_file.exists():
			available_envs = ', '.join(self._available_env_names()) or 'none'
			raise ValueError(
				f'Unknown environment "{self._current_env}". Expected one of: {available_envs}.'
			)

		return [
			self.environments_dir / 'base.env',
			self.root_env_file,
			env_file,
			self.root_local_env_file,
			self.project_root / f'.env.{self._current_env}.local',
		]

	def _load_values(self):
		merged: Dict[str, str] = {}
		for path in self._loaded_files:
			merged.update(self._read_env_file(path))

		merged.update({key: value for key, value in _ORIGINAL_ENV.items() if value is not None})
		merged['ENV'] = self._current_env
		return merged

	def _apply_to_process_environment(self):
		for key in self.__class__._loaded_keys:
			if key not in _ORIGINAL_ENV:
				os.environ.pop(key, None)

		for key, value in self._values.items():
			os.environ[key] = value

		self.__class__._loaded_keys = set(self._values)

	def _get(self, key: str, default: str = ''):
		return self._values.get(key, default)

	@property
	def current_env(self):
		return self._current_env

	@property
	def loaded_env_files(self):
		return [str(path) for path in self._loaded_files if path.exists()]

	@property
	def base_url(self):
		return self._get('BASE_URL', 'https://www.saucedemo.com')

	@property
	def api_url(self):
		return self._get('API_URL', '')

	@property
	def mcp_server_url(self):
		return self._get('MCP_SERVER_URL', 'ws://localhost:8080')

	@property
	def mcp_enabled(self):
		return self._get('MCP_ENABLED', 'false').lower() == 'true'

	@property
	def default_action_timeout_ms(self):
		return int(self._get('DEFAULT_ACTION_TIMEOUT_MS', '10000'))

	@property
	def default_navigation_timeout_ms(self):
		return int(self._get('DEFAULT_NAVIGATION_TIMEOUT_MS', '30000'))

	@property
	def custom_viewport_width(self):
		return int(self._get('CUSTOM_VIEWPORT_WIDTH', '390'))

	@property
	def custom_viewport_height(self):
		return int(self._get('CUSTOM_VIEWPORT_HEIGHT', '844'))

	@property
	def custom_device_scale_factor(self):
		return float(self._get('CUSTOM_DEVICE_SCALE_FACTOR', '3'))

	@property
	def credentials(self):
		return {
			'jira_api_token': self._get('JIRA_API_TOKEN', ''),
			'jira_project_key': self._get('JIRA_PROJECT_KEY', ''),
			'testrail_api_key': self._get('TESTRAIL_API_KEY', ''),
			'testrail_run_id': self._get('TESTRAIL_RUN_ID', ''),
		}

	def get_env_var(self, key: str, default: str = ''):
		return self._get(key, default)


def get_env_config(env_override: Optional[str] = None):
	return EnvConfig(env_override)


RuntimeConfig = EnvConfig

__all__ = ['EnvConfig', 'RuntimeConfig', 'get_env_config']
