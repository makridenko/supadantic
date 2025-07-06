from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Callable

from supadantic.query_builder import QueryBuilder


class BaseClientMeta(ABCMeta):
    """
    Metaclass for BaseClient.  Currently a placeholder but can be used for future
    metaclass-level customizations for all BaseClient subclasses.  This allows for
    modifying class creation behavior (e.g., registering subclasses, enforcing
    specific attributes).
    """

    pass


class BaseClient(ABC, metaclass=BaseClientMeta):
    """
    Abstract base class for all client implementations.

    This class defines the interface that all concrete client classes must implement.
    It provides a common `execute` method for dispatching queries based on the
    `QueryBuilder`'s mode and defines abstract methods for the core database
    operations.

    Subclasses must implement the abstract methods to provide concrete implementations
    for interacting with a specific database or service.
    """

    def __init__(self, table_name: str, schema: str | None = None) -> None:
        """
        Initializes the client with the table name.

        The table name is used to identify the target table for database operations.

        Args:
            table_name (str): The name of the table to operate on.
        """

        self.table_name = table_name
        self.schema = schema

    def execute(self, *, query_builder: QueryBuilder) -> list[dict[str, Any]] | int:
        """
        Executes a query constructed by the provided QueryBuilder.

        This method acts as a dispatcher, selecting the appropriate database operation
        based on the `query_builder.mode`.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance containing the query details
                           and execution mode.  The mode determines which underlying
                           database operation will be performed.

        Returns:
            (dict[str, Any] | int): A dictionary containing the results of the query for insert,
                                    update, or filter operations; or an integer representing the number
                                    of affected rows for delete or count operations. The exact structure
                                    of the dictionary depends on the specific data returned by the underlying database.
        """

        map_modes: dict[QueryBuilder.Mode, Callable] = {
            QueryBuilder.Mode.DELETE_MODE: self._delete,
            QueryBuilder.Mode.INSERT_MODE: self._insert,
            QueryBuilder.Mode.UPDATE_MODE: self._update,
            QueryBuilder.Mode.FILTER_MODE: self._filter,
            QueryBuilder.Mode.COUNT_MODE: self._count,
        }

        return map_modes[query_builder.mode](query_builder=query_builder)

    @abstractmethod
    def _delete(self, *, query_builder: QueryBuilder) -> list[dict[str, Any]]:
        """
        Abstract method to delete records from the database.

        Subclasses must implement this method to provide the concrete logic for deleting
        records based on the criteria specified in the QueryBuilder.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance containing the delete criteria.

        Returns:
            (int): The number of records deleted.
        """

        raise NotImplementedError

    @abstractmethod
    def _insert(self, *, query_builder: QueryBuilder) -> list[dict[str, Any]]:
        """
        Abstract method to insert records into the database.

        Subclasses must implement this method to provide the concrete logic for inserting
        records based on the data specified in the QueryBuilder.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance containing the data to insert.

        Returns:
            (list[dict[str, Any]]): A list representing the inserted record(s).
        """

        raise NotImplementedError

    @abstractmethod
    def _update(self, *, query_builder: QueryBuilder) -> list[dict[str, Any]]:
        """
        Abstract method to update records in the database.

        Subclasses must implement this method to provide the concrete logic for updating
        records based on the criteria and data specified in the QueryBuilder.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance containing the update criteria and data.

        Returns:
            (int): The number of records updated.
        """

        raise NotImplementedError

    @abstractmethod
    def _filter(self, *, query_builder: QueryBuilder) -> list[dict[str, Any]]:
        """
        Abstract method to filter records from the database.

        Subclasses must implement this method to provide the concrete logic for filtering
        records based on the criteria specified in the QueryBuilder.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance containing the filter criteria.

        Returns:
            (dict[str, Any]): A list containing the filtered records. The exact structure depends
            on the underlying database and the query executed. Could be a list of records,
            a single record, or a success/failure indicator.
        """

        raise NotImplementedError

    @abstractmethod
    def _count(self, *, query_builder: QueryBuilder) -> int:
        """
        Count method.

        Args:
            query_builder (QueryBuilder): The query builder instance.

        Returns:
            (int): Number of selected records.
        """
        raise NotImplementedError
