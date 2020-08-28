from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from explorer import schema
from explorer.app_settings import EXPLORER_CONNECTIONS


class TestSchemaInfo(TestCase):
    databases = ['postgres']

    def setUp(self):
        cache.clear()

    @patch('explorer.schema._get_includes')
    @patch('explorer.schema._get_excludes')
    def test_schema_info_returns_valid_data(self, mocked_excludes, mocked_includes):
        mocked_includes.return_value = None
        mocked_excludes.return_value = []
        res = schema.schema_info(EXPLORER_CONNECTIONS['Postgres'])
        assert mocked_includes.called  # sanity check: ensure patch worked
        tables = [x.name.name for x in res]
        self.assertIn('data_explorer_explorer_query', tables)
        schemas = [x.name.schema for x in res]
        self.assertIn('public', schemas)

    @patch('explorer.schema._get_includes')
    @patch('explorer.schema._get_excludes')
    def test_table_exclusion_list(self, mocked_excludes, mocked_includes):
        mocked_includes.return_value = None
        mocked_excludes.return_value = ('data_explorer_explorer_',)
        res = schema.schema_info(EXPLORER_CONNECTIONS['Postgres'])
        tables = [x.name.name for x in res]
        self.assertNotIn('data_explorer_explorer_query', tables)

    @patch('explorer.schema._get_includes')
    @patch('explorer.schema._get_excludes')
    def test_app_inclusion_list(self, mocked_excludes, mocked_includes):
        mocked_includes.return_value = ('data_explorer_auth_',)
        mocked_excludes.return_value = []
        res = schema.schema_info(EXPLORER_CONNECTIONS['Postgres'])
        tables = [x.name.name for x in res]
        self.assertNotIn('data_explorer_explorer_query', tables)
        self.assertIn('data_explorer_auth_user', tables)

    @patch('explorer.schema._get_includes')
    @patch('explorer.schema._get_excludes')
    def test_app_inclusion_list_excluded(self, mocked_excludes, mocked_includes):
        # Inclusion list "wins"
        mocked_includes.return_value = ('data_explorer_explorer_',)
        mocked_excludes.return_value = ('data_explorer_explorer_',)
        res = schema.schema_info(EXPLORER_CONNECTIONS['Postgres'])
        tables = [x.name.name for x in res]
        self.assertIn('data_explorer_explorer_query', tables)

    @patch('explorer.schema.build_schema_cache_async')
    @patch('explorer.schema.do_async')
    def test_builds_async(self, mocked_async_check, mock_build_schema_cache_async):
        mocked_async_check.return_value = True
        self.assertIsNone(schema.schema_info(EXPLORER_CONNECTIONS['Postgres']))
