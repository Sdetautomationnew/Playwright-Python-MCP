import json
from pathlib import Path
from typing import Any, Dict, List

from core.data_engine.data_provider_interface import DataProvider


class JsonUserProvider(DataProvider):
    def __init__(self, file_path: str = 'data/users/sauce_users.json') -> None:
        self.file_path = Path(file_path)

    def load_users(self) -> List[Dict[str, str]]:
        if not self.file_path.exists():
            raise FileNotFoundError(f'User data file not found: {self.file_path}')
        with self.file_path.open('r', encoding='utf-8') as stream:
            return json.load(stream)


class JsonCheckoutProvider(DataProvider):
    def __init__(self, file_path: str = 'data/checkout/checkout_info.json') -> None:
        self.file_path = Path(file_path)

    def load_users(self) -> List[Dict[str, str]]:
        return self.load_checkout_info()

    def load_checkout_info(self) -> List[Dict[str, Any]]:
        if not self.file_path.exists():
            raise FileNotFoundError(f'Checkout data file not found: {self.file_path}')
        with self.file_path.open('r', encoding='utf-8') as stream:
            return json.load(stream)


class JsonProductProvider(DataProvider):
    def __init__(self, file_path: str = 'data/products/products.json') -> None:
        self.file_path = Path(file_path)

    def load_users(self) -> List[Dict[str, str]]:
        return self.load_products()

    def load_products(self) -> List[Dict[str, Any]]:
        if not self.file_path.exists():
            raise FileNotFoundError(f'Product data file not found: {self.file_path}')
        with self.file_path.open('r', encoding='utf-8') as stream:
            return json.load(stream)


class JsonDataProvider:
    def __init__(self) -> None:
        self.users = JsonUserProvider()
        self.checkout = JsonCheckoutProvider()
        self.products = JsonProductProvider()


__all__ = ['JsonUserProvider', 'JsonCheckoutProvider', 'JsonProductProvider', 'JsonDataProvider']
