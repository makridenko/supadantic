import ast
from abc import ABC
from copy import copy
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from pydantic import BaseModel, model_validator
from pydantic._internal._model_construction import ModelMetaclass as PydanticModelMetaclass

from supadantic.clients import SupabaseClient
from supadantic.q_set import QSet
from supadantic.query_builder import QueryBuilder
from supadantic.utils import _to_snake_case


if TYPE_CHECKING:
    from clients.base import BaseClient


_M = TypeVar('_M', bound='BaseSBModel')  # noqa: WPS111


class ModelOptions:
    """
    Configuration class to store model metadata and options.
    """

    def __init__(
        self,
        table_name: str | None = None,
        db_client: type['BaseClient'] | None = None,
        schema: str | None = None,
    ):
        self.table_name = table_name
        self.db_client = db_client or SupabaseClient
        self.schema = schema


class ModelMetaclass(PydanticModelMetaclass):
    """
    Metaclass for BaseSBModel, handling Meta class configuration and objects property.
    """

    def __new__(mcs, name, bases, namespace):
        target_cls = super().__new__(mcs, name, bases, namespace)
        meta = namespace.get('Meta')
        options = ModelOptions()

        if meta is not None:
            if hasattr(meta, 'table_name'):
                options.table_name = meta.table_name

            if hasattr(meta, 'db_client'):
                options.db_client = meta.db_client

            if hasattr(meta, 'schema'):
                options.schema = meta.schema

        target_cls._meta = options
        return target_cls

    @property
    def objects(cls: type[_M]) -> QSet[_M]:  # type: ignore
        """
        Returns a QSet instance for querying the model's table.
        This is the primary interface for querying the database for instances of the model.
        """
        return QSet[_M](cls)


class BaseSBModel(BaseModel, ABC, metaclass=ModelMetaclass):
    """
    Abstract base model for Supabase tables, integrating with Pydantic.

    This class provides a foundation for creating Pydantic models that map to tables
    in a Supabase database.

    Subclasses should define their table structure using Pydantic's field
    definition syntax. They can override methods such as `db_client()` to
    customize the database client used for interactions.
    """

    class DoesNotExist(Exception):
        """
        Exception raised when a query returns no results but at least one result was expected.
        """

        ...

    class MultipleObjectsReturned(Exception):
        """
        Exception raised when a query returns multiple results but only one result was expected.
        """

        ...

    id: int | None = None
    _meta: ClassVar[ModelOptions]

    def save(self: _M) -> _M:
        """
        Saves the model instance to the database (either inserting or updating).

        If the model instance has an ID, it is updated in the database.  Otherwise,
        it is inserted as a new record.  The model instance is updated with the
        data returned from the database after the save operation.

        Returns:
            (_Model): The saved model instance, updated with data from the database (e.g.,
                    the assigned ID for a new record).
        """

        db_client = self._get_db_client()
        data = self.model_dump(exclude={'id'}, mode='json')

        query_builder = QueryBuilder()

        if self.id:
            query_builder.set_equal(id=self.id)
            query_builder.set_update_data(data)
        else:
            query_builder.set_insert_data(data)

        response_data = db_client.execute(query_builder=query_builder)[0]
        return self.__class__(**response_data)

    def delete(self: _M) -> None:
        """
        Deletes the model instance from the database.

        This method deletes the record from the database corresponding to the
        model instance's ID. If the model instance does not have an ID, this
        method does nothing.
        """

        if self.id:
            query_builder = QueryBuilder()
            query_builder.set_equal(id=self.id)
            query_builder.set_delete_mode(True)

            db_client = self._get_db_client()
            db_client.execute(query_builder=query_builder)

    @classmethod
    def db_client(cls) -> type['BaseClient']:
        """
        Gets the database client class to use for interactions.

        This method can be overridden in subclasses to provide a custom database
        client implementation.  The default implementation returns `SupabaseClient`.

        Returns:
            (BaseClient): The database client class.
        """

        return cls._meta.db_client

    @classmethod
    def _get_table_name(cls) -> str:
        """
        Gets the table name associated with the model.
        If no table_name is specified in Meta class, converts class name to snake_case.
        """
        return cls._meta.table_name or _to_snake_case(cls.__name__)

    @classmethod
    def _get_db_client(cls) -> 'BaseClient':
        """
        Retrieves the database client instance for the model.
        """
        table_name = cls._get_table_name()
        schema = cls._meta.schema
        client = cls.db_client()(table_name, schema)
        return client

    @model_validator(mode='before')
    def _validate_data_from_supabase(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validates and transforms data received from Supabase before it is used to create a model instance.

        This method converts string representations of arrays (which are how Supabase
        returns arrays) back into Python lists. This ensures that the data is in
        the correct format for Pydantic to validate it.

        Args:
            data (dict[str, Any]): The data received from Supabase, as a dictionary.

        Returns:
            (dict[str, Any]): The validated data, with string arrays converted to Python lists.
        """

        array_fields = []
        result_dict = copy(data)

        for key, value in cls.model_json_schema()['properties'].items():
            any_of_items = value.get("anyOf", [])
            is_any_array = any(item.get("type") == "array" for item in any_of_items)
            field_is_array = any(
                (
                    # If field is required, it's possible to get type
                    value.get('type') == 'array',
                    # If field is optional, it's possible to get type from anyOf array
                    is_any_array,
                )
            )

            if field_is_array:
                array_fields.append(key)

        for key, value in data.items():
            if key in array_fields and isinstance(value, str):
                result_dict[key] = ast.literal_eval(value)

        return result_dict
