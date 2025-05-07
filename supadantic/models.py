import ast
import re
from abc import ABC
from copy import copy
from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel, model_validator
from pydantic._internal._model_construction import ModelMetaclass as PydanticModelMetaclass

from .clients import SupabaseClient
from .q_set import QSet
from .query_builder import QueryBuilder


if TYPE_CHECKING:
    from clients.base import BaseClient


_M = TypeVar('_M', bound='BaseSBModel')


def _to_snake_case(value: str) -> str:
    """
    Converts a string from camel case or Pascal case to snake case.

    This function uses a regular expression to find uppercase letters within
    the string and inserts an underscore before them (except at the beginning
    of the string).  The entire string is then converted to lowercase.

    Args:
        value (str): The string to convert.

    Returns:
        (str): The snake_case version of the input string.

    Example:
        >>> _to_snake_case("MyClassName")
        'my_class_name'
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()


class ModelMetaclass(PydanticModelMetaclass):
    """
    Metaclass for BaseSBModel, adding a custom `objects` property.

    This metaclass extends Pydantic's ModelMetaclass to provide a custom `objects`
    property on each class that uses it. The `objects` property returns a `QSet`
    instance, which is used for performing database queries related to the model.
    """

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

        pass

    class MultipleObjectsReturned(Exception):
        """
        Exception raised when a query returns multiple results but only one result was expected.
        """

        pass

    id: int | None = None

    def save(self: _M) -> _M:
        """
        Saves the model instance to the database (either inserting or updating).

        If the model instance has an ID, it is updated in the database.  Otherwise,
        it is inserted as a new record.  The model instance is updated with the
        data returned from the database after the save operation.

        Returns:
            (_M): The saved model instance, updated with data from the database (e.g.,
                    the assigned ID for a new record).
        """

        db_client = self._get_db_client()
        data = self.model_dump(exclude={'id'})

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

        return SupabaseClient

    @classmethod
    def _get_table_name(cls) -> str:
        """
        Gets the table name associated with the model, converting the class name to snake case.

        This method converts the class name to snake_case to determine the corresponding
        table name in the database.

        Returns:
            (str): The table name in snake_case.
        """
        return _to_snake_case(cls.__name__)

    @classmethod
    def _get_db_client(cls) -> 'BaseClient':
        """
        Retrieves the database client instance for the model, configured with the table name.

        This method creates a database client instance using the `db_client()` method
        and initializes it with the appropriate table name.

        Returns:
            (BaseClient): An initialized instance of the database client.
        """

        table_name = cls._get_table_name()
        return cls.db_client()(table_name)

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
            _field_is_array = any(
                (
                    # If field is required, it's possible to get type
                    value.get('type') == 'array',
                    # If field is optional, it's possible to get type from anyOf array
                    any(item.get('type') == 'array' for item in value.get('anyOf', [])),
                )
            )

            if _field_is_array:
                array_fields.append(key)

        for key, value in data.items():
            if key in array_fields and isinstance(value, str):
                result_dict[key] = ast.literal_eval(value)

        return result_dict
