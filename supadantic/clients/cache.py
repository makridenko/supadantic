from copy import copy
from typing import Any, Dict, Iterable, List

from .base import BaseClient


class CacheClient(BaseClient):
    """Client for caching data in memory."""

    def __init__(self, table_name: str) -> None:
        """Initialize the client with the table name."""
        super().__init__(table_name=table_name)

        # The cache of records
        self._cache: Dict[int, dict] = {}

    def _get_return_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the return data for a record.
        Supabase returns iterables as strings, so we need to convert them back.

        :param data: The record data.
        :return: The return data.
        """
        result_data = copy(data)

        for key, value in data.items():
            if type(value) in (list, tuple):
                result_data.update({key: str(value)})

        return result_data

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a new record into the table.

        :param data: The data to insert.
        :return: The inserted record.
        """

        # Get the next ID
        if _ids := list(self._cache.keys()):
            _id = _ids[-1] + 1
        else:
            _id = 1

        data['id'] = _id

        self._cache[_id] = data
        return self._get_return_data(self._cache[_id])

    def update(self, *, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a record in the table.

        :param id: The ID of the record to update.
        :param data: The data to update.

        :return: The updated record.
        """
        self._cache[id].update(data)
        return self._get_return_data(self._cache[id])

    def select(self, *, eq: Dict[str, Any] | None = None, neq: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        """
        Select records from the table.

        :param eq: The equality filter.
        :param neq: The non-equality filter.

        :return: The selected records.
        """

        def _filter(obj: Dict[str, Any]) -> bool:
            """Filter the records based on the equality and non-equality filters."""
            _eq = eq if eq else {}
            _neq = neq if neq else {}

            for key, value in _eq.items():
                if not obj[key] == value:
                    return False

            for key, value in _neq.items():
                if not obj[key] != value:
                    return False

            return True

        return list(filter(_filter, self._cache.values()))

    def delete(self, *, id: int) -> None:
        """
        Delete a record from the table.

        :param id: The ID of the record to delete.
        """

        del self._cache[id]

    def bulk_update(self, *, ids: Iterable[int], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Bulk update records in the table.

        :param ids: The IDs of the records to update.

        :param data: List of updated data.
        """

        result = []
        for _id in ids:
            self._cache[_id].update(data)
            result.append(self._cache[_id])

        return result

    def bulk_delete(self, *, ids: Iterable[int]) -> List[Dict[str, Any]]:
        """
        Bulk delete records in the table.

        :param ids: The IDs of the records to delete.

        :return: List of deleted records.
        """

        result = []
        for _id in ids:
            result.append(self._cache[_id])
            del self._cache[_id]
        return result
