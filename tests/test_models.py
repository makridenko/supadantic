from typing import TYPE_CHECKING, Type

from supadantic.q_set import QSet


if TYPE_CHECKING:
    from tests.fixtures.model import ModelMock


class TestBaseSBModel:
    class TestSave:
        def test_create(self, model_mock: Type['ModelMock']):
            # Prepare data
            test_entity = model_mock(
                name='test_name',
                some_optional_list=['foo', 'bar'],
                some_optional_tuple=('foo', 'bar'),
            )

            # Execution
            saved_entity = test_entity.save()

            # Testing
            assert saved_entity.id == 1
            assert saved_entity.name == 'test_name'
            assert saved_entity.some_optional_list == ['foo', 'bar']

        def test_update(self, model_mock: Type['ModelMock']):
            # Prepare data
            model_mock(name='test_name', some_optional_list=['foo', 'bar']).save()
            model_mock(name='test_name_2', some_optional_list=['bar', 'foo']).save()

            test_entity = model_mock(
                id=2,
                name='2_test_name',
                some_optional_list=['bar'],
                some_optional_tuple=('foo',),
            )

            # Execution
            updated_entity = test_entity.save()

            # Testing
            assert updated_entity.id == 2
            assert updated_entity.name == '2_test_name'
            assert updated_entity.some_optional_list == ['bar']
            assert updated_entity.some_optional_tuple == ('foo',)

    def test_objects(self, model_mock: Type['ModelMock']):
        assert isinstance(model_mock.objects, QSet)  # pyright: ignore
