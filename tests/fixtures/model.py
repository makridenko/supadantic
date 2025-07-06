from typing import TYPE_CHECKING

import pytest

from supadantic.clients import CacheClient
from supadantic.models import BaseSBModel


if TYPE_CHECKING:
    from collections.abc import Generator


class ModelMock(BaseSBModel):
    id: int | None = None
    name: str
    age: int | None = None
    some_optional_list: list[str] | None = None
    some_optional_tuple: tuple[str, ...] | None = None  # noqa: CCE001

    class Meta:
        db_client = CacheClient


class ModelMockCustomSchema(ModelMock):
    class Meta:
        db_client = CacheClient
        schema = 'custom_schema'


@pytest.fixture(scope='function')
def model_mock() -> type[ModelMock]:
    return ModelMock


@pytest.fixture(scope='function')
def model_mock_custom_schema() -> type[ModelMockCustomSchema]:
    return ModelMockCustomSchema


@pytest.fixture(autouse=True, scope='function')
def clean_db_cache(model_mock: type['ModelMock']) -> 'Generator':
    yield
    model_mock.objects._cache = []
    model_mock.objects.all().delete()


@pytest.fixture(autouse=True, scope='function')
def clean_db_cache_custom_schema(model_mock_custom_schema: type['ModelMockCustomSchema']) -> 'Generator':
    yield
    model_mock_custom_schema.objects._cache = []
    model_mock_custom_schema.objects.all().delete()
