from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock

import pytest

from supadantic.clients import SupabaseClient
from supadantic.query_builder import QueryBuilder


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


class TestSupabaseClient:
    @pytest.fixture(autouse=True)
    def mock_create_client(self, mocker: 'MockerFixture') -> MagicMock:
        return mocker.patch('supadantic.clients.supabase.create_client')

    @pytest.fixture
    def supabase_client(self) -> SupabaseClient:
        return SupabaseClient(table_name='table_name')

    def test_delete(self, supabase_client: SupabaseClient):
        # Prepare data
        mock_supabase_query = Mock()
        mock_supabase_query.delete.return_value.eq.return_value.neq.return_value.execute.return_value.data = [
            {'test': 'data'}
        ]
        supabase_client.query = mock_supabase_query

        query_builder = QueryBuilder()
        query_builder.equal = {'id': 1}  # type: ignore
        query_builder.not_equal = {'title': 'test'}  # type: ignore
        query_builder.delete_mode = True

        # Execution
        result = supabase_client.execute(query_builder=query_builder)

        # Testing
        mock_supabase_query.delete.assert_called_once()
        mock_supabase_query.delete.return_value.eq.assert_called_once_with('id', 1)
        mock_supabase_query.delete.return_value.eq.return_value.neq.assert_called_once_with('title', 'test')
        mock_supabase_query.delete.return_value.eq.return_value.neq.return_value.execute.assert_called_once()

        assert result == [{'test': 'data'}]

    def test_insert(self, supabase_client: SupabaseClient):
        # Prepare data
        mock_supabase_query = Mock()
        mock_supabase_query.insert.return_value.execute.return_value.data = {'data': 'foo'}
        supabase_client.query = mock_supabase_query

        query_builder = QueryBuilder()
        query_builder.insert_data = {'insert': 'data'}

        # Execution
        result = supabase_client.execute(query_builder=query_builder)

        # Testing
        mock_supabase_query.insert.assert_called_once_with({'insert': 'data'})
        mock_supabase_query.insert.return_value.execute.assert_called_once()

        assert result == {'data': 'foo'}

    def test_update(self, supabase_client: SupabaseClient):
        # Prepare data
        mock_supabase_query = Mock()
        mock_supabase_query.update.return_value.eq.return_value.neq.return_value.execute.return_value.data = [
            {'data': 'foo'}
        ]
        supabase_client.query = mock_supabase_query

        query_builder = QueryBuilder()
        query_builder.update_data = {'update': 'data'}
        query_builder.equal = {'id': 1}  # type: ignore
        query_builder.not_equal = {'title': 'test'}  # type: ignore

        # Execution
        result = supabase_client.execute(query_builder=query_builder)

        # Testing
        mock_supabase_query.update.assert_called_once_with({'update': 'data'})
        mock_supabase_query.update.return_value.eq.assert_called_once_with('id', 1)
        mock_supabase_query.update.return_value.eq.return_value.neq.assert_called_once_with('title', 'test')
        mock_supabase_query.update.return_value.eq.return_value.neq.return_value.execute.assert_called_once()

        assert result == [{'data': 'foo'}]

    def test_filter(self, supabase_client: SupabaseClient):
        # Prepare data
        mock_supabase_query = Mock()
        mock_supabase_query.select.return_value.eq.return_value.neq.return_value.execute.return_value.data = [
            {'test': 'data'}
        ]
        supabase_client.query = mock_supabase_query

        query_builder = QueryBuilder()
        query_builder.equal = {'id': 1}  # type: ignore
        query_builder.not_equal = {'title': 'test'}  # type: ignore

        # Execution
        result = supabase_client.execute(query_builder=query_builder)

        # Testing
        mock_supabase_query.select.return_value.eq.assert_called_once_with('id', 1)
        mock_supabase_query.select.return_value.eq.return_value.neq.assert_called_once_with('title', 'test')
        mock_supabase_query.select.return_value.eq.return_value.neq.return_value.execute.assert_called_once()

        assert result == [{'test': 'data'}]

    def test_count(self, supabase_client: SupabaseClient):
        # Prepare data
        mock_supabase_query = Mock()
        mock_supabase_query.select.return_value.eq.return_value.neq.return_value.execute.return_value.count = 1
        supabase_client.query = mock_supabase_query

        query_builder = QueryBuilder()
        query_builder.equal = {'id': 1}  # type: ignore
        query_builder.not_equal = {'title': 'test'}  # type: ignore
        query_builder.count_mode = True

        # Execution
        result = supabase_client.execute(query_builder=query_builder)

        # Testing
        mock_supabase_query.select.assert_called_once_with('*', count='exact')
        mock_supabase_query.select.return_value.eq.assert_called_once_with('id', 1)
        mock_supabase_query.select.return_value.eq.return_value.neq.assert_called_once_with('title', 'test')
        mock_supabase_query.select.return_value.eq.return_value.neq.return_value.execute.assert_called_once()

        assert result == 1
