import os
from typing import TYPE_CHECKING, Any, Literal

from supabase.client import create_client

from .base import BaseClient


if TYPE_CHECKING:
    from postgrest._sync.request_builder import SyncSelectRequestBuilder
    from postgrest.base_request_builder import BaseFilterRequestBuilder

    from supadantic.query_builder import QueryBuilder


class SupabaseClient(BaseClient):
    """
    Client for interacting with a Supabase database.

    This client provides methods for performing common database operations
    using the Supabase client library.
    It inherits from `BaseClient` and implements the abstract methods defined there.

    This client relies on environment variables `SUPABASE_URL` and `SUPABASE_KEY`
    to initialize the Supabase client.
    """

    def __init__(self, table_name: str):
        """
        Initializes the Supabase client and sets up the query object.

        Args:
            table_name (str): The name of the table to interact with.
        """

        super().__init__(table_name=table_name)
        url: str = os.getenv('SUPABASE_URL', default='')
        key: str = os.getenv('SUPABASE_KEY', default='')
        supabase_client = create_client(url, key)
        self.query = supabase_client.table(table_name=self.table_name)

    def _delete(self, *, query_builder: 'QueryBuilder') -> list[dict[str, Any]]:
        """
        Deletes records from the Supabase table based on the filter criteria in the query builder.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance specifying the deletion criteria.

        Returns:
            (list[dict[str, Any]]): A list of dictionaries representing the deleted records.
        """

        self.query = self.query.delete()
        self.query = self._add_filters(query_builder=query_builder)
        response = self.query.execute()
        return response.data

    def _insert(self, *, query_builder: 'QueryBuilder') -> list[dict[str, Any]]:
        """
        Inserts a new record into the Supabase table.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance containing the data to insert.
                           The data is expected to be in the `insert_data` attribute of the QueryBuilder.

        Returns:
            (list[dict[str, Any]]): A list of dictionaries representing the inserted records.
        """

        self.query = self.query.insert(query_builder.insert_data)
        response = self.query.execute()
        return response.data

    def _update(self, *, query_builder: 'QueryBuilder') -> list[dict[str, Any]]:
        """
        Updates records in the Supabase table based on the filter criteria in the query builder.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance containing the update criteria
                                          and the data to update. The data is expected to be in the
                                          `update_data` attribute of the QueryBuilder.

        Returns:
            (list[dict[str, Any]]): A list of dictionaries representing the updated records.
        """

        self.query = self.query.update(query_builder.update_data)
        self.query = self._add_filters(query_builder=query_builder)
        response = self.query.execute()
        return response.data

    def _filter(self, *, query_builder: 'QueryBuilder') -> list[dict[str, Any]]:
        """
        Filters records from the Supabase table based on the filter criteria in the query builder.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance specifying the filter criteria.

        Returns:
            (list[dict[str, Any]]): A list of dictionaries representing the filtered records.
        """

        self.query = self._select(query_builder=query_builder)
        self.query = self._add_filters(query_builder=query_builder)
        response = self.query.execute()
        return response.data

    def _count(self, *, query_builder: 'QueryBuilder') -> int:
        """
        Counts the number of records in the Supabase table that match the filter criteria in the query builder.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance specifying the filter criteria.

        Returns:
            (int): The number of records matching the filter criteria.
        """

        self.query = self._select(query_builder=query_builder, count='exact')
        self.query = self._add_filters(query_builder=query_builder)
        response = self.query.execute()
        return response.count

    def _select(
        self, *, query_builder: 'QueryBuilder', count: Literal['exact'] | None = None
    ) -> 'SyncSelectRequestBuilder':
        """
        Builds the select query based on the query builder and count option.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance specifying the select fields.
            count: The count option, which can be 'exact' or None.

        Returns:
            (SyncSelectRequestBuilder): A SyncSelectRequestBuilder instance representing the select query.
        """

        if count == 'exact':
            _query = self.query.select(*query_builder.select_fields, count=count)
        else:
            _query = self.query.select(*query_builder.select_fields)
        return _query

    def _add_filters(self, *, query_builder: 'QueryBuilder') -> 'BaseFilterRequestBuilder':
        """
        Adds filters to the query based on the query builder.

        Args:
            query_builder (QueryBuilder): The QueryBuilder instance specifying
                                          the filter criteria. The filter criteria are
                                          expected to be in the `equal` and `not_equal` attributes of the QueryBuilder.

        Returns:
            (BaseFilterRequestBuilder): A BaseFilterRequestBuilder instance representing
                                        the query with the added filters.
        """

        _query = self.query

        equal = query_builder.equal
        not_equal = query_builder.not_equal
        less_than_or_equal = query_builder.less_than_or_equal
        greater_than = query_builder.greater_than

        for equal_filter in equal:
            _query = _query.eq(*equal_filter)

        for not_equal_filter in not_equal:
            _query = _query.neq(*not_equal_filter)

        for lte_filter in less_than_or_equal:
            _query = _query.lte(*lte_filter)

        for gt_filter in greater_than:
            _query = _query.gt(*gt_filter)

        return _query
