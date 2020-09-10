import json
import time

from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.test import TestCase, TransactionTestCase

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

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
        resp = self.client.get(reverse("list_queries"))
        self.assertContains(resp, 'foo (3)')
        self.assertContains(resp, 'foo - bar2')
        self.assertContains(resp, 'qux - mux')

    def test_run_count(self):
        q = SimpleQueryFactory(title='foo - bar1')
        for i in range(0, 4):
            q.log()
        resp = self.client.get(reverse("list_queries"))
        self.assertContains(resp, '4')


class TestQueryCreateView(TransactionTestCase):
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
        data['action'] = "save"
        del data['id']
        del data['created_by_user']

        self.client.post(reverse("query_create"), data)

        self.assertEqual(Query.objects.all()[0].sql, 'SELECT 1;')

    def test_invalid_query(self):
        self.client.login(username='admin', password='pwd')
        query = SimpleQueryFactory.build(sql='SELECT foo; DELETE FROM foo;')
        data = model_to_dict(query)
        data['action'] = "save"
        del data['id']
        del data['created_by_user']
        response = self.client.post(reverse("query_create"), data)
        assert response.status_code == 200
        self.assertEquals(len(Query.objects.all()), 0)

    def test_renders_back_link(self):
        self.client.login(username='admin', password='pwd')
        response = self.client.get(reverse("query_create"), {"sql": "select 1, 2, 3"})
        assert (
            '<a href="/?sql=select+1%2C+2%2C+3" class="govuk-back-link">Back</a>'
            in response.content.decode(response.charset)
        )


class TestQueryDetailView(TestCase):
    databases = ['default', 'alt']

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_query_with_bad_sql_fails_on_save(self):
        query = SimpleQueryFactory(sql="select 1;")
        resp = self.client.post(
            reverse("query_detail", kwargs={'query_id': query.id}),
            data={'sql': 'error', "action": "save"},
        )
        self.assertTemplateUsed(resp, 'explorer/query.html')
        self.assertContains(resp, "Enter a SQL statement starting with SELECT or WITH")

    def test_posting_query_saves_correctly(self):
        expected = 'select 2;'
        query = SimpleQueryFactory(sql="select 1;")
        data = model_to_dict(query)
        data['sql'] = expected
        data['action'] = 'save'
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

    def test_doesnt_render_results_on_page(self):
        query = SimpleQueryFactory(sql='select 6870+1;')
        resp = self.client.post(
            reverse("query_detail", kwargs={'query_id': query.id}),
            {'sql': 'select 6870+2;', 'action': 'save'},
        )
        self.assertTemplateUsed(resp, 'explorer/query.html')
        self.assertNotContains(resp, '6872')

    def test_renders_back_link(self):
        query = SimpleQueryFactory(sql='select 6870+1;')
        self.client.login(username='admin', password='pwd')
        response = self.client.get(
            reverse("query_detail", kwargs={"query_id": query.id}), {"from": "play"}
        )
        assert (
            f'<a href="/?sql=select+6870%2B1%3B&amp;query_id={query.id}" class="govuk-back-link">Back</a>'
            in response.content.decode(response.charset)
        )


class TestDownloadView(TestCase):
    def setUp(self):
        self.query = SimpleQueryFactory(sql="select 1;")
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_params_in_download(self):
        q = SimpleQueryFactory(sql="select '$$foo$$';")
        url = '%s?params=%s' % (
            reverse("download_query", kwargs={'query_id': q.id}),
            'foo:1234567890',
        )
        resp = self.client.get(url)
        self.assertContains(resp, "1234567890")

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
        self.assertEqual(response.url, f'/queries/{query.pk}/')

    def test_download_json(self):
        query = SimpleQueryFactory()
        url = reverse("download_query", args=[query.pk]) + '?format=json'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        json_data = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(json_data, list)
        self.assertEqual(len(json_data), 1)
        self.assertEqual(json_data, [{'two': 2}])


class TestHomePage(TransactionTestCase):
    databases = ['default', 'alt']

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_empty_playground_renders(self):
        resp = self.client.get(reverse("explorer_index"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'explorer/home.html')

    def test_playground_renders_with_query_sql(self):
        query = SimpleQueryFactory(sql="select 1;")
        resp = self.client.get('%s?query_id=%s' % (reverse("explorer_index"), query.id))
        self.assertTemplateUsed(resp, 'explorer/home.html')
        self.assertContains(resp, 'select 1;')

    def test_playground_renders_with_posted_sql(self):
        resp = self.client.post(
            reverse("explorer_index"), {'title': 'test', 'sql': 'select 1+3400;', "action": "run"},
        )
        self.assertTemplateUsed(resp, 'explorer/home.html')
        self.assertContains(resp, '3401')

    def test_playground_redirects_to_query_create_on_save_with_sql_query_param(self):
        resp = self.client.post(
            reverse("explorer_index"), {'sql': 'select 1+3400;', "action": "save"}
        )
        self.assertEqual(resp.url, '/queries/create/?sql=select+1%2B3400%3B')

    def test_playground_renders_with_empty_posted_sql(self):
        resp = self.client.post(reverse("explorer_index"), {'sql': '', "action": "run"})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'explorer/home.html')

    def test_query_with_no_resultset_doesnt_throw_error(self):
        query = SimpleQueryFactory(sql="")
        resp = self.client.get('%s?query_id=%s' % (reverse("explorer_index"), query.id))
        self.assertTemplateUsed(resp, 'explorer/home.html')

    def test_loads_query_from_log(self):
        querylog = QueryLogFactory()
        resp = self.client.get('%s?querylog_id=%s' % (reverse("explorer_index"), querylog.id))
        self.assertContains(resp, "FOUR")

    def test_multiple_connections_integration(self):
        from explorer.app_settings import EXPLORER_CONNECTIONS
        from explorer.connections import connections

        c1_alias = EXPLORER_CONNECTIONS['Postgres']
        conn = connections[c1_alias]
        c1 = conn.cursor()
        c1.execute('CREATE TABLE IF NOT EXISTS animals (name text NOT NULL);')
        c1.execute('INSERT INTO animals ( name ) VALUES (\'peacock\')')
        c1.execute('COMMIT')

        c2_alias = EXPLORER_CONNECTIONS['Alt']
        conn = connections[c2_alias]
        c2 = conn.cursor()
        c2.execute('CREATE TABLE IF NOT EXISTS animals (name text NOT NULL);')
        c2.execute('INSERT INTO animals ( name ) VALUES (\'superchicken\')')
        c2.execute('COMMIT')

        resp = self.client.post(
            reverse("explorer_index"),
            {
                "title": "Playground query",
                "sql": "select name from animals;",
                "connection": c1_alias,
                "action": "run",
            },
        )
        self.assertContains(resp, "peacock")

        resp = self.client.post(
            reverse("explorer_index"),
            {
                "title": "Playground query",
                "sql": "select name from animals;",
                "connection": c2_alias,
                "action": "run",
            },
        )
        self.assertContains(resp, "superchicken")


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

        c1_alias = EXPLORER_CONNECTIONS['Postgres']
        conn = connections[c1_alias]
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS animals (name text NOT NULL);')
        c.execute('INSERT INTO animals ( name ) VALUES (\'peacock\')')

        c2_alias = EXPLORER_CONNECTIONS['Alt']
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
        self.assertEqual(response.content.decode('utf-8'), '?column?|?column?\r\n1|2\r\n')

    def test_sql_download_csv_with_tab_delim(self):
        url = reverse("download_sql") + '?format=csv&delim=tab'

        response = self.client.post(url, {'sql': 'select 1,2;'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')
        self.assertEqual(response.content.decode('utf-8'), '?column?\t?column?\r\n1\t2\r\n')

    def test_sql_download_csv_with_bad_delim(self):
        url = reverse("download_sql") + '?format=csv&delim=foo'

        response = self.client.post(url, {'sql': 'select 1,2;'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')
        self.assertEqual(response.content.decode('utf-8'), '?column?,?column?\r\n1,2\r\n')

    def test_sql_download_json(self):
        url = reverse("download_sql") + '?format=json'

        response = self.client.post(url, {'sql': 'select 1;'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')


class TestParamsInViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')
        self.query = SimpleQueryFactory(sql="select $$swap$$;")

    def test_retrieving_query_works_with_params(self):
        resp = self.client.get(
            reverse("explorer_index") + f"?query_id={self.query.id}&params=swap:1234567890"
        )
        self.assertContains(resp, "1234567890")


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
        query = Query.objects.get(id=self.query.id)
        self.assertEqual(query.created_by_user_id, self.user.id)

    def test_new_query_gets_created_by_logged_in_user(self):
        self.client.post(reverse("query_create"), {**self.data, "action": "save"})
        query = Query.objects.first()
        self.assertEqual(query.created_by_user_id, self.user.id)


class TestQueryLog(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_playground_saves_query_to_log(self):
        self.client.post(
            reverse("explorer_index"), {'title': 'test', 'sql': 'select 1', "action": "run"}
        )
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
        data['action'] = 'run'
        self.client.post(reverse("explorer_index") + f"?query_id={query.id}", data)
        self.assertEqual(1, QueryLog.objects.count())

    def test_query_gets_logged_and_appears_on_log_page(self):
        query = SimpleQueryFactory()
        data = model_to_dict(query)
        data['sql'] = 'select 12345;'
        data['action'] = 'run'
        self.client.post(reverse("explorer_index") + f"?query_id={query.id}", data)
        resp = self.client.get(reverse("explorer_logs"))
        self.assertContains(resp, 'select 12345;')

    def test_is_playground(self):
        self.assertTrue(QueryLog(sql='foo').is_playground)

        q = SimpleQueryFactory()
        self.assertFalse(QueryLog(sql='foo', query_id=q.id).is_playground)
