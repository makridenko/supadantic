from typing import TYPE_CHECKING, Any, Dict, List, NoReturn, Type

from typing_extensions import Self


if TYPE_CHECKING:
    from .clients.base import BaseClient
    from .models import BaseSBModel


class QSet:
    """Lazy database lookup for a set of objects."""

    class InvalidFilter(Exception):
        pass

    class InvalidField(Exception):
        pass

    def __init__(self, model_class: Type['BaseSBModel'], objects: List['BaseSBModel'] | None = None) -> None:
        """
        Initialize the QSet with the model class and objects.

        Args:
            model_class (Type[BaseSBModel]): The model class.
            objects (List[BaseSBModel] | None): The objects to initialize the QSet with.
        """

        self._model_class = model_class
        self.objects = objects if objects else []

    @property
    def client(self) -> 'BaseClient':
        """
        Get the database client for the model.

        Returns:
            (BaseClient): The database client.
        """

        return self._model_class._get_db_client()

    def update(self, **data) -> int | NoReturn:
        """
        Update the objects in the QSet with the data.
        If data is not valid, raise an InvalidField exception.

        Returns:
            (int): The number of objects updated.

        Raises:
            (InvalidField): If the field is not valid.

        Examples:
            >>> qs = Model.objects.update(name='new_name')
        """

        for field in data.keys():
            if field not in self._model_class.model_fields.keys():
                raise self.InvalidField(f'Invalid field {field}!')

        ids = tuple(obj.id for obj in self.objects)
        response_data = self.client.bulk_update(ids=ids, data=data)  # pyright: ignore
        return len(response_data)

    def delete(self) -> int:
        """
        Delete the objects in the QSet.

        Returns:
            (int): The number of objects deleted.

        Examples:
            >>> Model.objects.filter(name='name').delete()
        """

        ids = tuple(obj.id for obj in self.objects)
        response_data = self.client.bulk_delete(ids=ids)  # pyright: ignore
        self.objects = []
        return len(response_data)

    def all(self) -> Self:
        """
        Get all objects from the database.

        Returns:
            (Self): The QSet with all objects.

        Examples:
            >>> qs = Model.objects.all()
        """

        response_data = self.client.select()
        self.objects = list(self._model_class(**data) for data in response_data)
        return self._copy()

    def _select(self, eq: Dict[str, Any] | None = None, neq: Dict[str, Any] | None = None) -> Self:
        """
        Select objects from the database with the equality and non-equality filters.

        Args:
            eq (Dict[str, Any] | None): The equality filter.
            neq (Dict[str, Any] | None): The non-equality filter.

        Returns:
            (Self): The QSet with the selected objects.
        """

        response_data = self.client.select(eq=eq, neq=neq)
        objects = list(self._model_class(**data) for data in response_data)
        return self.__class__(model_class=self._model_class, objects=objects)

    def _validate_filters(self, **filters) -> None | NoReturn:
        """
        Validate the filters.
        If a filter is not valid, raise an InvalidFilter exception.

        Raises:
            (InvalidFilter): If a filter is not valid.
        """
        for filter_name in filters.keys():
            if filter_name not in self._model_class.model_fields.keys():
                raise self.InvalidFilter(f'Invalid filter {filter_name}!')

    def filter(self, **filters) -> Self:
        """
        Filter objects from the database with the filters.

        Returns:
            (Self): The QSet with the filtered objects.

        Examples:
            >>> qs = Model.objects.filter(name='name')
        """

        self._validate_filters(**filters)
        return self._select(eq=filters)

    def exclude(self, **filters) -> Self:
        """
        Exclude objects from the database with the filters.

        Returns:
            (Self): The QSet with the excluded objects.

        Examples:
            >>> qs = Model.objects.exclude(name='name')
        """

        self._validate_filters(**filters)
        return self._select(neq=filters)

    def get(self, **filters) -> 'BaseSBModel' | NoReturn:
        """
        Get an object from the database with the filters.
        If the object does not exist, raise a DoesNotExist exception.
        If more than one object exists, raise a MultipleObjectsReturned exception.

        Returns:
            (BaseSBModel): The object.

        Raises:
            (DoesNotExist): If the object does not exist or more than one object exists.

        Examples:
            >>> obj = Model.objects.get(name='name')
        """

        self._validate_filters(**filters)
        result_qs = self._select(eq=filters)

        if not result_qs:
            raise self._model_class.DoesNotExist(f'{self._model_class.__name__} object with {filters} does not exist!')

        if result_qs.count() > 1:
            raise self._model_class.MultipleObjectsReturned(
                f'For {filters} returned more than 1 {self._model_class.__name__} objects!'
            )

        return result_qs.first()  # pyright: ignore

    def count(self) -> int:
        """
        Get the number of objects in the QSet.

        Returns:
            (int): The number of objects in the QSet.

        Examples:
            >>> count = Model.objects.count()
        """

        return len(self.objects)

    def first(self) -> 'BaseSBModel | None':
        """
        Get the first object in the QSet.
        If the QSet is empty, return None.

        Returns:
            (BaseSBModel | None): The first object in the QSet.

        Examples:
            >>> first_obj = Model.objects.all().first()
        """

        if self.count():
            return self[0]

    def last(self) -> 'BaseSBModel | None':
        """
        Get the last object in the QSet.
        If the QSet is empty, return None.

        Returns:
            (BaseSBModel | None): The last object in the QSet.

        Examples:
            >>> last_obj = Model.objects.all().last()
        """

        if self.count():
            return self[-1]

    def _copy(self) -> Self:
        """
        Copy the QSet.

        Returns:
            (Self): The copied QSet.
        """
        return self.__class__(model_class=self._model_class, objects=self.objects)

    def __iter__(self):
        return iter(self.objects)

    def __len__(self) -> int:
        return len(self.objects)

    def __getitem__(self, index: int) -> 'BaseSBModel':
        return list(self)[index]

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {list(self)} >'

    def __eq__(self, obj: object) -> bool:
        return all(
            (
                self._model_class == getattr(obj, '_model_class'),
                self.objects == getattr(obj, 'objects'),
            )
        )
