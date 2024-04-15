from abc import ABC, abstractmethod
from typing import List, NoReturn

from pydantic import BaseModel
from typing_extensions import Self

from .supabase_client import SupabaseClient


class BaseDBEntity(BaseModel, ABC):
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
    def get_list(cls: type[Self], *, eq: dict | None = None, neq: dict | None = None) -> List[Self]:
        db_client = cls._get_db_client()
        _filters = {}

        if eq:
            _filters['eq'] = eq

        if neq:
            _filters['neq'] = neq

        response_data = db_client.select(**_filters)
        return list(cls(**data) for data in response_data)

    def save(self: Self) -> Self:
        db_client = self._get_db_client()
        data = self.model_dump(exclude={'id'})

        if self.id:
            response_data = db_client.update(id=self.id, data=data)
        else:
            response_data = db_client.insert(data)

        return self.__class__(**response_data)

    @classmethod
    def get(cls, *, eq: dict, neq: dict | None = None) -> Self | NoReturn:
        result = cls.get_list(eq=eq, neq=neq)
        _filters_str = f"eq={eq}, neq={neq}"
        if not result:
            raise cls.DoesNotExist(f'{cls.__name__} object with {_filters_str} does not exist!')

        if len(result) > 1:
            raise cls.MultipleObjectsReturned(f'For {_filters_str} returned more than 1 {cls.__name__} objects!')

        return result[0]

    @classmethod
    def bulk_update(cls, *, ids: List[int], data: dict) -> None:
        db_client = cls._get_db_client()
        db_client.bulk_update(ids=ids, data=data)
