import enum
from typing import TYPE_CHECKING, Any, Literal


if TYPE_CHECKING:
    from collections.abc import Iterable


class QueryBuilder:
    """
    A class for constructing database queries in a structured way.

    This class provides a fluent interface for building queriess.
    It encapsulates the query building logic, making it easier to construct complex queries
    in a readable and maintainable way.
    """

    class Mode(enum.Enum):
        """
        Enum representing the different query modes.

        The `Mode` enum defines the different types of queries that can be
        built using the `QueryBuilder` class.
        """

        FILTER_MODE = 'FILTER_MODE'
        INSERT_MODE = 'INSERT_MODE'
        UPDATE_MODE = 'UPDATE_MODE'
        DELETE_MODE = 'DELETE_MODE'
        COUNT_MODE = 'COUNT_MODE'

    def __init__(self) -> None:
        self._select_fields: tuple[str, ...] | None = None
        self._equal: tuple[tuple[str, Any], ...] = ()
        self._not_equal: tuple[tuple[str, Any], ...] = ()
        self._less_than_or_equal: tuple[tuple[str, Any], ...] = ()
        self._insert_data: dict[str, Any] | None = None
        self._update_data: dict[str, Any] | None = None
        self._delete_mode: bool = False
        self._count_mode: bool = False

    @property
    def select_fields(self) -> tuple[str, ...] | Literal['*']:
        """
        Gets the selected fields for the query.

        If no specific fields have been selected, this property returns `"*"`,
        which indicates that all fields should be selected.

        Returns:
            (tuple[str, ...] | Literal[*]): A tuple of strings representing the selected fields,
                                            or `"*"` if no fields have been explicitly selected.
        """

        if self._select_fields is None:
            return '*'
        return self._select_fields

    @property
    def equal(self) -> tuple[tuple[str, Any], ...]:
        """
        Gets the equality filters for the query.

        Returns:
            (tuple[tuple[str, Any], ...]): A tuple of tuples, where each inner tuple contains a field name
                                           and its desired value for equality filtering.
        """

        return self._equal

    @property
    def not_equal(self) -> tuple[tuple[str, Any], ...]:
        """
        Gets the non-equality filters for the query.

        Returns:
            (tuple[tuple[str, Any], ...]): A tuple of tuples, where each inner tuple contains a field name and
                                           its desired value for non-equality filtering.
        """

        return self._not_equal

    @property
    def less_than_or_equal(self) -> tuple[tuple[str, Any], ...]:
        """
        Gets the less than or equal filters for the query.

        Returns:
            (tuple[tuple[str, Any], ...]): A tuple of tuples, where each inner tuple contains a field name and
                                           its desired value for non-equality filtering.
        """

        return self._less_than_or_equal

    @property
    def insert_data(self) -> dict[str, Any] | None:
        """
        Gets the data to be inserted in an insert query.

        Returns:
            (dict[str, Any] | None): A dictionary representing the data to be inserted,
                                     or None if no data has been set for insertion.
        """

        return self._insert_data

    @property
    def update_data(self) -> dict[str, Any] | None:
        """
        Gets the data to be updated in an update query.

        Returns:
            (dict[str, Any] | None): A dictionary representing the data to be updated,
                                     or None if no data has been set for updating.
        """
        return self._update_data

    @property
    def delete_mode(self) -> bool:
        """
        Gets the delete mode flag.

        Returns:
            (bool): True if the query is in delete mode, False otherwise.
        """

        return self._delete_mode

    @property
    def count_mode(self) -> bool:
        """
        Gets the count mode flag.

        Returns:
            (bool): True if the query is in count mode, False otherwise.
        """

        return self._count_mode

    @property
    def mode(self) -> 'Mode':
        """
        Determines the query mode based on the current state of the QueryBuilder.

        Returns:
            ('Mode'): The QueryBuilder.Mode enum representing the determined mode.
        """

        if self.delete_mode:
            return self.Mode.DELETE_MODE

        if self.insert_data:
            return self.Mode.INSERT_MODE

        if self.update_data:
            return self.Mode.UPDATE_MODE

        if self.count_mode:
            return self.Mode.COUNT_MODE

        return self.Mode.FILTER_MODE

    def set_select_fields(self, fields: 'Iterable[str]') -> None:
        """
        Sets the selected fields for the query.

        This method appends the provided fields to the existing set of selected
        fields. It converts the input to a tuple.

        Args:
            fields (Iterable[str]): An iterable of strings representing the fields to select.
        """

        if self._select_fields is None:
            self._select_fields = tuple(fields)
        else:
            self._select_fields += tuple(fields)

    def set_equal(self, **kwargs) -> None:
        """
        Sets the equality filters for the query.

        This method accepts keyword arguments representing the equality filters
        and appends them to the existing set of equality filters.

        Args:
            **kwargs: Key-value pairs where keys are field names and values are the desired values for equality.
        """

        self._equal += self._dict_to_tuple(data=kwargs)

    def set_not_equal(self, **kwargs) -> None:
        """
        Sets the non-equality filters for the query.

        This method accepts keyword arguments representing the non-equality filters
        and appends them to the existing set of non-equality filters.

        Args:
            **kwargs: Key-value pairs where keys are field names and values are the values to exclude.
        """

        self._not_equal += self._dict_to_tuple(data=kwargs)

    def set_less_than_or_equal(self, **kwargs) -> None:
        """
        Sets the less than or equal filters for the query.

        This method accepts keyword arguments representing the non-equality filters
        and appends them to the existing set of less than or equal filters.

        Args:
            **kwargs: Key-value pairs where keys are field names and values are the values to exclude.
        """

        self._less_than_or_equal += self._dict_to_tuple(data=kwargs)

    def set_insert_data(self, data: dict[str, Any]) -> None:
        """
        Sets the data to be inserted in an insert query.

        Args:
            data (dict[str, Any]): A dictionary representing the data to be inserted,
                                   where keys are field names and values are the corresponding values.
        """

        self._insert_data = data

    def set_update_data(self, data: dict[str, Any]) -> None:
        """
        Sets the data to be updated in an update query.

        Args:
            data (dict[str, Any]): A dictionary representing the data to be updated,
                                   where keys are field names and values are the new values.
        """

        self._update_data = data

    def set_delete_mode(self, value: bool) -> None:
        """
        Sets the delete mode flag.

        Args:
            value: True to set the query to delete mode, False otherwise.
        """

        self._delete_mode = value

    def set_count_mode(self, value: bool) -> None:
        """
        Sets the count mode flag.

        Args:
            value (bool): True to set the query to count mode, False otherwise.
        """

        self._count_mode = value

    def _dict_to_tuple(self, *, data: dict[str, str]) -> tuple[tuple[str, Any], ...]:
        """
        Converts a dictionary to a tuple of tuples.

        This helper method is used to convert a dictionary of filters to a tuple
        of tuples, which is the format used to store the filters internally.

        Args:
            data (dict[str, str]): The dictionary to convert.

        Returns:
            (tuple[tuple[str, ...], ...]): A tuple of tuples, where each inner tuple
                                           contains a key-value pair from the input dictionary.
        """

        return tuple((key, value) for key, value in data.items())
