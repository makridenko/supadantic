import pytest

from .test_classes.models import ModelMock


class TestBaseSBModel:
    def test_all(self):
        result_qs = ModelMock.all()

        assert result_qs.objects == [
            ModelMock(id=1, name='test_name'),
            ModelMock(id=2, name='unique_name'),
            ModelMock(id=3, name='test_name'),
            ModelMock(id=4, name='new_name'),
        ]

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
        expected_data = [
            ModelMock(id=1, name='test_name'),
            ModelMock(id=2, name='unique_name'),
            ModelMock(id=3, name='test_name'),
            ModelMock(id=4, name='new_name'),
        ]
        if with_eq:
            filters['eq'] = {'name': 'test_name'}
            expected_data.remove(ModelMock(id=2, name='unique_name'))
            expected_data.remove(ModelMock(id=4, name='new_name'))

        if with_neq:
            filters['neq'] = {'id': 1}
            expected_data.remove(ModelMock(id=1, name='test_name'))

        # Testing
        actual_qs = ModelMock.filter(**filters)
        assert actual_qs.objects == expected_data

    class TestSave:
        def test_create(self):
            # Prepare data
            test_entity = ModelMock(name='test_name')

            # Execution
            updated_entity = test_entity.save()

            # Testing
            assert updated_entity.id == 1
            assert updated_entity.name == 'test_name'

        def test_update(self):
            # Prepare data
            test_entity = ModelMock(id=2, name='test_name')

            # Execution
            updated_entity = test_entity.save()

            # Testing
            assert updated_entity.id == 2
            assert updated_entity.name == 'test_name'

        class TestGet:
            def test(self):
                # Execution
                actual_entity = ModelMock.get(eq={'name': 'unique_name'})

                # Testing
                assert actual_entity.id == 2
                assert actual_entity.name == 'unique_name'

            def test_with_does_not_exist(self):
                with pytest.raises(ModelMock.DoesNotExist):
                    ModelMock.get(eq={'id': 5})

            def test_with_multiple_objects_returned(self):
                # Execution
                with pytest.raises(ModelMock.MultipleObjectsReturned):
                    ModelMock.get(eq={'name': 'test_name'})
