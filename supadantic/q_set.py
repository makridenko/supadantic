from typing import TYPE_CHECKING, Dict, List, NoReturn, Type

from typing_extensions import Self


if TYPE_CHECKING:
    from .clients import SupabaseClient
    from .models import BaseSBModel


class QSet:
    '''Lazy database lookup for a set of objects'''

    def __init__(self, model_class: Type['BaseSBModel'], objects: List['BaseSBModel'] | None = None) -> None:
        self._model_class = model_class
        self.objects = objects if objects else []

    @property
    def client(self) -> 'SupabaseClient':
        return self._model_class._get_db_client()

    def update(self, data: Dict) -> int:
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

    def filter(self, *, eq: Dict | None = None, neq: Dict | None = None) -> Self:
        _filters = {}

        if eq:
            _filters['eq'] = eq

        if neq:
            _filters['neq'] = neq

        response_data = self.client.select(**_filters)
        objects = list(self._model_class(**data) for data in response_data)
        return self.__class__(model_class=self._model_class, objects=objects)

    def get(self, *, eq: Dict | None = None, neq: Dict | None = None) -> 'BaseSBModel' | NoReturn:
        result_qs = self.filter(eq=eq, neq=neq)
        _filters_str = f'eq={eq}, neq={neq}'
        if not result_qs:
            raise self._model_class.DoesNotExist(
                f'{self._model_class.__name__} object with {_filters_str} does not exist!'
            )

        if result_qs.count() > 1:
            raise self._model_class.MultipleObjectsReturned(
                f'For {_filters_str} returned more than 1 {self._model_class.__name__} objects!'
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
