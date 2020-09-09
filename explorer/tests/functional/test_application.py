from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from explorer.tests.functional.pages import get_driver, HomePage


class TestApplication(StaticLiveServerTestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')
        self.driver = get_driver()

        # Log into the site via selenium by stealing the cookie from the Django client
        self.driver.get(self.live_server_url + "/page-that-does-not-exist-and-returns-404")
        self.driver.add_cookie(
            {
                "name": self.client.cookies[settings.SESSION_COOKIE_NAME].key,
                "value": self.client.cookies[settings.SESSION_COOKIE_NAME].value,
                "path": self.client.cookies[settings.SESSION_COOKIE_NAME]['path'],
            }
        )

    def tearDown(self) -> None:
        self.driver.close()

    def test_can_execute_query(self):
        home_page = HomePage(driver=self.driver, base_url=self.live_server_url)
        home_page.open()

        home_page.enter_query("select 1, 2, 3")
        home_page.click_run()

        assert home_page.read_result_headers() == ['?column?', '?column?', '?column?']
        assert home_page.read_result_rows() == [["1", "2", "3"]]

    def test_results_pagination(self):
        home_page = HomePage(driver=self.driver, base_url=self.live_server_url)
        home_page.open()

        home_page.enter_query("select unnest(array[1, 2, 3]) as numbers")
        home_page.click_run()

        home_page.change_results_pagination(page=1, results_per_page=2)

        assert home_page.read_result_headers() == ['numbers']
        assert home_page.read_result_rows() == [["1"], ["2"]]

        home_page.change_results_pagination(page=2, results_per_page=2)

        assert home_page.read_result_headers() == ['numbers']
        assert home_page.read_result_rows() == [["3"]]

    def test_format_sql(self):
        home_page = HomePage(driver=self.driver, base_url=self.live_server_url)
        home_page.open()

        home_page.enter_query("select unnest(array[1, 2, 3]) as numbers")
        home_page.click_format_sql()

        assert home_page.read_sql() == "select\n  unnest(array [1, 2, 3]) as numbers"

    def test_save_and_run_a_query(self):
        home_page = HomePage(driver=self.driver, base_url=self.live_server_url)
        home_page.open()

        home_page.enter_query("select 1, 2, 3")
        save_page = home_page.click_save()

        title = uuid4()
        save_page.set_title(str(title))
        save_page.set_description("I am a lovely query")

        query_detail_page = save_page.click_save()

        assert query_detail_page.read_title() == str(title)
        assert query_detail_page.read_description() == 'I am a lovely query'
        assert query_detail_page.read_sql() == 'select 1, 2, 3'

        edit_query_on_home_page = query_detail_page.click_edit()
        edit_query_on_home_page.click_run()

        assert edit_query_on_home_page.read_result_headers() == ['?column?', '?column?', '?column?']
        assert edit_query_on_home_page.read_result_rows() == [["1", "2", "3"]]

        query_log_page = edit_query_on_home_page.click_query_log()
        assert f"Query {query_detail_page.query_id}" in query_log_page.get_html()
        assert f"select 1, 2, 3" in query_log_page.get_html()

    def test_download_a_query(self):
        home_page = HomePage(driver=self.driver, base_url=self.live_server_url)
        home_page.open()

        home_page.enter_query("select 1, 2, 3")
        save_page = home_page.click_save()

        title = uuid4()
        save_page.set_title(str(title))
        save_page.set_description("I am a lovely query")

        query_detail_page = save_page.click_save()

        assert query_detail_page.read_title() == str(title)
        assert query_detail_page.read_description() == 'I am a lovely query'
        assert query_detail_page.read_sql() == 'select 1, 2, 3'

        edit_query_on_home_page = query_detail_page.click_edit()
        edit_query_on_home_page.click_run()

        assert edit_query_on_home_page.read_result_headers() == ['?column?', '?column?', '?column?']
        assert edit_query_on_home_page.read_result_rows() == [["1", "2", "3"]]

        query_log_page = edit_query_on_home_page.click_query_log()
        assert f"Query {query_detail_page.query_id}" in query_log_page.get_html()
        assert f"select 1, 2, 3" in query_log_page.get_html()
