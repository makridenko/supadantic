from supadantic.q_set import QSet

from .test_classes.models import ModelMock


class TestBaseSBModel:
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

    def test_objects(self):
        assert ModelMock.objects == QSet(model_class=ModelMock)
