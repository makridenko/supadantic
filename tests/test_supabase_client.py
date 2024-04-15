from unittest.mock import Mock, PropertyMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from src.supabase_client import SupabaseClient


class TestSupabaseClient:
    @pytest.fixture(autouse=True)
    def mock_create_client(self, mocker: MockerFixture) -> MagicMock:
        return mocker.patch('src.supabase_client.create_client')

    @pytest.fixture
    def supabase_client(self) -> SupabaseClient:
        return SupabaseClient(table_name='table_name')

    def test_insert(self, supabase_client: SupabaseClient):
        # Prepare data
        mock_supabase_query = Mock()

        supabase_client.query = mock_supabase_query

        test_data = {'test': 'data'}

        mock_response = Mock()
        type(mock_response).data = PropertyMock(return_value=[test_data])

        mock_supabase_query.insert.return_value.execute.return_value = mock_response

        # Execution
        response = supabase_client.insert(test_data)

        # Testing
        mock_supabase_query.insert.assert_called_once_with(test_data)
        assert response == test_data

    def test_update(self, supabase_client: SupabaseClient):
        # Prepare data
        mock_supabase_query = Mock()

        supabase_client.query = mock_supabase_query

        test_data = {'test': 'data'}
        test_data_with_id = {'id': 1, 'test': 'data'}

        mock_response = Mock()
        type(mock_response).data = PropertyMock(return_value=[test_data_with_id])

        mock_supabase_query.update.return_value.eq.return_value.execute.return_value = mock_response

        # Execution
        response = supabase_client.update(id=1, data=test_data)

        # Testing
        mock_supabase_query.update.assert_called_once_with(test_data)
        mock_supabase_query.update.return_value.eq.assert_called_once_with('id', 1)

        assert response == test_data_with_id

    def test_select(self, supabase_client: SupabaseClient):
        # Prepare data
        mock_supabase_query = Mock()

        supabase_client.query = mock_supabase_query

        test_filters = {'column1': 'value1', 'column2': 'value2'}

        mock_response = Mock()
        type(mock_response).data = PropertyMock(return_value=[{'id': 1}, {'id': 2}])

        mock_supabase_query.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        # Execution
        result = supabase_client.select(eq=test_filters)

        # Testing
        mock_supabase_query.select.assert_called_with('*')

        mock_supabase_query.select.return_value.eq.assert_called_with('column1', 'value1')
        mock_supabase_query.select.return_value.eq.return_value.eq.assert_called_with('column2', 'value2')

        # Assert the result
        assert result == [{'id': 1}, {'id': 2}]

    def test_bulk_update(self, supabase_client: SupabaseClient):
        # Prepare data
        mock_supabase_query = Mock()

        supabase_client.query = mock_supabase_query

        test_data = {'name': 'new_name'}
        test_ids = [1, 2, 3]
        test_response = [
            {'id': 1, 'name': 'new_name'},
            {'id': 2, 'name': 'new_name'},
            {'id': 3, 'name': 'new_name'},
        ]

        mock_response = Mock()
        type(mock_response).data = PropertyMock(return_value=test_response)

        mock_supabase_query.update.return_value.in_.return_value.execute.return_value = mock_response

        # Execution
        result = supabase_client.bulk_update(ids=test_ids, data=test_data)

        # Testing
        mock_supabase_query.update.assert_called_once_with(test_data)
        mock_supabase_query.update.return_value.in_.assert_called_once_with('id', test_ids)

        assert result == test_response
