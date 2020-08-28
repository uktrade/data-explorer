import json
import time
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.forms.models import model_to_dict
from django.test import TestCase

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from explorer.app_settings import EXPLORER_CONNECTIONS
from explorer.models import Query, QueryLog
from explorer.tests.factories import QueryLogFactory, SimpleQueryFactory


class TestQueryListView(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_headers(self):
        SimpleQueryFactory(title='foo - bar1')
        SimpleQueryFactory(title='foo - bar2')
        SimpleQueryFactory(title='foo - bar3')
        SimpleQueryFactory(title='qux - mux')
        resp = self.client.get(reverse("explorer_index"))
        self.assertContains(resp, 'foo (3)')
        self.assertContains(resp, 'foo - bar2')
        self.assertContains(resp, 'qux - mux')

    def test_run_count(self):
        q = SimpleQueryFactory(title='foo - bar1')
        for i in range(0, 4):
            q.log()
        resp = self.client.get(reverse("explorer_index"))
        self.assertContains(resp, '4')


class TestQueryCreateView(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.user = User.objects.create_user('user', 'user@user.com', 'pwd')

    def test_renders_with_title(self):
        self.client.login(username='admin', password='pwd')
        resp = self.client.get(reverse("query_create"))
        self.assertTemplateUsed(resp, 'explorer/query.html')
        self.assertContains(resp, "New Query")

    def test_valid_query(self):
        self.client.login(username='admin', password='pwd')
        query = SimpleQueryFactory.build(sql='SELECT 1;')
        data = model_to_dict(query)
        del data['id']
        del data['created_by_user']
        self.client.post(reverse("query_create"), data)
        self.assertEqual(Query.objects.all()[0].sql, 'SELECT 1;')

    def test_invalid_query(self):
        self.client.login(username='admin', password='pwd')
        query = SimpleQueryFactory.build(sql='DELETE FROM foo;')
        data = model_to_dict(query)
        del data['id']
        del data['created_by_user']
        self.client.post(reverse("query_create"), data)
        self.assertEquals(len(Query.objects.all()), 0)


class TestQueryDetailView(TestCase):
    databases = ['default', 'alt']

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_query_with_bad_sql_fails_on_save(self):
        query = SimpleQueryFactory(sql="select 1;")
        resp = self.client.post(
            reverse("query_detail", kwargs={'query_id': query.id}), data={'sql': 'error'}
        )
        self.assertTemplateUsed(resp, 'explorer/query.html')
        self.assertContains(resp, "Enter a SQL statement starting with SELECT or WITH")

    def test_posting_query_saves_correctly(self):
        expected = 'select 2;'
        query = SimpleQueryFactory(sql="select 1;")
        data = model_to_dict(query)
        data['sql'] = expected
        self.client.post(reverse("query_detail", kwargs={'query_id': query.id}), data)
        self.assertEqual(Query.objects.get(pk=query.id).sql, expected)

    def test_change_permission_required_to_save_query(self):
        query = SimpleQueryFactory()
        expected = query.sql
        resp = self.client.get(reverse("query_detail", kwargs={'query_id': query.id}))
        self.assertTemplateUsed(resp, 'explorer/query.html')

        self.client.post(
            reverse("query_detail", kwargs={'query_id': query.id}), {'sql': 'select 1;'}
        )
        self.assertEqual(Query.objects.get(pk=query.id).sql, expected)

    def test_modified_date_gets_updated_after_viewing_query(self):
        query = SimpleQueryFactory()
        old = query.last_run_date
        time.sleep(0.1)
        self.client.get(reverse("query_detail", kwargs={'query_id': query.id}))
        self.assertNotEqual(old, Query.objects.get(pk=query.id).last_run_date)

    def test_doesnt_render_results_if_show_is_none(self):
        query = SimpleQueryFactory(sql='select 6870+1;')
        resp = self.client.get(reverse("query_detail", kwargs={'query_id': query.id}) + '?show=0')
        self.assertTemplateUsed(resp, 'explorer/query.html')
        self.assertNotContains(resp, '6871')

    def test_doesnt_render_results_if_show_is_none_on_post(self):
        query = SimpleQueryFactory(sql='select 6870+1;')
        resp = self.client.post(
            reverse("query_detail", kwargs={'query_id': query.id}) + '?show=0',
            {'sql': 'select 6870+2;'},
        )
        self.assertTemplateUsed(resp, 'explorer/query.html')
        self.assertNotContains(resp, '6872')

    def test_individual_view_permission(self):
        self.client.logout()
        user = User.objects.create_user('user1', 'user@user.com', 'pwd')
        self.client.login(username='user1', password='pwd')

        query = SimpleQueryFactory(sql="select 123+1")

        with self.settings(EXPLORER_USER_QUERY_VIEWS={user.id: [query.id]}):
            resp = self.client.get(reverse("query_detail", kwargs={'query_id': query.id}))
        self.assertTemplateUsed(resp, 'explorer/query.html')
        self.assertContains(resp, "124")

    def test_multiple_connections_integration(self):
        from explorer.app_settings import EXPLORER_CONNECTIONS
        from explorer.connections import connections

        c1_alias = EXPLORER_CONNECTIONS['SQLite']
        conn = connections[c1_alias]
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS animals (name text NOT NULL);')
        c.execute('INSERT INTO animals ( name ) VALUES (\'peacock\')')

        c2_alias = EXPLORER_CONNECTIONS['Another']
        conn = connections[c2_alias]
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS animals (name text NOT NULL);')
        c.execute('INSERT INTO animals ( name ) VALUES (\'superchicken\')')

        query = SimpleQueryFactory(sql="select name from animals;", connection=c1_alias)
        resp = self.client.get(reverse("query_detail", kwargs={'query_id': query.id}))
        self.assertContains(resp, "peacock")

        query = SimpleQueryFactory(sql="select name from animals;", connection=c2_alias)
        resp = self.client.get(reverse("query_detail", kwargs={'query_id': query.id}))
        self.assertContains(resp, "superchicken")


class TestDownloadView(TestCase):
    def setUp(self):
        self.query = SimpleQueryFactory(sql="select 1;")
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_params_in_download(self):
        q = SimpleQueryFactory(sql="select '$$foo$$';")
        url = '%s?params=%s' % (reverse("download_query", kwargs={'query_id': q.id}), 'foo:123')
        resp = self.client.get(url)
        self.assertContains(resp, "'123'")

    def test_download_defaults_to_csv(self):
        query = SimpleQueryFactory()
        url = reverse("download_query", args=[query.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')

    def test_download_csv(self):
        query = SimpleQueryFactory()
        url = reverse("download_query", args=[query.pk]) + '?format=csv'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')

    def test_bad_query_redirects_to_query_view(self):
        query = SimpleQueryFactory(sql='bad')
        url = reverse("download_query", args=[query.pk]) + '?format=csv'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/{query.pk}/')

    def test_download_json(self):
        query = SimpleQueryFactory()
        url = reverse("download_query", args=[query.pk]) + '?format=json'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        json_data = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(json_data, list)
        self.assertEqual(len(json_data), 1)
        self.assertEqual(json_data, [{'TWO': 2}])


class TestQueryPlayground(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_empty_playground_renders(self):
        resp = self.client.get(reverse("explorer_playground"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'explorer/play.html')

    def test_playground_renders_with_query_sql(self):
        query = SimpleQueryFactory(sql="select 1;")
        resp = self.client.get('%s?query_id=%s' % (reverse("explorer_playground"), query.id))
        self.assertTemplateUsed(resp, 'explorer/play.html')
        self.assertContains(resp, 'select 1;')

    def test_playground_renders_with_posted_sql(self):
        resp = self.client.post(
            reverse("explorer_playground"), {'title': 'test', 'sql': 'select 1+3400;'}
        )
        self.assertTemplateUsed(resp, 'explorer/play.html')
        self.assertContains(resp, '3401')

    def test_playground_doesnt_render_with_posted_sql_if_show_is_none(self):
        resp = self.client.post(
            reverse("explorer_playground") + '?show=0', {'sql': 'select 1+3400;'}
        )
        self.assertTemplateUsed(resp, 'explorer/play.html')
        self.assertNotContains(resp, '3401')

    def test_playground_renders_with_empty_posted_sql(self):
        resp = self.client.post(reverse("explorer_playground"), {'sql': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'explorer/play.html')

    def test_query_with_no_resultset_doesnt_throw_error(self):
        query = SimpleQueryFactory(sql="")
        resp = self.client.get('%s?query_id=%s' % (reverse("explorer_playground"), query.id))
        self.assertTemplateUsed(resp, 'explorer/play.html')

    def test_loads_query_from_log(self):
        querylog = QueryLogFactory()
        resp = self.client.get('%s?querylog_id=%s' % (reverse("explorer_playground"), querylog.id))
        self.assertContains(resp, "FOUR")


class TestCSVFromSQL(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_downloading_from_playground(self):
        sql = "select 1;"
        resp = self.client.post(reverse("download_sql"), {'sql': sql})
        self.assertIn('attachment', resp['Content-Disposition'])
        self.assertEqual('text/csv', resp['content-type'])
        ql = QueryLog.objects.first()
        self.assertIn('filename="Playground_-_%s.csv"' % ql.id, resp['Content-Disposition'])


class TestSQLDownloadViews(TestCase):
    databases = ['default', 'alt']

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_sql_download_csv(self):
        url = reverse("download_sql") + '?format=csv'

        response = self.client.post(url, {'sql': 'select 1;'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')

    def test_sql_download_respects_connection(self):
        from explorer.app_settings import EXPLORER_CONNECTIONS
        from explorer.connections import connections

        c1_alias = EXPLORER_CONNECTIONS['SQLite']
        conn = connections[c1_alias]
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS animals (name text NOT NULL);')
        c.execute('INSERT INTO animals ( name ) VALUES (\'peacock\')')

        c2_alias = EXPLORER_CONNECTIONS['Another']
        conn = connections[c2_alias]
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS animals (name text NOT NULL);')
        c.execute('INSERT INTO animals ( name ) VALUES (\'superchicken\')')

        url = reverse("download_sql") + '?format=csv'

        response = self.client.post(url, {'sql': 'select * from animals;', 'connection': c2_alias})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'superchicken')

    def test_sql_download_csv_with_custom_delim(self):
        url = reverse("download_sql") + '?format=csv&delim=|'

        response = self.client.post(url, {'sql': 'select 1,2;'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')
        self.assertEqual(response.content.decode('utf-8'), '1|2\r\n1|2\r\n')

    def test_sql_download_csv_with_tab_delim(self):
        url = reverse("download_sql") + '?format=csv&delim=tab'

        response = self.client.post(url, {'sql': 'select 1,2;'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')
        self.assertEqual(response.content.decode('utf-8'), '1\t2\r\n1\t2\r\n')

    def test_sql_download_csv_with_bad_delim(self):
        url = reverse("download_sql") + '?format=csv&delim=foo'

        response = self.client.post(url, {'sql': 'select 1,2;'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')
        self.assertEqual(response.content.decode('utf-8'), '1,2\r\n1,2\r\n')

    def test_sql_download_json(self):
        url = reverse("download_sql") + '?format=json'

        response = self.client.post(url, {'sql': 'select 1;'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')


class TestSchemaView(TestCase):
    databases = ['default', 'postgres']

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_returns_schema_contents(self):
        resp = self.client.get(
            reverse("explorer_schema", kwargs={'connection': EXPLORER_CONNECTIONS['Postgres']})
        )
        self.assertContains(resp, "explorer_query")
        self.assertTemplateUsed(resp, 'explorer/schema.html')

    def test_returns_404_if_conn_doesnt_exist(self):
        resp = self.client.get(reverse("explorer_schema", kwargs={'connection': 'foo'}))
        self.assertEqual(resp.status_code, 404)

    @patch('explorer.schema.build_schema_cache_async')
    @patch('explorer.schema.do_async')
    def test_builds_async(self, mocked_async_check, mock_build_schema_cache_async):
        mocked_async_check.return_value = True
        resp = self.client.get(
            reverse("explorer_schema", kwargs={'connection': EXPLORER_CONNECTIONS['Postgres']})
        )
        self.assertTemplateUsed(resp, 'explorer/schema_building.html')


class TestFormat(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_returns_formatted_sql(self):
        resp = self.client.post(reverse("format_sql"), data={"sql": "select * from explorer_query"})
        resp = json.loads(resp.content.decode('utf-8'))
        self.assertIn("\n", resp['formatted'])
        self.assertIn("explorer_query", resp['formatted'])


class TestParamsInViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')
        self.query = SimpleQueryFactory(sql="select $$swap$$;")

    def test_retrieving_query_works_with_params(self):
        resp = self.client.get(
            reverse("query_detail", kwargs={'query_id': self.query.id}) + '?params=swap:123}'
        )
        self.assertContains(resp, "123")

    def test_saving_non_executing_query_with__wrong_url_params_fails(self):
        q = SimpleQueryFactory(sql="select $$swap$$;")
        data = model_to_dict(q)
        url = '%s?params=%s' % (reverse("query_detail", kwargs={'query_id': q.id}), 'foo:123')
        resp = self.client.post(url, data)
        self.assertContains(resp, 'Query error')

    def test_users_without_change_permissions_can_use_params(self):
        resp = self.client.get(
            reverse("query_detail", kwargs={'query_id': self.query.id}) + '?params=swap:123}'
        )
        self.assertContains(resp, "123")


class TestCreatedBy(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.user2 = User.objects.create_superuser('admin2', 'admin2@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')
        self.query = SimpleQueryFactory.build(created_by_user=self.user)
        self.data = model_to_dict(self.query)
        del self.data['id']
        self.data["created_by_user_id"] = self.user2.id

    def test_query_update_doesnt_change_created_user(self):
        self.query.save()
        self.client.post(reverse("query_detail", kwargs={'query_id': self.query.id}), self.data)
        q = Query.objects.get(id=self.query.id)
        self.assertEqual(q.created_by_user_id, self.user.id)

    def test_new_query_gets_created_by_logged_in_user(self):
        self.client.post(reverse("query_create"), self.data)
        q = Query.objects.first()
        self.assertEqual(q.created_by_user_id, self.user.id)


class TestQueryLog(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_playground_saves_query_to_log(self):
        self.client.post(reverse("explorer_playground"), {'title': 'test', 'sql': 'select 1'})
        log = QueryLog.objects.first()
        self.assertTrue(log.is_playground)
        self.assertEqual(log.sql, 'select 1')

    # Since it will be saved on the initial query creation, no need to log it
    def test_creating_query_does_not_save_to_log(self):
        query = SimpleQueryFactory()
        self.client.post(reverse("query_create"), model_to_dict(query))
        self.assertEqual(0, QueryLog.objects.count())

    def test_query_saves_to_log(self):
        query = SimpleQueryFactory()
        data = model_to_dict(query)
        data['sql'] = 'select 12345;'
        self.client.post(reverse("query_detail", kwargs={'query_id': query.id}), data)
        self.assertEqual(1, QueryLog.objects.count())

    def test_query_gets_logged_and_appears_on_log_page(self):
        query = SimpleQueryFactory()
        data = model_to_dict(query)
        data['sql'] = 'select 12345;'
        self.client.post(reverse("query_detail", kwargs={'query_id': query.id}), data)
        resp = self.client.get(reverse("explorer_logs"))
        self.assertContains(resp, 'select 12345;')

    def test_is_playground(self):
        self.assertTrue(QueryLog(sql='foo').is_playground)

        q = SimpleQueryFactory()
        self.assertFalse(QueryLog(sql='foo', query_id=q.id).is_playground)
