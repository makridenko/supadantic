from typing import TYPE_CHECKING

import pytest

from supadantic.q_set import QSet


if TYPE_CHECKING:
    from tests.fixtures.model import ModelMock


class TestQSet:
    @pytest.fixture(autouse=True, scope='function')
    def fill_cache_db_and_clear(self, model_mock: type['ModelMock']) -> None:
        names = ('test_name', 'unique_name', 'test_name', 'new_name')
        for name in names:
            model_mock(name=name).save()

    def test_all(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[
                model_mock(id=1, name='test_name'),
                model_mock(id=2, name='unique_name'),
                model_mock(id=3, name='test_name'),
                model_mock(id=4, name='new_name'),
            ],
        )

        # Execution
        actual_q_set = model_mock.objects.all()
        actual_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set

    def test_include_filter(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[
                model_mock(id=1, name='test_name'),
                model_mock(id=3, name='test_name'),
            ],
        )

        # Execution
        actual_q_set = model_mock.objects.filter(id__in=[1, 3])
        actual_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set

    def test_filter(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[
                model_mock(id=1, name='test_name'),
                model_mock(id=3, name='test_name'),
            ],
        )

        # Execution
        actual_q_set = model_mock.objects.filter(name='test_name', id__lte=3)
        actual_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set

    def test_greater_than_filter(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[
                model_mock(id=2, name="unique_name"),
                model_mock(id=3, name="test_name"),
                model_mock(id=4, name="new_name"),
            ],
        )

        # Execution
        actual_q_set = model_mock.objects.filter(id__gt=1)
        actual_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set

    def test_less_than_filter(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[model_mock(id=1, name="test_name"), model_mock(id=2, name="unique_name")],
        )

        # Execution
        actual_q_set = model_mock.objects.filter(id__lt=3)
        actual_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set

    def test_greater_than_or_equal_filter(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[
                model_mock(id=2, name="unique_name"),
                model_mock(id=3, name="test_name"),
                model_mock(id=4, name="new_name"),
            ],
        )

        # Execution
        actual_q_set = model_mock.objects.filter(id__gte=2)
        actual_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set

    def test_exclude(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[
                model_mock(id=2, name='unique_name'),
                model_mock(id=4, name='new_name'),
            ],
        )

        # Execution
        actual_q_set = model_mock.objects.exclude(name='test_name')
        actual_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set

    def test_exclude_less_than_or_equal(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[
                model_mock(id=3, name='test_name'),
                model_mock(id=4, name='new_name'),
            ],
        )

        # Execution
        actual_q_set = model_mock.objects.exclude(id__lte=2)
        actual_q_set._execute()

        filtered_q_set = model_mock.objects.filter(id__gt=2)
        filtered_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set
        assert actual_q_set == filtered_q_set

    def test_exclude_greater_than(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[
                model_mock(id=1, name='test_name'),
                model_mock(id=2, name='unique_name'),
            ],
        )

        # Execution
        actual_q_set = model_mock.objects.exclude(id__gt=2)
        actual_q_set._execute()

        filtered_q_set = model_mock.objects.filter(id__lte=2)
        filtered_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set
        assert actual_q_set == filtered_q_set

    def test_exclude_less_than(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[model_mock(id=3, name='test_name'), model_mock(id=4, name='new_name')],
        )

        # Execution
        actual_q_set = model_mock.objects.exclude(id__lt=3)
        actual_q_set._execute()

        filtered_q_set = model_mock.objects.filter(id__gte=3)
        filtered_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set
        assert actual_q_set == filtered_q_set

    def test_exclude_greater_than_or_equal(self, model_mock: type['ModelMock']):
        # Prepare data
        expected_q_set = QSet(
            model_class=model_mock,
            cache=[model_mock(id=1, name='test_name'), model_mock(id=2, name='unique_name')],
        )

        # Execution
        actual_q_set = model_mock.objects.exclude(id__gte=3)
        actual_q_set._execute()

        filtered_q_set = model_mock.objects.filter(id__lt=3)
        filtered_q_set._execute()

        # Testing
        assert actual_q_set == expected_q_set
        assert actual_q_set == filtered_q_set

    def test_filters_with_wrong_field(self, model_mock: type['ModelMock']):
        with pytest.raises(QSet.InvalidFilter, match='Invalid filter'):
            model_mock.objects.filter(foo='bar')

    def test_get(self, model_mock: type['ModelMock']):
        assert model_mock.objects.get(id=1) == model_mock(id=1, name='test_name')

        with pytest.raises(model_mock.DoesNotExist, match='does not exist!'):
            model_mock.objects.get(id=5)

        with pytest.raises(model_mock.MultipleObjectsReturned, match='returned more than 1'):
            model_mock.objects.get(name='test_name')

    def test_count(self, model_mock: type['ModelMock']):
        model_mock.objects.count() == 4
        model_mock.objects.filter(name='unique_name').count() == 1
        model_mock.objects.filter(name='foo').count() == 0

    def test_first(self, model_mock: type['ModelMock']):
        assert model_mock.objects.all().first() == model_mock(id=1, name='test_name')
        assert model_mock.objects.filter(name='foo').first() is None

    def test_last(self, model_mock: type['ModelMock']):
        assert model_mock.objects.all().last() == model_mock(id=4, name='new_name')
        assert model_mock.objects.filter(name='foo').last() is None

    def test_update(self, model_mock: type['ModelMock']):
        assert model_mock.objects.filter(name='test_name').update(name='_test_name') == 2

    def test_update_with_invalid_field(self, model_mock: type['ModelMock']):
        with pytest.raises(
            QSet.InvalidField,
            match="Field 'foo' is not defined for ModelMock model."
            "Available fields are: id, name, age, some_optional_list, some_optional_tuple",
        ):
            model_mock.objects.filter(name='name').update(foo='bar')

    def test_create(self, model_mock: type['ModelMock']):
        assert model_mock.objects.create(name='new_name') == model_mock(id=5, name='new_name')

    def test_create_with_invalid_field(self, model_mock: type['ModelMock']):
        with pytest.raises(
            QSet.InvalidField,
            match="Field 'foo' is not defined for ModelMock model."
            "Available fields are: id, name, age, some_optional_list, some_optional_tuple",
        ):
            model_mock.objects.create(foo='bar')

    def test_delete(self, model_mock: type['ModelMock']):
        assert model_mock.objects.all().delete() == 4
        assert not model_mock.objects.all()

    def test_copy(self, model_mock: type['ModelMock']):
        assert QSet(
            model_class=model_mock,
            cache=[
                model_mock(id=1, name='first'),
                model_mock(id=2, name='second'),
            ],
        )._copy() == QSet(
            model_class=model_mock,
            cache=[
                model_mock(id=1, name='first'),
                model_mock(id=2, name='second'),
            ],
        )

    def test_get_or_create(self, model_mock: type['ModelMock']):
        expected_obj = model_mock(name='test', age=21).save()
        assert QSet(model_class=model_mock).get_or_create(name='test', defaults={'age': 23}) == (expected_obj, False)

        created_obj, result = QSet(model_class=model_mock).get_or_create(name='create', defaults={'age': 23})
        assert result is True
        assert created_obj.id is not None
        assert created_obj.name == 'create'
        assert created_obj.age == 23

    def test_exists(self, model_mock: type['ModelMock']):
        model_mock.objects.all().delete()
        assert not QSet(model_class=model_mock).exists()

        model_mock(name='test', age=21).save()

        assert QSet(model_class=model_mock).exists()
        assert QSet(model_class=model_mock).filter(name='test').exists()
        assert QSet(model_class=model_mock).filter(age=21).exists()
        assert not QSet(model_class=model_mock).filter(name='test', age=12).exists()
        assert not QSet(model_class=model_mock).filter(name='foo', age=21).exists()

    def test_order_by(self, model_mock: type['ModelMock']):
        # Arrange
        model_mock.objects.all().delete()
        assert not QSet(model_class=model_mock).exists()

        model_mock(name='test', age=2).save()
        model_mock(name='test', age=3).save()
        model_mock(name='test', age=1).save()
        model_mock(name='test', age=4).save()

        # Assert
        assert (
            QSet(model_class=model_mock).order_by('age').first() == QSet(model_class=model_mock).filter(age=1).first()
        )
        assert QSet(model_class=model_mock).order_by('age').last() == QSet(model_class=model_mock).filter(age=4).last()

        assert (
            QSet(model_class=model_mock).order_by('-age').first() == QSet(model_class=model_mock).filter(age=4).first()
        )
        assert (
            QSet(model_class=model_mock).order_by('-age').last() == QSet(model_class=model_mock).filter(age=1).first()
        )

        with pytest.raises(QSet.InvalidField, match="Invalid field: 'test'!"):
            QSet(model_class=model_mock).order_by('test')
