import os

import pytest


pytest_plugins = ('tests.fixtures.model',)


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock Supabase environment variables."""
    os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
    os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYW5vbiJ9.ZOxUwxBHPJQR4Q7q9FtqV3LFwP-P4jUVLXGb5JhKBLA'
    yield
    del os.environ['SUPABASE_URL']
    del os.environ['SUPABASE_KEY']
