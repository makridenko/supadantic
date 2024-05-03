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

    class TestFilters:
        def test_filter(self):
            # Prepare data
            expected_objects = [
                ModelMock(id=1, name='test_name'),
                ModelMock(id=3, name='test_name'),
            ]

            # Testing
            assert QSet(model_class=ModelMock).filter(name='test_name') == QSet(
                model_class=ModelMock,
                objects=expected_objects,  # pyright: ignore
            )

        def test_exclude(self):
            # Prepare data
            expected_objects = [
                ModelMock(id=2, name='unique_name'),
                ModelMock(id=4, name='new_name'),
            ]

            # Testing
            assert QSet(model_class=ModelMock).exclude(name='test_name') == QSet(
                model_class=ModelMock,
                objects=expected_objects,  # pyright: ignore
            )

        def test_filters_with_wrong_field(self):
            with pytest.raises(QSet.InvalidFilter, match='Invalid filter'):
                QSet(model_class=ModelMock).filter(foo='bar')

    def test_get(self):
        assert QSet(model_class=ModelMock).get(id=1) == ModelMock(id=1, name='test_name')

        with pytest.raises(ModelMock.DoesNotExist, match='does not exist!'):
            QSet(model_class=ModelMock).get(id=5)

        with pytest.raises(ModelMock.MultipleObjectsReturned, match='returned more than 1'):
            QSet(model_class=ModelMock).get(name='test_name')

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
