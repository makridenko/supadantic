from typing import List, Tuple

from supadantic.models import BaseSBModel

from .supabase_client import SupabaseClientMock


class ModelMock(BaseSBModel):
    name: str
    some_optional_list: List[str] | None = None
    some_optional_tuple: Tuple[int] | None = None

    @classmethod
    def _get_table_name(cls) -> str:
        return 'test'

    @classmethod
    def _get_db_client(cls) -> SupabaseClientMock:  # pyright: ignore
        return SupabaseClientMock(table_name='test')
