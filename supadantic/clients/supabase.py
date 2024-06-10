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

        Args:
            data (Dict[str, Any]): The data to insert.

        Returns:
            (Dict[str, Any]): The inserted record.
        """

        response = self.query.insert(data).execute()
        return response.data[0]

    def update(self, *, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a record in the table.

        Args:
            id (int): The ID of the record to update.
            data (Dict[str, Any]): The data to update.

        Returns:
            (Dict[str, Any]): The updated record.
        """

        response = self.query.update(data).eq('id', id).execute()
        return response.data[0]

    def select(self, *, eq: Dict[str, Any] | None = None, neq: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        """
        Select records from the table.

        Args:
            eq (Dict[str, Any] | None): The equality filter.
            neq (Dict[str, Any] | None): The non-equality filter.

        Returns:
            (List[Dict[str, Any]]): The selected records.
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

        Args:
            id (int): The ID of the record to delete.
        """

        self.query.delete().eq('id', id).execute()

    def bulk_update(self, *, ids: Iterable[int], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Bulk update records in the table.

        Args:
            ids (Iterable[int]): The IDs of the records to update.
            data (Dict[str, Any]): The data to update.

        Returns:
            (List[Dict[str, Any]]): List of updated records.
        """

        response = self.query.update(data).in_('id', ids).execute()
        return response.data

    def bulk_delete(self, *, ids: Iterable[int]) -> List[Dict[str, Any]]:
        """
        Bulk delete records from the table.

        Args:
            ids (Iterable[int]): The IDs of the records to delete.

        Returns:
            (List[Dict[str, Any]]): List of deleted records.
        """

        response = self.query.delete().in_('id', ids).execute()
        return response.data
