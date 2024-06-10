import pytest

from supadantic.clients import CacheClient


class TestCacheClient:
    @pytest.fixture
    def cache_client(self) -> CacheClient:
        return CacheClient(table_name='table_name')

    class TestInsert:
        def test_insert_with_existing_data(self, cache_client: CacheClient):
            # Prepare data
            cache_client._cache[1] = {'foo': 'bar'}
            cache_client._cache[2] = {'bar': 'foo'}

            # Execution
            response = cache_client.insert({'test': 'foo'})

            # Testing
            assert response == {'id': 3, 'test': 'foo'}

        def test_insert_first_object(self, cache_client: CacheClient):
            # Execution
            cache_client._cache = {}
            response = cache_client.insert({'foo': 'bar'})

            # Testing
            assert response == {'id': 1, 'foo': 'bar'}

    def test_update(self, cache_client: CacheClient):
        # Prepare data
        cache_client._cache[1] = {'id': 1, 'foo': 'bar'}

        # Execution
        response = cache_client.update(id=1, data={'foo': 'test'})

        # Testing
        assert response == {'id': 1, 'foo': 'test'}

    def test_select(self, cache_client: CacheClient):
        # Prepare data
        cache_client._cache = {
            1: {'id': 1, 'foo': 'bar'},
            2: {'id': 2, 'foo': 'test'},
            3: {'id': 3, 'foo': 'value'},
            4: {'id': 4, 'foo': 'test'},
        }

        # Testing
        assert cache_client.select(eq={'id': 1}) == [{'id': 1, 'foo': 'bar'}]
        assert cache_client.select(eq={'id': 2, 'foo': 'foo'}) == []
        assert cache_client.select(neq={'foo': 'test'}) == [{'id': 1, 'foo': 'bar'}, {'id': 3, 'foo': 'value'}]
        assert cache_client.select(eq={'foo': 'test'}) == [{'id': 2, 'foo': 'test'}, {'id': 4, 'foo': 'test'}]

    def test_delete(self, cache_client: CacheClient):
        # Prepare data
        cache_client._cache = {}
        cache_client._cache[1] = {'id': 1, 'foo': 'bar'}

        # Execution
        cache_client.delete(id=1)

        # Testing
        assert cache_client._cache == {}

    def test_bulk_update(self, cache_client: CacheClient):
        # Prepare data
        cache_client._cache = {
            1: {'id': 1, 'foo': 'bar'},
            2: {'id': 2, 'foo': 'test'},
            3: {'id': 3, 'foo': 'value'},
        }

        # Execution
        response = cache_client.bulk_update(ids=(1, 3), data={'foo': 'foo'})

        # Testing
        assert response == [
            {'id': 1, 'foo': 'foo'},
            {'id': 3, 'foo': 'foo'},
        ]
        assert cache_client._cache == {
            1: {'id': 1, 'foo': 'foo'},
            2: {'id': 2, 'foo': 'test'},
            3: {'id': 3, 'foo': 'foo'},
        }

    def test_bulk_delete(self, cache_client: CacheClient):
        # Prepare data
        cache_client._cache = {
            1: {'id': 1, 'foo': 'bar'},
            2: {'id': 2, 'foo': 'test'},
            3: {'id': 3, 'foo': 'value'},
        }

        # Execution
        result = cache_client.bulk_delete(ids=(2, 3))

        # Testing
        assert result == [{'id': 2, 'foo': 'test'}, {'id': 3, 'foo': 'value'}]
        assert cache_client._cache == {1: {'id': 1, 'foo': 'bar'}}
