from supadantic.query_builder import QueryBuilder


class TestQueryBuilder:
    def test_select_fields(self):
        query_builder = QueryBuilder()
        assert query_builder.select_fields == '*'

        query_builder.set_select_fields(['test', 'foo'])
        assert query_builder.select_fields == ('test', 'foo')

        query_builder.set_select_fields(['bar'])
        assert query_builder.select_fields == ('test', 'foo', 'bar')
        assert query_builder.mode == QueryBuilder.Mode.FILTER_MODE

    def test_equal(self):
        query_builder = QueryBuilder()
        assert query_builder.equal == ()

        query_builder.set_equal(test='bar')
        assert query_builder.equal == (('test', 'bar'),)

        query_builder.set_equal(foo='bar')
        assert query_builder.equal == (
            ('test', 'bar'),
            (
                'foo',
                'bar',
            ),
        )
        assert query_builder.mode == QueryBuilder.Mode.FILTER_MODE

    def test_not_equal(self):
        query_builder = QueryBuilder()
        assert query_builder.not_equal == ()

        query_builder.set_not_equal(test='bar')
        assert query_builder.not_equal == (('test', 'bar'),)

        query_builder.set_not_equal(foo='bar')
        assert query_builder.not_equal == (('test', 'bar'), ('foo', 'bar'))
        assert query_builder.mode == QueryBuilder.Mode.FILTER_MODE

    def test_insert_data(self):
        query_builder = QueryBuilder()
        assert query_builder.insert_data is None

        query_builder.set_insert_data({'a': 'b'})
        assert query_builder.insert_data == {'a': 'b'}
        assert query_builder.mode == QueryBuilder.Mode.INSERT_MODE

    def test_update_data(self):
        query_builder = QueryBuilder()
        assert query_builder.update_data is None

        query_builder.set_update_data({'a': 'b'})
        assert query_builder.update_data == {'a': 'b'}
        assert query_builder.mode == QueryBuilder.Mode.UPDATE_MODE

    def test_delete_mode(self):
        query_builder = QueryBuilder()
        assert query_builder.delete_mode is False

        query_builder.set_delete_mode(True)
        assert query_builder.delete_mode is True
        assert query_builder.mode == QueryBuilder.Mode.DELETE_MODE

    def test_count_mode(self):
        query_builder = QueryBuilder()
        assert query_builder.count_mode is False

        query_builder.set_count_mode(True)
        assert query_builder.count_mode is True
        assert query_builder.mode == QueryBuilder.Mode.COUNT_MODE
