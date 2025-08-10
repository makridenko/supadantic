from typing import TYPE_CHECKING

from supadantic.q_set import QSet


if TYPE_CHECKING:
    from tests.fixtures.model import ModelMock


class TestBaseSBModel:
    def test_create(self, model_mock: type['ModelMock']):
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

    def test_update(self, model_mock: type['ModelMock']):
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

    def test_objects(self, model_mock: type['ModelMock']):
        assert isinstance(model_mock.objects, QSet)

    def test_refresh_from_db(self, model_mock: type['ModelMock']):
        original = model_mock(
            name='initial',
            some_optional_list=['old', 'data'],
            some_optional_tuple=('old', 'data'),
        ).save()

        model_mock.objects.filter(id=original.id).update(
            name='updated',
            some_optional_tuple=('updated', 'data'),
        )

        assert original.id == original.id
        assert original.name == 'initial'
        assert original.some_optional_list == ['old', 'data']
        assert original.some_optional_tuple == ('old', 'data')

        original.refresh_from_db()

        assert original.id == original.id
        assert original.name == 'updated'
        assert original.some_optional_list == ['old', 'data']
        assert original.some_optional_tuple == ('updated', 'data')


class TestBaseSBModelCustomSchema:
    def test_db_client_with_custom_schema(self, model_mock_custom_schema: type['ModelMock']):
        # Prepare data
        test_entity = model_mock_custom_schema(name='test_name')

        # Execution
        db_client = test_entity._get_db_client()

        # Testing
        assert db_client.schema == 'custom_schema'
