from abc import ABC, abstractmethod
from typing import Dict, List


class DataProvider(ABC):
    @abstractmethod
    def load_users(self) -> List[Dict[str, str]]:
        raise NotImplementedError
