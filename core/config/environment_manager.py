from core.config.runtime_config import EnvConfig, RuntimeConfig, get_env_config

def get_runtime_config(env_override=None):
    return get_env_config(env_override)

__all__ = ['EnvConfig', 'RuntimeConfig', 'get_env_config', 'get_runtime_config']
