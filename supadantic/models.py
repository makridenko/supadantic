from abc import ABC, abstractmethod
from typing import Dict, NoReturn

from pydantic import BaseModel
from typing_extensions import Self

from .clients import SupabaseClient
from .q_set import QSet


class BaseSBModel(BaseModel, ABC):
    id: int | None = None

    class DoesNotExist(Exception):
        pass

    class MultipleObjectsReturned(Exception):
        pass

    @classmethod
    @abstractmethod
    def _get_table_name(cls) -> str:
        pass

    @classmethod
    def _get_db_client(cls) -> SupabaseClient:
        table_name = cls._get_table_name()
        return SupabaseClient(table_name=table_name)

    @classmethod
    def all(cls) -> QSet:
        return QSet(model_class=cls).all()

    @classmethod
    def filter(cls: type[Self], *, eq: Dict | None = None, neq: Dict | None = None) -> QSet:
        return QSet(model_class=cls).filter(eq=eq, neq=neq)

    def save(self: Self) -> Self:
        db_client = self._get_db_client()
        data = self.model_dump(exclude={'id'})

        if self.id:
            response_data = db_client.update(id=self.id, data=data)
        else:
            response_data = db_client.insert(data)

        return self.__class__(**response_data)

    @classmethod
    def get(cls, *, eq: Dict, neq: Dict | None = None) -> Self | NoReturn:
        result_qs = cls.filter(eq=eq, neq=neq)
        _filters_str = f"eq={eq}, neq={neq}"
        if not result_qs:
            raise cls.DoesNotExist(f'{cls.__name__} object with {_filters_str} does not exist!')

        if result_qs.count() > 1:
            raise cls.MultipleObjectsReturned(f'For {_filters_str} returned more than 1 {cls.__name__} objects!')

        return result_qs.first()  # pyright: ignore

    def delete(self: Self) -> None:
        if self.id:
            db_client = self._get_db_client()
            db_client.delete(id=self.id)
