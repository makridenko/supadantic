from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Dict, Iterable, List


class SingletoneMeta(ABCMeta):
    """Metaclass for the singletone pattern."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Return the instance if it exists, otherwise create a new one.
        Instances are stored in a dictionary with the key being a tuple of the arguments and the class.
        In other words, it's possible to have only one instance with specific table name and child class.
        """

        key = (args, frozenset(kwargs.items()), cls)
        if key not in cls._instances:
            cls._instances[key] = super(SingletoneMeta, cls).__call__(*args, **kwargs)
        return cls._instances[key]


class BaseClient(ABC, metaclass=SingletoneMeta):
    """Base client for all clients."""

    def __init__(self, table_name: str) -> None:
        """Initialize the client with the table name."""
        self.table_name = table_name

    @abstractmethod
    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a new record into the table.

        Args:
            data (Dict[str, Any]): The data to insert.

        Returns:
            (Dict[str, Any]): The inserted record.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, *, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a record in the table.

        Args:
            id (int): The ID of the record to update.
            data (Dict[str, Any]): The data to update.

        Returns:
            (Dict[str, Any]): The updated record.
        """
        raise NotImplementedError

    @abstractmethod
    def select(self, *, eq: Dict[str, Any] | None = None, neq: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        """
        Select records from the table.

        Args:
            eq (Dict[str, Any] | None): The equality filter.
            neq (Dict[str, Any] | None): The non-equality filter.

        Returns:
            (List[Dict[str, Any]]): The selected records.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, *, id: int) -> None:
        """
        Delete a record from the table.

        Args:
            id (int): The ID of the record to delete.
        """
        raise NotImplementedError

    @abstractmethod
    def bulk_update(self, *, ids: Iterable[int], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Bulk update records in the table.

        Args:
            ids (Iterable[int]): The IDs of the records to update.
            data (Dict[str, Any]): The data to update.

        Returns:
            (List[Dict[str, Any]]): List of updated records.
        """
        raise NotImplementedError

    @abstractmethod
    def bulk_delete(self, *, ids: Iterable[int]) -> List[Dict[str, Any]]:
        """
        Bulk delete records from the table.

        Args:
            ids (Iterable[int]): The IDs of the records to delete.

        Returns:
            (List[Dict[str, Any]]): List of deleted records.
        """
        raise NotImplementedError
