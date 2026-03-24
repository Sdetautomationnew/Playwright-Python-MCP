import os
from typing import Dict, Iterable


class SecretsResolver:
    def get(self, key: str, default: str = '') -> str:
        return os.getenv(key, default)

    def as_dict(self, keys: Iterable[str]) -> Dict[str, str]:
        return {key: os.getenv(key, '') for key in keys}
