from typing import TYPE_CHECKING, Dict, List, Type

from typing_extensions import Self


if TYPE_CHECKING:
    from .models import BaseSBModel


class QSet:
    '''Lazy database lookup for a set of objects'''

    def __init__(self, model_class: Type['BaseSBModel'], objects: List['BaseSBModel'] | None = None) -> None:
        self._model_class = model_class
        self.client = self._model_class._get_db_client()
        self.objects = objects if objects else []

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
        if not isinstance(obj, QSet):
            return False

        return all(
            (
                self._model_class == obj._model_class,
                self.objects == obj.objects,
            )
        )
