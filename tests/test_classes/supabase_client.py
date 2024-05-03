from copy import copy
from typing import Any, Dict, Iterable, List

from supadantic.clients.base import BaseClient


class SupabaseClientMock(BaseClient):
    def __init__(self, table_name: str):
        pass

    def _get_return_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result_data = copy(data)

        for key, value in data.items():
            if type(value) in (list, tuple):
                result_data.update({key: str(value)})

        return result_data

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data = dict(id=1, **data)
        return self._get_return_data(data=data)

    def update(self, *, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        data['id'] = id
        return self._get_return_data(data=data)

    def select(self, *, eq: Dict[str, Any] | None = None, neq: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        data = [
            {'id': 1, 'name': 'test_name'},
            {'id': 2, 'name': 'unique_name'},
            {'id': 3, 'name': 'test_name'},
            {'id': 4, 'name': 'new_name'},
        ]

        def _filter(obj: Dict) -> bool:
            _eq = eq if eq else {}
            _neq = neq if neq else {}
            for key, value in _eq.items():
                if not obj[key] == value:
                    return False
            for key, value in _neq.items():
                if not obj[key] != value:
                    return False
            return True

        return list(filter(_filter, data))

    def delete(self, *, id: int) -> None:
        pass

    def bulk_update(self, *, ids: Iterable[int], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return list(dict(id=_id, **data) for _id in ids)

    def bulk_delete(self, *, ids: Iterable[int]) -> List[Dict[str, Any]]:
        return list(dict(id=_id) for _id in ids)
