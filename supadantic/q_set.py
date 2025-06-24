from typing import TYPE_CHECKING, Any, Generic, TypeVar

from supadantic.query_builder import QueryBuilder


if TYPE_CHECKING:
    from .clients.base import BaseClient
    from .models import BaseSBModel


_M = TypeVar('_M', bound='BaseSBModel')


class QSet(Generic[_M]):
    """
    Represents a set of query operations for a specific model.

    This class provides a chainable interface for building and executing database
    queries related to a particular model. It handles filtering, updating,
    creating, deleting, and retrieving data.  It's designed to work with a
    `BaseClient` for interacting with the database and a `QueryBuilder` for
    constructing queries.

    Examples:
        >>> # Get all instances of the Model class.
        >>> all_models = Model.objects.all()
        >>>
        >>> # Filter for instances with name equal to "example".
        >>> filtered_models = Model.objects.filter(name="example")
        >>>
        >>> # Get the last instance.
        >>> last_model = Model.objects.last()
    """

    class InvalidFilter(Exception):
        """
        Exception raised when attempting to update or create a record with an invalid field.
        """

        pass

    class InvalidField(Exception):
        """
        Exception raised when attempting to filter with an invalid field.
        """

        pass

    def __init__(
        self,
        model_class: type[_M],
        cache: list[_M] | None = None,
        query_builder: QueryBuilder | None = None,
    ) -> None:
        """
        Initializes the QSet with the model class, cache, and query builder.

        Args:
            model_class (Type[_M]): The model class associated with this QSet.
            cache (list[_M] | None): An optional initial cache of model instances.
            query_builder (QueryBuilder | None): An optional QueryBuilder instance.  If None, a new
                                                 instance is created.
        """

        self._model_class = model_class
        self._cache = cache
        self._query_builder = query_builder if query_builder else QueryBuilder()

    def delete(self) -> int:
        """
        Deletes the objects in the QSet from the database.

        This method sets the `delete_mode` attribute on the QueryBuilder and executes
        the query. It returns the number of objects that were deleted.

        Returns:
            (int): The number of objects deleted.

        Examples:
            >>> num_deleted = Model.objects.filter(active=False).delete()
        """

        self._query_builder.set_delete_mode(True)
        self._execute()
        return len(self._cache) if self._cache else 0

    @property
    def client(self) -> 'BaseClient':
        """
        Gets the database client for the model.

        This method retrieves the database client associated with the model class.
        The database client is responsible for executing the queries.

        Returns:
            (BaseClient): The database client instance.
        """

        return self._model_class._get_db_client()

    def all(self) -> 'QSet[_M]':
        """
        Returns a QSet containing all instances of the associated model.

        This method clears any existing filters on the QSet.

        Returns:
            (QSet[_M]): A QSet containing all instances of the model.

        Examples:
            >>> qs = Model.objects.all()
        """

        return self._copy()

    def filter(self, **filters: Any) -> 'QSet[_M]':
        """
        Returns a QSet filtered by the given keyword arguments.

        Each keyword argument represents a field name and its desired value.
        Multiple filters are combined with AND logic.

        Args:
            **filters: Keyword arguments representing the filter criteria.

        Returns:
            (QSet[_M]): A new QSet instance with the specified filters applied.

        Examples:
            >>> qs = Model.objects.filter(name='example', age=20)
        """

        self._validate_filters(**filters)

        for filter_field, value in filters.items():
            filter_type = filter_field.split("__")

            _filters = {filter_type[0]: value}

            if len(filter_type) == 1:
                self._query_builder.set_equal(**_filters)
            elif filter_type[1] == "lte":
                self._query_builder.set_less_than_or_equal(**_filters)
            elif filter_type[1] == "gt":
                self._query_builder.set_greater_than(**_filters)
            elif filter_type[1] == "lt":
                self._query_builder.set_less_than(**_filters)
            elif filter_type[1] == "gte":
                self._query_builder.set_greater_than_or_equal(**_filters)
            elif filter_type[1] == "in":
                self._query_builder.set_included(**_filters)

        return self._copy()

    def exclude(self, **filters: Any) -> 'QSet[_M]':
        """
        Excludes objects based on the provided keyword arguments.

        This method adds non-equality filters to the query. Only objects that do
        not match any of the provided filters will be included in the resulting QSet.

        Args:
            **filters: Keyword arguments representing the filters to apply.

        Returns:
            A new QSet instance with the added exclusion filters.

        Examples:
            >>> qs = Model.objects.exclude(name='example', age=30)
        """

        self._validate_filters(**filters)
        for filter_field, value in filters.items():
            filter_type = filter_field.split("__")

            _filters = {filter_type[0]: value}

            if len(filter_type) == 1:
                self._query_builder.set_not_equal(**_filters)
            elif filter_type[1] == "lte":
                self._query_builder.set_greater_than(**_filters)
            elif filter_type[1] == "gt":
                self._query_builder.set_less_than_or_equal(**_filters)
            elif filter_type[1] == "lt":
                self._query_builder.set_greater_than_or_equal(**_filters)
            elif filter_type[1] == "gte":
                self._query_builder.set_less_than(**_filters)

        return self._copy()

    def get(self, **filters: Any) -> _M:
        """
        Gets a single object matching the provided filters.

        This method retrieves a single object from the database that matches the
        provided filters. If no object matches the filters, a DoesNotExist
        exception is raised. If more than one object matches the filters, a
        MultipleObjectsReturned exception is raised.

        Args:
            **filters: Keyword arguments representing the filters to apply.

        Returns:
            (_M): The object matching the filters.

        Examples:
            >>> qs = Model.objects.get(name='example', age=30)
        """

        self.filter(**filters)
        self._execute()

        if not self._cache:
            raise self._model_class.DoesNotExist(f'{self._model_class.__name__} object with {filters} does not exist!')

        if len(self._cache) > 1:
            raise self._model_class.MultipleObjectsReturned(
                f'For {filters} returned more than 1 {self._model_class.__name__} objects!'
            )

        return self._cache[0]

    def count(self) -> int:
        """
        Gets the number of objects matching the current query.

        This method returns the number of objects in the database that match the
        filters applied to the QSet. If the results are already cached, the
        count is returned from the cache. Otherwise, a database query is executed.

        Returns:
            The number of objects matching the query.

        Examples:
            >>> count = Model.objects.filter(name='example').count()
        """

        if self._cache is not None:
            return len(self._cache)

        self._query_builder.set_count_mode(True)
        result = self.client.execute(query_builder=self._query_builder)
        if not isinstance(result, int):
            raise TypeError(f"Expected int from client.execute in count(), got {type(result)}")

        return result

    def first(self) -> _M | None:
        """
        Gets the first object matching the current query.

        This method returns the first object in the QSet. If the QSet is empty,
        this method returns None.

        Returns:
            The first object in the QSet, or None if the QSet is empty.

        Examples:
            >>> obj = Model.objects.filter(name='example').first()
        """

        try:
            return self[0]
        except IndexError:
            return None

    def last(self) -> _M | None:
        """
        Returns the last object in the QSet.

        If the QSet is empty, returns None. This method executes the query to
        populate the cache before retrieving the last element.

        Returns:
            The last object in the QSet, or None if the QSet is empty.

        Examples:
            >>> obj = Model.objects.all().last()
        """

        try:
            return self[-1]
        except IndexError:
            return None

    def update(self, **data: Any) -> int:
        """
        Updates the objects in the QSet with the provided data.

        This method sets the `update_data` attribute on the QueryBuilder and executes
        the query. It returns the number of objects that were updated.

        Args:
            **data: Keyword arguments representing the fields to update and their new values.

        Returns:
            (int): The number of objects updated.

        Examples:
            >>> num_updated = Model.objects.filter(active=True).update(name='new_name')
        """

        for field in data.keys():
            if field not in self._model_class.model_fields.keys():
                raise self.InvalidField(
                    f"Field '{field}' is not defined for {self._model_class.__name__} model."
                    f"Available fields are: {', '.join(self._model_class.model_fields.keys())}"
                )

        self._query_builder.set_update_data(data)
        self._execute()
        return len(self._cache) if self._cache else 0

    def create(self, **data) -> _M:
        """
        Creates a new instance of the model in the database.

        This method sets the `insert_data` attribute on the QueryBuilder and executes
        the query. It returns a new model instance populated with the data from the
        database after the insert operation.

        Args:
            **data (dict[str, Any]): Keyword arguments representing the fields and their values for the new instance.

        Returns:
            (_M): The newly created model instance.
        """

        for field in data.keys():
            if field not in self._model_class.model_fields.keys():
                raise self.InvalidField(
                    f"Field '{field}' is not defined for {self._model_class.__name__} model."
                    f"Available fields are: {', '.join(self._model_class.model_fields.keys())}"
                )

        self._query_builder.set_insert_data(data)
        response_data = self.client.execute(query_builder=self._query_builder)
        if not isinstance(response_data, list):
            raise TypeError(f"Expected list from client.execute in create(), got {type(response_data)}")

        return self._model_class(**response_data[0])

    def get_or_create(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> tuple[_M, bool]:
        """
        Tries to retrieve an object with the given parameters or creates one if it doesn't exist.

        Args:
            defaults (dict[str, Any] | None): A dictionary of values to use when creating a new object.
            **kwargs (Any): Keyword arguments representing the filter criteria.

        Returns:
            (tuple[_M, bool]): A tuple containing the retrieved or created object and a boolean indicating whether
                               the object was newly created or retrieved.

        Examples:
            >>> obj, created = Model.objects.get_or_create(name="Alex", defaults={"age": 30})
            >>> if created:
            ...     print("New object created!")
            >>> else:
            ...     print("Object retrieved.")
        """

        try:
            return self.get(**kwargs), False
        except self._model_class.DoesNotExist:
            if defaults is not None:
                kwargs.update(defaults)
            new_obj = self.create(**kwargs)
            return new_obj, True

    def exists(self) -> bool:
        """
        Checks if any objects match the current query.

        Returns:
            (bool): True if matching objects exist, False otherwise.

        Examples:
            >>> if Model.objects.filter(name='example').exists():
            ...     print("Objects with name 'example' exist!")
        """

        if self._cache is not None:
            return bool(self._cache)

        result = self.client.execute(query_builder=self._query_builder)
        return bool(result)

    def order_by(self, key: str) -> 'QSet[_M]':
        """
        Orders the query results by the specified field.

        This method sets the ordering of the query results based on the provided key.
        The key can be prefixed with '-' to indicate descending order.

        Args:
            key (str): The field name to order by. Prefix with '-' for descending order.

        Returns:
            (QSet[_M]): A new QSet instance with the ordering applied.

        Examples:
            >>> # Order by name ascending
            >>> qs = Model.objects.order_by('name')
            >>> # Order by age descending
            >>> qs = Model.objects.order_by('-age')

        Raises:
            InvalidField: If the specified field does not exist in the model.
        """

        column = key.split('-')[-1]
        if column not in self._model_class.model_fields.keys():
            raise self.InvalidField(f'Invalid field {column}!')

        self._query_builder.set_order_by_field(key)
        return self._copy()

    def _execute(self) -> None:
        """
        Executes the query and populates the cache with the results.

        This method uses the database client to execute the query built by the
        QueryBuilder and populates the `_cache` attribute with model instances
        created from the response data.
        """

        response_data = self.client.execute(query_builder=self._query_builder)
        if not isinstance(response_data, list):
            raise TypeError(f"Expected list from client.execute in _execute(), got {type(response_data)}")

        self._cache = [self._model_class(**data) for data in response_data]

    def _validate_filters(self, **filters) -> None:
        """
        Validates the filter names against the model's fields.

        Raises the InvalidFilter exception if a filter name is not a valid field on the model.

        Args:
            **filters: Keyword arguments representing the filter criteria.
        """

        for filter_name in filters.keys():
            if filter_name.split("__")[0] not in self._model_class.model_fields.keys():
                raise self.InvalidFilter(f'Invalid filter {filter_name}!')

    def _copy(self) -> 'QSet[_M]':
        """
        Creates a copy of the QSet.

        This method creates a new QSet instance with the same model class, cache,
        and query builder as the original.

        Returns:
            (QSet[_M]): A new QSet instance that is a copy of the original.
        """
        return self.__class__(model_class=self._model_class, cache=self._cache, query_builder=self._query_builder)

    def __iter__(self):
        self._execute()
        return iter(self._cache)

    def __len__(self) -> int:
        self._execute()
        return len(self._cache) if self._cache else 0

    def __getitem__(self, index: int) -> _M:
        self._execute()
        return list(self)[index]

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {list(self)} >'

    def __eq__(self, obj: object) -> bool:
        return all(
            (
                self._model_class == getattr(obj, '_model_class'),
                self._cache == getattr(obj, '_cache'),
            )
        )
