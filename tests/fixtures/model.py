from typing import TYPE_CHECKING

import pytest

from supadantic.clients import CacheClient
from supadantic.models import BaseSBModel


if TYPE_CHECKING:
    from collections.abc import Generator

    from supadantic.clients.base import BaseClient


class ModelMock(BaseSBModel):
    id: int | None = None
    name: str
    some_optional_list: list[str] | None = None
    some_optional_tuple: tuple[str, ...] | None = None

    @classmethod
    def db_client(cls) -> type['BaseClient']:
        return CacheClient


@pytest.fixture(scope='function')
def model_mock() -> type[ModelMock]:
    return ModelMock


@pytest.fixture(autouse=True, scope='function')
def clean_db_cache(model_mock: type['ModelMock']) -> 'Generator':
    yield
    model_mock.objects._cache = []
    model_mock.objects.all().delete()
