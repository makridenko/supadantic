from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List


class BaseClient(ABC):
    def __init__(self, table_name: str) -> None:
        pass

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
