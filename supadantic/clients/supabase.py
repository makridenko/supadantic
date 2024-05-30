import os
from typing import Any, Dict, Iterable, List

from supabase.client import create_client

from .base import BaseClient


class SupabaseClient(BaseClient):
    """Client for Supabase."""

    def __init__(self, table_name: str):
        """
        Initialize the client with the table name.
        It creates a Supabase client and a query object.
        """

        super().__init__(table_name=table_name)
        url: str = os.getenv('SUPABASE_URL') or ''
        key: str = os.getenv('SUPABASE_KEY') or ''
        supabase_client = create_client(url, key)
        self.query = supabase_client.table(table_name=self.table_name)

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a new record into the table.

        :param data: The data to insert.

        :return: The inserted record.
        """

        response = self.query.insert(data).execute()
        return response.data[0]

    def update(self, *, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a record in the table.

        :param id: The ID of the record to update.
        :param data: The data to update.

        :return: The updated record.
        """

        response = self.query.update(data).eq('id', id).execute()
        return response.data[0]

    def select(self, *, eq: Dict[str, Any] | None = None, neq: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        """
        Select records from the table.

        :param eq: The equality filter.
        :param neq: The non-equality filter.

        :return: The selected records.
        """

        _query = self.query.select('*')

        if eq:
            for eq_filter in list(eq.items()):
                _query = _query.eq(*eq_filter)

        if neq:
            for neq_filter in list(neq.items()):
                _query = _query.neq(*neq_filter)

        response = _query.execute()
        return response.data

    def delete(self, *, id: int) -> None:
        """
        Delete a record from the table.

        :param id: The ID of the record to delete.
        """

        self.query.delete().eq('id', id).execute()

    def bulk_update(self, *, ids: Iterable[int], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Bulk update records in the table.

        :param ids: The IDs of the records to update.
        :param data: The data to update.

        :return: List of updated records.
        """

        response = self.query.update(data).in_('id', ids).execute()
        return response.data

    def bulk_delete(self, *, ids: Iterable[int]) -> List[Dict[str, Any]]:
        """
        Bulk delete records from the table.

        :param ids: The IDs of the records to delete.
        """

        response = self.query.delete().in_('id', ids).execute()
        return response.data
