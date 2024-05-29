from typing import TYPE_CHECKING, Type

import pytest

from supadantic.q_set import QSet


if TYPE_CHECKING:
    from tests.fixtures.model import ModelMock


class TestQSet:
    @pytest.fixture(autouse=True, scope='function')
    def _fill_cache_db_and_clear(self, model_mock: Type['ModelMock']) -> None:
        names = ('test_name', 'unique_name', 'test_name', 'new_name')
        for name in names:
            model_mock(name=name).save()

    class TestUpdate:
        def test(self, model_mock: Type['ModelMock']):
            assert model_mock.objects.filter(name='test_name').update(name='_test_name') == 2  # pyright: ignore

        def test_with_invalid_field(self, model_mock: Type['ModelMock']):
            with pytest.raises(QSet.InvalidField, match='Invalid field'):
                model_mock.objects.filter(name='name').update(foo='bar')  # pyright: ignore

    def test_delete(self, model_mock: Type['ModelMock']):
        assert model_mock.objects.all().delete() == 4  # pyright: ignore
        assert not model_mock.objects.all()  # pyright: ignore

    def test_all(self, model_mock: Type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            objects=[
                model_mock(id=1, name='test_name'),
                model_mock(id=2, name='unique_name'),
                model_mock(id=3, name='test_name'),
                model_mock(id=4, name='new_name'),
            ],
        )

        # Execution
        actual_q_set = model_mock.objects.all()  # pyright: ignore

        # Testing
        assert actual_q_set == expected_q_set

    class TestFilters:
        def test_filter(self, model_mock: Type['ModelMock']):
            # Prepare data
            expected_q_set = QSet(
                model_class=model_mock,
                objects=[
                    model_mock(id=1, name='test_name'),
                    model_mock(id=3, name='test_name'),
                ],
            )

            # Execution
            actual_q_set = model_mock.objects.filter(name='test_name')  # pyright: ignore

            # Testing
            assert actual_q_set == expected_q_set

        def test_exclude(self, model_mock: Type['ModelMock']):
            # Prepare data
            expected_q_set = QSet(
                model_class=model_mock,
                objects=[
                    model_mock(id=2, name='unique_name'),
                    model_mock(id=4, name='new_name'),
                ],
            )

            # Execution
            actual_q_set = model_mock.objects.exclude(name='test_name')  # pyright: ignore

            # Testing
            assert actual_q_set == expected_q_set

        def test_filters_with_wrong_field(self, model_mock: Type['ModelMock']):
            with pytest.raises(QSet.InvalidFilter, match='Invalid filter'):
                model_mock.objects.filter(foo='bar')  # pyright: ignore

    def test_get(self, model_mock: Type['ModelMock']):
        assert model_mock.objects.get(id=1) == model_mock(id=1, name='test_name')  # pyright: ignore

        with pytest.raises(model_mock.DoesNotExist, match='does not exist!'):
            model_mock.objects.get(id=5)  # pyright: ignore

        with pytest.raises(model_mock.MultipleObjectsReturned, match='returned more than 1'):
            model_mock.objects.get(name='test_name')  # pyright: ignore

    def test_count(self, model_mock: Type['ModelMock']):
        model_mock.objects.count() == 4  # pyright: ignore

    def test_first(self, model_mock: Type['ModelMock']):
        assert model_mock.objects.all().first() == model_mock(id=1, name='test_name')  # pyright: ignore

    def test_last(self, model_mock: Type['ModelMock']):
        assert model_mock.objects.all().last() == model_mock(id=4, name='new_name')  # pyright: ignore

    def test_copy(self, model_mock: Type['ModelMock']):
        assert QSet(
            model_class=model_mock,
            objects=[
                model_mock(id=1, name='first'),
                model_mock(id=2, name='second'),
            ],
        )._copy() == QSet(
            model_class=model_mock,
            objects=[
                model_mock(id=1, name='first'),
                model_mock(id=2, name='second'),
            ],
        )
