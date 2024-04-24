from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Type

from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass as PydanticModelMetaclass
from typing_extensions import Self

from .clients import SupabaseClient
from .q_set import QSet


class ModelMetaclass(PydanticModelMetaclass):
    def __new__(mcs: Type, cls_name: str, bases: Tuple[Type[Any], ...], namespace: Dict[str, Any], **kwargs: Any):
        new_model = super().__new__(mcs, cls_name, bases, namespace, **kwargs)  # pyright: ignore
        new_model.objects = QSet(new_model)
        return new_model


class BaseSBModel(BaseModel, ABC, metaclass=ModelMetaclass):
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

    def save(self: Self) -> Self:
        db_client = self._get_db_client()
        data = self.model_dump(exclude={'id'})

        if self.id:
            response_data = db_client.update(id=self.id, data=data)
        else:
            response_data = db_client.insert(data)

        return self.__class__(**response_data)

    def delete(self: Self) -> None:
        if self.id:
            db_client = self._get_db_client()
            db_client.delete(id=self.id)
