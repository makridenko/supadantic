from typing import TYPE_CHECKING, Any, Dict, List, NoReturn, Type

from typing_extensions import Self


if TYPE_CHECKING:
    from .clients import SupabaseClient
    from .models import BaseSBModel


class QSet:
    '''Lazy database lookup for a set of objects'''

    class InvalidFilter(Exception):
        pass

    class InvalidField(Exception):
        pass

    def __init__(self, model_class: Type['BaseSBModel'], objects: List['BaseSBModel'] | None = None) -> None:
        self._model_class = model_class
        self.objects = objects if objects else []

    @property
    def client(self) -> 'SupabaseClient':
        return self._model_class._get_db_client()

    def update(self, **data) -> int:
        for field in data.keys():
            if field not in self._model_class.model_fields.keys():
                raise self.InvalidField(f'Invalid field {field}!')

        ids = tuple(obj.id for obj in self.objects)
        response_data = self.client.bulk_update(ids=ids, data=data)  # pyright: ignore
        return len(response_data)

    def delete(self) -> int:
        ids = tuple(obj.id for obj in self.objects)
        response_data = self.client.bulk_delete(ids=ids)  # pyright: ignore
        return len(response_data)

    def all(self) -> Self:
        response_data = self.client.select()
        self.objects = list(self._model_class(**data) for data in response_data)
        return self._copy()

    def _select(self, eq: Dict[str, Any] | None = None, neq: Dict[str, Any] | None = None) -> Self:
        response_data = self.client.select(eq=eq, neq=neq)
        objects = list(self._model_class(**data) for data in response_data)
        return self.__class__(model_class=self._model_class, objects=objects)

    def _validate_filters(self, **filters) -> None | NoReturn:
        for filter_name in filters.keys():
            if filter_name not in self._model_class.model_fields.keys():
                raise self.InvalidFilter(f'Invalid filter {filter_name}!')

    def filter(self, **filters) -> Self:
        self._validate_filters(**filters)
        return self._select(eq=filters)

    def exclude(self, **filters) -> Self:
        self._validate_filters(**filters)
        return self._select(neq=filters)

    def get(self, **filters) -> 'BaseSBModel' | NoReturn:
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
        return len(self.objects)

    def first(self) -> 'BaseSBModel | None':
        if self.count():
            return self[0]

    def last(self) -> 'BaseSBModel | None':
        if self.count():
            return self[-1]

    def _copy(self) -> Self:
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
