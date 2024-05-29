from typing import Generator, List, Tuple, Type

import pytest

from supadantic.clients import CacheClient
from supadantic.clients.base import BaseClient
from supadantic.models import BaseSBModel


class ModelMock(BaseSBModel):
    name: str
    some_optional_list: List[str] | None = None
    some_optional_tuple: Tuple[str, ...] | None = None

    @classmethod
    def db_client(cls) -> Type[BaseClient]:
        return CacheClient


@pytest.fixture(scope='function')
def model_mock() -> Type[ModelMock]:
    return ModelMock


@pytest.fixture(autouse=True, scope='function')
def clean_db_cache(model_mock: Type['ModelMock']) -> Generator:
    yield
    model_mock.objects._cache = {}  # pyright: ignore
    model_mock.objects.all().delete()  # pyright: ignore
