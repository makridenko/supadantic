from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Dict, Iterable, List


class SingletoneMeta(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        key = (args, frozenset(kwargs.items()), cls)
        if key not in cls._instances:
            cls._instances[key] = super(SingletoneMeta, cls).__call__(*args, **kwargs)
        return cls._instances[key]


class BaseClient(ABC, metaclass=SingletoneMeta):
    """Base client for all clients"""

    def __init__(self, table_name: str) -> None:
        self.table_name = table_name

    @abstractmethod
    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update(self, *, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def select(self, *, eq: Dict[str, Any] | None = None, neq: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, *, id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def bulk_update(self, *, ids: Iterable[int], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def bulk_delete(self, *, ids: Iterable[int]) -> List[Dict[str, Any]]:
        raise NotImplementedError
