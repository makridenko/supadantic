import json
import re
from abc import ABC
from copy import copy
from typing import Any, Dict

from pydantic import BaseModel, model_validator
from pydantic._internal._model_construction import ModelMetaclass as PydanticModelMetaclass
from typing_extensions import Self

from .clients import SupabaseClient
from .q_set import QSet


def _to_snake_case(value: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()


class ModelMetaclass(PydanticModelMetaclass):
    def __new__(mcs, name: str, bases: Any, namespace: dict, *args, **kwargs) -> type:
        new_model = super().__new__(mcs, name, bases, namespace, *args, **kwargs)
        new_model.objects = QSet(new_model)
        return new_model


class BaseSBModel(BaseModel, ABC, metaclass=ModelMetaclass):
    id: int | None = None

    class DoesNotExist(Exception):
        pass

    class MultipleObjectsReturned(Exception):
        pass

    @classmethod
    def _get_table_name(cls) -> str:
        return _to_snake_case(cls.__name__)

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

    @model_validator(mode='before')
    def _validate_data_from_supabase(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        array_fields = []
        result_dict = copy(data)

        for key, value in cls.model_json_schema()['properties'].items():
            _field_is_array = any(
                (
                    # If field is required, it's possible to get type
                    value.get('type', None) == 'array',
                    # If field is optional, it's possible to get type from anyOf array
                    any(item.get('type', None) == 'array' for item in value.get('anyOf', [])),
                )
            )

            if _field_is_array:
                array_fields.append(key)

        for key, value in data.items():
            if key in array_fields and isinstance(value, str):
                result_dict[key] = json.loads(data[key])

        return result_dict
