from supadantic.models import BaseSBModel

from .supabase_client import SupabaseClientMock


class ModelMock(BaseSBModel):
    name: str

    @classmethod
    def _get_table_name(cls) -> str:
        return 'test'

    @classmethod
    def _get_db_client(cls):  # pyright: ignore
        return SupabaseClientMock(table_name='test')
