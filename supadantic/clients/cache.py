from copy import copy
from typing import Any, Dict, Iterable, List

from .base import BaseClient


class CacheClient(BaseClient):
    def __init__(self, table_name: str) -> None:
        super().__init__(table_name=table_name)

        self._cache: Dict[int, dict] = {}

    def _get_return_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result_data = copy(data)

        for key, value in data.items():
            if type(value) in (list, tuple):
                result_data.update({key: str(value)})

        return result_data

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if _ids := list(self._cache.keys()):
            _id = _ids[-1] + 1
        else:
            _id = 1

        data['id'] = _id

        self._cache[_id] = data
        return self._get_return_data(self._cache[_id])

    def update(self, *, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        self._cache[id].update(data)
        return self._get_return_data(self._cache[id])

    def select(self, *, eq: Dict[str, Any] | None = None, neq: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        def _filter(obj: Dict[str, Any]) -> bool:
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
        del self._cache[id]

    def bulk_update(self, *, ids: Iterable[int], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = []
        for _id in ids:
            self._cache[_id].update(data)
            result.append(self._cache[_id])

        return result

    def bulk_delete(self, *, ids: Iterable[int]) -> List[Dict[str, Any]]:
        result = []
        for _id in ids:
            result.append(self._cache[_id])
            del self._cache[_id]
        return result
