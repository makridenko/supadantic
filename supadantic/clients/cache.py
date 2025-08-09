from copy import copy
from typing import TYPE_CHECKING, Any

from supadantic.clients.base import BaseClient, BaseClientMeta


if TYPE_CHECKING:
    from collections.abc import Iterable

    from supadantic.query_builder import QueryBuilder


class SingletoneMeta(BaseClientMeta):
    """
    Metaclass implementing the Singleton pattern.

    This metaclass ensures that only one instance of a class (and its subclasses)
    exists for a given set of initialization arguments (table_name and class).
    It utilizes a dictionary to store instances, keyed by a tuple of the initialization arguments,
    frozen set of keyword arguments and the class itself.

    In other words, it's possible to have only one instance with specific table name and child class.
    """

    _instances: dict[tuple[tuple, frozenset, type], Any] = {}

    def __call__(cls, *args, **kwargs):
        """
        Returns the existing instance if it exists; otherwise, creates and returns a new one.

        This method intercepts the class instantiation process (`cls(...)`) and checks
        if an instance with the given initialization arguments already exists. If so,
        it returns the existing instance. Otherwise, it creates a new instance using
        the `super()` call and stores it in the `_instances` dictionary.
        """

        key = (args, frozenset(kwargs.items()), cls)
        if key not in cls._instances:
            cls._instances[key] = super().__call__(*args, **kwargs)
        return cls._instances[key]


class CacheClient(BaseClient, metaclass=SingletoneMeta):
    """
    Client for caching data in memory, using the Singleton pattern.

    This client stores data in a simple in-memory dictionary (`_cache_data`).
    It implements the `BaseClient` interface for common database operations,
    simulating database interactions by operating on the in-memory cache.

    This class is designed for testing.
    It is NOT suitable for production environments.
    """

    def __init__(self, table_name: str, schema: str | None = None) -> None:
        """
        Initializes the client with the table name and an empty cache.

        Args:
            table_name (str): The name of the table associated with the cache.
                         While the table name isn't directly used for in-memory
                         operations, it's stored for consistency with the
                         `BaseClient` interface and may be used in future
                         extensions of this class.
            schema (str | None, optional): Name of the database schema containing
                 the target table. Included for interface compatibility with BaseClient.
        """
        super().__init__(table_name=table_name, schema=schema)

        self._cache_data: dict[int, dict[str, Any]] = {}

    def _delete(self, *, query_builder: 'QueryBuilder') -> list[dict[str, Any]]:
        """
        Deletes records from the cache that match the query builder's filter criteria.

        This method first filters the cache to identify records that match the
        deletion criteria. Then, it removes those records from the cache.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance specifying the deletion criteria.

        Returns:
            (list[dict[str, Any]]): A list of the deleted records. The records are returned *before* they are
            deleted from the cache. This allows for auditing or other post-deletion
            operations.
        """

        filtered_data = self._filter(query_builder=query_builder)
        ids = [data['id'] for data in filtered_data]

        deleted_records = []
        for id_ in ids:
            deleted_records.append(self._cache_data.pop(id_))

        return self._get_return_data(objects=deleted_records)

    def _insert(self, *, query_builder: 'QueryBuilder') -> list[dict[str, Any]]:
        """
        Inserts a new record into the cache.

        A new ID is generated for the record (incrementing from the highest existing ID).
        The data to insert is taken from the `query_builder.insert_data` attribute.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance containing the data to insert.
                           The data is expected to be in the `insert_data` attribute
                           of the QueryBuilder.

        Returns:
            (list[dict[str, Any]]): A list containing the newly inserted record.  The record will have an 'id'
            field automatically assigned.
        """

        ids = list(self._cache_data.keys())
        if ids:
            id_ = ids[-1] + 1
        else:
            id_ = 1

        insert_data = query_builder.insert_data if query_builder.insert_data else {}
        self._cache_data[id_] = {'id': id_, **insert_data}
        return [self._convert_obj(obj=self._cache_data[id_])]

    def _update(self, *, query_builder: 'QueryBuilder') -> list[dict[str, Any]]:
        """
        Updates records in the cache that match the query builder's filter criteria.

        This method filters the cache to identify records to update and then
        applies the update data from `query_builder.update_data` to those records.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance containing the update criteria
                           and the data to update. The data is expected to be in
                           the `update_data` attribute of the QueryBuilder.

        Returns:
            A list of the updated records. The list contains *copies* of the records
            *after* the update is applied.
        """

        filtered_data = self._filter(query_builder=query_builder)

        updated_records = []
        ids = [data['id'] for data in filtered_data]
        for id_ in ids:
            update_data = query_builder.update_data if query_builder.update_data else {}
            self._cache_data[id_].update(update_data)
            updated_records.append(self._cache_data[id_])

        return self._get_return_data(objects=updated_records)

    def _filter(self, *, query_builder: 'QueryBuilder') -> list[dict[str, Any]]:
        """
        Filters records in the cache based on equality and non-equality filters specified
        in the QueryBuilder.

        This method supports filtering based on equality and non-equality. The filters
        are applied as a chain of AND conditions. It provides a basic example of
        filtering logic and can be extended with other filtering conditions as needed.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance containing the filter criteria.
                           The filter criteria are expected to be in the `equal` and
                           `not_equal` attributes of the QueryBuilder. These attributes
                           are expected to be dictionaries mapping field names to values.

        Returns:
            (list[dict[str, Any]]): A list of records that match the filter criteria.  The records in the
            list are converted to return data using the `_get_return_data` method.
        """
        equal_filters: dict[str, Any] = dict(pair for pair in query_builder.equal)
        not_equal_filters: dict[str, Any] = dict(pair for pair in query_builder.not_equal)
        less_than_or_equal_filters: dict[str, Any] = dict(pair for pair in query_builder.less_than_or_equal)
        greater_than_filters: dict[str, Any] = dict(pair for pair in query_builder.greater_than)
        less_than_filters: dict[str, Any] = dict(pair for pair in query_builder.less_than)
        greater_than_or_equal_filters: dict[str, Any] = dict(pair for pair in query_builder.greater_than_or_equal)
        included_filters: dict[str, Any] = dict(pair for pair in query_builder.included)

        def _lambda_filter(obj: dict[str, Any]) -> bool:  # noqa: WPS430
            """Filter the records based on the equality and non-equality filters."""
            return all(
                (
                    all(obj[key] != value for key, value in not_equal_filters.items()),  # noqa: WPS204
                    all(obj[key] == value for key, value in equal_filters.items()),
                    all(obj[key] <= value for key, value in less_than_or_equal_filters.items()),
                    all(obj[key] > value for key, value in greater_than_filters.items()),
                    all(obj[key] < value for key, value in less_than_filters.items()),
                    all(obj[key] >= value for key, value in greater_than_or_equal_filters.items()),
                    all(obj[key] in value for key, value in included_filters.items()),
                )
            )

        result = filter(_lambda_filter, self._cache_data.values())
        return self._get_return_data(objects=result, order_by=query_builder.order_by_field)

    def _count(self, *, query_builder: 'QueryBuilder') -> int:
        """
        Counts the number of records in the cache that match the query builder's
        filter criteria.

        This method uses the `_filter` method to identify records that match the
        filter criteria and then returns the number of those records.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance specifying the filter criteria.

        Returns:
            (int): The number of records matching the filter criteria.
        """

        return len(self._filter(query_builder=query_builder))

    def _convert_obj(self, *, obj: dict[str, Any]) -> dict[str, Any]:
        """
        Converts a record's data to a format suitable for returning to the client.

        This method simulates the behavior of Supabase, which returns iterables as strings.
        It converts any list or tuple values in the record to strings. This conversion
        is performed to maintain consistency with the Supabase API.

        Args:
            obj (dict[str, Any]): The record data.

        Returns:
            (dict[str, Any]): A copy of the record data with iterables converted to strings. The
            original record data is not modified.
        """

        result_data = copy(obj)

        for key, value in obj.items():
            if type(value) in (list, tuple):  # noqa: WPS516
                result_data.update({key: str(value)})

        return result_data

    def _get_return_data(
        self, *, objects: 'Iterable[dict[str, Any]]', order_by: tuple[str, bool] | None = None
    ) -> list[dict[str, Any]]:
        """
        Applies the `_convert_obj` method to each record in an iterable and returns the result as a list.

        This method is used to format the results of database operations before
        returning them to the client.

        Args:
            objects (Iterable[dict[str, Any]]): An iterable of records to convert.
            order_by (tuple[str, bool] | None): A tuple containing the field name to sort by and
                                            a boolean indicating descending (True) or ascending (False) order.
                                            If None, no sorting is applied.

        Returns:
            (list[dict[str, Any]]): A list of records, where each record has been converted to return data
                                using the `_convert_obj` method. Records will be sorted if order_by is provided.
        """

        result = [self._convert_obj(obj=obj) for obj in objects]
        if order_by:
            column, desc = order_by
            result = sorted(result, key=lambda item: item[column], reverse=desc)
        return result
