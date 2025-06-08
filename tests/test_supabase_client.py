from typing import TYPE_CHECKING

import httpx
import pytest

from supadantic.clients import SupabaseClient
from supadantic.query_builder import QueryBuilder


if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


class TestSupabaseClient:
    @pytest.fixture
    def supabase_client(self) -> SupabaseClient:
        return SupabaseClient(table_name='table_name')

    def test_delete(self, supabase_client: SupabaseClient, httpx_mock: 'HTTPXMock'):
        # Prepare response
        httpx_mock.add_response(
            method="DELETE",
            url=httpx.URL('https://test.supabase.co/rest/v1/table_name', params={'id': 'eq.1', 'title': 'neq.test'}),
            status_code=200,
        )

        query_builder = QueryBuilder()
        query_builder.set_equal(id=1)
        query_builder.set_not_equal(title='test')
        query_builder.set_delete_mode(True)

        # Execution
        supabase_client.execute(query_builder=query_builder)

        # Testing
        assert len(httpx_mock.get_requests()) == 1

    def test_insert(self, supabase_client: SupabaseClient, httpx_mock: 'HTTPXMock'):
        # Prepare response
        httpx_mock.add_response(
            method="POST",
            url="https://test.supabase.co/rest/v1/table_name",
            status_code=201,
            match_json={'insert': 'data'},
        )

        query_builder = QueryBuilder()
        query_builder.set_insert_data({'insert': 'data'})

        # Execution
        supabase_client.execute(query_builder=query_builder)

        # Testing
        assert len(httpx_mock.get_requests()) == 1

    def test_update(self, supabase_client: SupabaseClient, httpx_mock: 'HTTPXMock'):
        # Prepare response
        httpx_mock.add_response(
            method="PATCH",
            url=httpx.URL("https://test.supabase.co/rest/v1/table_name", params={'id': 'eq.1', 'title': 'neq.test'}),
            status_code=200,
            match_json={'update': 'data'},
        )

        query_builder = QueryBuilder()
        query_builder.set_update_data({'update': 'data'})
        query_builder.set_equal(id=1)
        query_builder.set_not_equal(title='test')

        # Execution
        supabase_client.execute(query_builder=query_builder)

        # Testing
        assert len(httpx_mock.get_requests()) == 1

    def test_filter(self, supabase_client: SupabaseClient, httpx_mock: 'HTTPXMock'):
        # Prepare response
        httpx_mock.add_response(
            method="GET",
            url=httpx.URL(
                'https://test.supabase.co/rest/v1/table_name',
                params={'select': '*', 'id': 'eq.1', 'title': 'neq.test', 'id__lte': 'lte.3'},
            ),
            status_code=200,
        )
        httpx_mock.add_response(is_optional=True)

        query_builder = QueryBuilder()
        query_builder.set_equal(id=1)
        query_builder.set_not_equal(title='test')
        query_builder.set_less_than_or_equal(id__lte=3)

        # Execution
        supabase_client.execute(query_builder=query_builder)

        # Testing
        assert len(httpx_mock.get_requests()) == 1

    def test_count(self, supabase_client: SupabaseClient, httpx_mock: 'HTTPXMock'):
        # Prepare response
        httpx_mock.add_response(
            method="GET",
            url=httpx.URL(
                'https://test.supabase.co/rest/v1/table_name',
                params={
                    'select': '*',
                    'id': 'eq.1',
                    'title': 'neq.test',
                },
            ),
            status_code=200,
        )

        query_builder = QueryBuilder()
        query_builder.set_equal(id=1)
        query_builder.set_not_equal(title='test')
        query_builder.set_count_mode(True)

        # Execution
        supabase_client.execute(query_builder=query_builder)

        # Testing
        assert len(httpx_mock.get_requests()) == 1
