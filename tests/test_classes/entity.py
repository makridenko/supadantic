from supadantic.base import BaseDBEntity

from .supabase_client import SupabaseClientMock


class EntityMock(BaseDBEntity):
    name: str

    @classmethod
    def _get_table_name(cls) -> str:
        return 'test'

    @classmethod
    def _get_db_client(cls):  # pyright: ignore
        return SupabaseClientMock(table_name='test')
