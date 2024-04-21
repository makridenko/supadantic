from typing import Type
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from supadantic.base import BaseDBEntity


class TestBaseDBEntity:
    @pytest.fixture
    def entity(self, mocker) -> Type[BaseDBEntity]:
        mocker.patch('supadantic.base.BaseDBEntity.__abstractmethods__', set())
        return BaseDBEntity

    @pytest.fixture
    def test_supabase_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def mock_get_db_client(
        self,
        entity: Type[BaseDBEntity],
        test_supabase_client: MagicMock,
        mocker: MockerFixture,
    ) -> MagicMock:
        return mocker.patch.object(entity, '_get_db_client', return_value=test_supabase_client)

    def test_get_list(
        self,
        entity: Type[BaseDBEntity],
        test_supabase_client: MagicMock,
        mock_get_db_client: MagicMock,
        mocker: MockerFixture,
    ):
        # Prepare data
        test_data = [{'id': 1}, {'id': 2}]
        mock_client_select = mocker.patch.object(test_supabase_client, 'select', return_value=test_data)

        # Execution
        actual = BaseDBEntity.get_list(eq={'test': 'filters'})

        # Testing
        mock_get_db_client.assert_called_once()
        mock_client_select.assert_called_once_with(eq={'test': 'filters'})

        expected = [entity(**data) for data in test_data]

        assert actual == expected

    class TestSave:
        @pytest.fixture
        def mock_model_dump(
            self,
            entity: Type[BaseDBEntity],
            mocker: MockerFixture,
        ) -> MagicMock:
            return mocker.patch.object(entity, 'model_dump', return_value={'test': 'data'})

        @pytest.fixture
        def mock_db_client_insert(
            self,
            test_supabase_client: MagicMock,
            mocker: MockerFixture,
        ) -> MagicMock:
            return mocker.patch.object(test_supabase_client, 'insert', return_value={'id': 1})

        @pytest.fixture
        def mock_db_client_update(
            self,
            test_supabase_client: MagicMock,
            mocker: MockerFixture,
        ) -> MagicMock:
            return mocker.patch.object(test_supabase_client, 'update', return_value={'id': 1})

        def test_create(
            self,
            entity: Type[BaseDBEntity],
            mock_get_db_client: MagicMock,
            mock_model_dump: MagicMock,
            mock_db_client_update: MagicMock,
            mock_db_client_insert: MagicMock,
        ):
            # Prepare data
            test_entity = entity()

            # Execution
            updated_entity = test_entity.save()

            # Testing
            mock_get_db_client.assert_called_once()
            mock_model_dump.assert_called_once_with(exclude={'id'})
            mock_db_client_update.assert_not_called()
            mock_db_client_insert.assert_called_once_with({'test': 'data'})

            assert updated_entity.id == 1

        def test_update(
            self,
            entity: Type[BaseDBEntity],
            mock_get_db_client: MagicMock,
            mock_model_dump: MagicMock,
            mock_db_client_update: MagicMock,
            mock_db_client_insert: MagicMock,
        ):
            # Prepare data
            test_entity = entity(id=2)

            # Execution
            updated_entity = test_entity.save()

            # Testing
            mock_get_db_client.assert_called_once()
            mock_model_dump.assert_called_once_with(exclude={'id'})
            mock_db_client_update.assert_called_once_with(id=2, data={'test': 'data'})
            mock_db_client_insert.assert_not_called()

            assert updated_entity.id == 1

        class TestGet:
            def test(
                self,
                entity: Type[BaseDBEntity],
                mocker: MockerFixture,
            ):
                # Prepare data
                mocker.patch.object(BaseDBEntity, 'get_list', return_value=[entity(id=1)])

                # Execution
                actual_entity = BaseDBEntity.get(eq={'id': 1})

                # Testing
                assert actual_entity.id == 1

            def test_with_does_not_exist(
                self,
                mocker: MockerFixture,
            ):
                # Prepare data
                mocker.patch.object(BaseDBEntity, 'get_list', return_value=[])

                # Execution
                with pytest.raises(BaseDBEntity.DoesNotExist):
                    BaseDBEntity.get(eq={'id': 1})

            def test_with_multiple_objects_returned(
                self,
                entity: Type[MagicMock],
                mocker: MockerFixture,
            ):
                # Prepare data
                mocker.patch.object(BaseDBEntity, 'get_list', return_value=[entity(id=1), entity(id=1)])

                # Execution
                with pytest.raises(BaseDBEntity.MultipleObjectsReturned):
                    BaseDBEntity.get(eq={'id': 1})

        def test_bulk_update(
            self,
            entity: Type[BaseDBEntity],
            test_supabase_client: MagicMock,
            mock_get_db_client: MagicMock,
            mocker: MockerFixture,
        ):
            # Prepare data
            test_data = {'name': 'new_name'}
            test_ids = [1, 2, 3]
            mock_db_client_bulk_update = mocker.patch.object(
                test_supabase_client, 'bulk_update', return_value=[{'id': _id} for _id in test_ids]
            )

            # Execution
            entity.bulk_update(ids=test_ids, data=test_data)

            # Testing
            mock_get_db_client.assert_called_once()
            mock_db_client_bulk_update.assert_called_once_with(ids=test_ids, data=test_data)

        def test_delete(
            self,
            entity: Type[BaseDBEntity],
            test_supabase_client: MagicMock,
            mock_get_db_client: MagicMock,
            mocker: MockerFixture,
        ):
            # Prepare data
            test_entity_with_id = entity(id=1)
            test_entity_without_id = entity()
            mock_db_client_delete = mocker.patch.object(test_supabase_client, 'delete')

            # Execution
            test_entity_with_id.delete()
            test_entity_without_id.delete()

            # Testing
            mock_get_db_client.assert_called_once()
            mock_db_client_delete.assert_called_once_with(id=1)
