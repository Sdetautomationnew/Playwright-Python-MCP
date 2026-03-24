class TestDataCache:
    def __init__(self):
        self._cache = {}

    def get(self, key, default=None):
        return self._cache.get(key, default)

    def set(self, key, value):
        self._cache[key] = value
