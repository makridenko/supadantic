import pytest

from supadantic.queryset import QuerySet

from .test_classes.entity import EntityMock


class TestQuerySet:
    def test_update(self):
        assert (
            QuerySet(
                model_class=EntityMock,
                objects=[
                    EntityMock(id=1, name='first'),
                    EntityMock(id=2, name='second'),
                ],
            ).update(data={'name': 'test_name'})
            == 2
        )

    def test_delete(self):
        assert (
            QuerySet(
                model_class=EntityMock,
                objects=[
                    EntityMock(id=1, name='first'),
                    EntityMock(id=2, name='second'),
                ],
            ).delete()
            == 2
        )

    def test_all(self):
        assert QuerySet(model_class=EntityMock).all() == QuerySet(
            model_class=EntityMock,
            objects=[
                EntityMock(id=1, name='test_name'),
                EntityMock(id=2, name='unique_name'),
                EntityMock(id=3, name='test_name'),
                EntityMock(id=4, name='new_name'),
            ],
        )

    @pytest.mark.parametrize(
        'with_eq,with_neq',
        (
            (False, False),
            (False, True),
            (True, False),
            (True, True),
        ),
    )
    def test_filter(self, with_eq: bool, with_neq: bool):
        # Prepare data
        filters = {}
        expected_objects = [
            EntityMock(id=1, name='test_name'),
            EntityMock(id=2, name='unique_name'),
            EntityMock(id=3, name='test_name'),
            EntityMock(id=4, name='new_name'),
        ]
        if with_eq:
            filters['eq'] = {'name': 'test_name'}
            expected_objects.remove(EntityMock(id=2, name='unique_name'))
            expected_objects.remove(EntityMock(id=4, name='new_name'))

        if with_neq:
            filters['neq'] = {'id': 1}
            expected_objects.remove(EntityMock(id=1, name='test_name'))

        # Testing
        assert QuerySet(model_class=EntityMock).filter(**filters) == QuerySet(
            model_class=EntityMock,
            objects=expected_objects,
        )

    def test_count(self):
        assert (
            QuerySet(
                model_class=EntityMock,
                objects=[
                    EntityMock(id=1, name='first'),
                    EntityMock(id=2, name='second'),
                ],
            ).count()
            == 2
        )

    def test_first(self):
        assert QuerySet(
            model_class=EntityMock,
            objects=[
                EntityMock(id=1, name='first'),
                EntityMock(id=2, name='second'),
            ],
        ).first() == EntityMock(id=1, name='first')

    def test_last(self):
        assert QuerySet(
            model_class=EntityMock,
            objects=[
                EntityMock(id=1, name='first'),
                EntityMock(id=2, name='second'),
            ],
        ).last() == EntityMock(id=2, name='second')

    def test_copy(self):
        assert QuerySet(
            model_class=EntityMock,
            objects=[
                EntityMock(id=1, name='first'),
                EntityMock(id=2, name='second'),
            ],
        )._copy() == QuerySet(
            model_class=EntityMock,
            objects=[
                EntityMock(id=1, name='first'),
                EntityMock(id=2, name='second'),
            ],
        )
