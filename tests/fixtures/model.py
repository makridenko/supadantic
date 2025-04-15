from typing import Generator, Type

import pytest

from supadantic.clients import CacheClient
from supadantic.clients.base import BaseClient
from supadantic.models import BaseSBModel


class ModelMock(BaseSBModel):
    id: int | None = None
    name: str
    age: int | None = None
    some_optional_list: list[str] | None = None
    some_optional_tuple: tuple[str, ...] | None = None

    @classmethod
    def db_client(cls) -> Type[BaseClient]:
        return CacheClient


@pytest.fixture(scope='function')
def model_mock() -> Type[ModelMock]:
    return ModelMock


@pytest.fixture(autouse=True, scope='function')
def clean_db_cache(model_mock: Type['ModelMock']) -> Generator:
    yield
    model_mock.objects._cache = {}
    model_mock.objects.all().delete()
