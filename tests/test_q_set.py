import pytest

from supadantic.q_set import QSet

from .test_classes.models import ModelMock


class TestQSet:
    def test_update(self):
        assert (
            QSet(
                model_class=ModelMock,
                objects=[
                    ModelMock(id=1, name='first'),
                    ModelMock(id=2, name='second'),
                ],
            ).update(data={'name': 'test_name'})
            == 2
        )

    def test_delete(self):
        assert (
            QSet(
                model_class=ModelMock,
                objects=[
                    ModelMock(id=1, name='first'),
                    ModelMock(id=2, name='second'),
                ],
            ).delete()
            == 2
        )

    def test_all(self):
        assert QSet(model_class=ModelMock).all() == QSet(
            model_class=ModelMock,
            objects=[
                ModelMock(id=1, name='test_name'),
                ModelMock(id=2, name='unique_name'),
                ModelMock(id=3, name='test_name'),
                ModelMock(id=4, name='new_name'),
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
            ModelMock(id=1, name='test_name'),
            ModelMock(id=2, name='unique_name'),
            ModelMock(id=3, name='test_name'),
            ModelMock(id=4, name='new_name'),
        ]

        if with_eq:
            filters['eq'] = {'name': 'test_name'}
            expected_objects.remove(ModelMock(id=2, name='unique_name'))
            expected_objects.remove(ModelMock(id=4, name='new_name'))

        if with_neq:
            filters['neq'] = {'id': 1}
            expected_objects.remove(ModelMock(id=1, name='test_name'))

        # Testing
        assert QSet(model_class=ModelMock).filter(**filters) == QSet(
            model_class=ModelMock,
            objects=expected_objects,  # pyright: ignore
        )

    def test_get(self):
        assert QSet(model_class=ModelMock).get(eq={'id': 1}) == ModelMock(id=1, name='test_name')

        with pytest.raises(ModelMock.DoesNotExist, match='does not exist!'):
            QSet(model_class=ModelMock).get(eq={'id': 5})

        with pytest.raises(ModelMock.MultipleObjectsReturned, match='returned more than 1'):
            QSet(model_class=ModelMock).get(eq={'name': 'test_name'})

    def test_count(self):
        assert (
            QSet(
                model_class=ModelMock,
                objects=[
                    ModelMock(id=1, name='first'),
                    ModelMock(id=2, name='second'),
                ],
            ).count()
            == 2
        )

    def test_first(self):
        assert QSet(
            model_class=ModelMock,
            objects=[
                ModelMock(id=1, name='first'),
                ModelMock(id=2, name='second'),
            ],
        ).first() == ModelMock(id=1, name='first')

    def test_last(self):
        assert QSet(
            model_class=ModelMock,
            objects=[
                ModelMock(id=1, name='first'),
                ModelMock(id=2, name='second'),
            ],
        ).last() == ModelMock(id=2, name='second')

    def test_copy(self):
        assert QSet(
            model_class=ModelMock,
            objects=[
                ModelMock(id=1, name='first'),
                ModelMock(id=2, name='second'),
            ],
        )._copy() == QSet(
            model_class=ModelMock,
            objects=[
                ModelMock(id=1, name='first'),
                ModelMock(id=2, name='second'),
            ],
        )
