import os
from typing import Any, Dict, Iterable, List

from supabase.client import create_client


class SupabaseClient:
    def __init__(self, table_name: str):
        url: str = os.getenv('SUPABASE_URL') or ''
        key: str = os.getenv('SUPABASE_KEY') or ''
        supabase_client = create_client(url, key)
        self.query = supabase_client.table(table_name=table_name)

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.query.insert(data).execute()
        return response.data[0]

    def update(self, *, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.query.update(data).eq('id', id).execute()
        return response.data[0]

    def select(self, *, eq: Dict[str, Any] | None = None, neq: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
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
        self.query.delete().eq('id', id).execute()

    def bulk_update(self, *, ids: Iterable[int], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        response = self.query.update(data).in_('id', ids).execute()
        return response.data

    def bulk_delete(self, *, ids: Iterable[int]) -> List[Dict[str, Any]]:
        response = self.query.delete().in_('id', ids).execute()
        return response.data
