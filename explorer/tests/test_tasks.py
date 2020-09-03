from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase

from explorer.app_settings import EXPLORER_DEFAULT_CONNECTION as CONN
from explorer.models import QueryLog
from explorer.tasks import build_schema_cache_async, truncate_querylogs


class TestTasks(TestCase):
    def test_truncating_querylogs(self):
        QueryLog(sql='foo').save()
        QueryLog.objects.filter(sql='foo').update(run_at=datetime.now() - timedelta(days=30))
        QueryLog(sql='bar').save()
        QueryLog.objects.filter(sql='bar').update(run_at=datetime.now() - timedelta(days=29))
        truncate_querylogs(30)
        self.assertEqual(QueryLog.objects.count(), 1)

    @patch('explorer.schema.build_schema_info')
    @patch('explorer.schema.cache.set')
    def test_build_schema_cache_async(self, _, mocked_build):
        mocked_build.return_value = ['list_of_tuples']
        schema = build_schema_cache_async(CONN)
        assert mocked_build.called
        self.assertEqual(schema, ['list_of_tuples'])
