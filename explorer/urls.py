import threading

from django.conf import settings
from django.urls import include, path

from explorer.tasks import build_schema_cache_async
from explorer.views import (
    ConnectionBrowserListView,
    CreateQueryView,
    DeleteQueryView,
    DownloadFromSqlView,
    DownloadQueryView,
    format_sql,
    ListQueryLogView,
    ListQueryView,
    PlayQueryView,
    QueryView,
    SchemaView,
    TableBrowserDetailView,
    TableBrowserListView,
)

urlpatterns = [
    path('', ListQueryView.as_view(), name='explorer_index'),
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
    path('<int:query_id>/', QueryView.as_view(), name='query_detail'),
    path('<int:query_id>/download/', DownloadQueryView.as_view(), name='download_query'),
    path('download/', DownloadFromSqlView.as_view(), name='download_sql'),
    path('<int:pk>/delete/', DeleteQueryView.as_view(), name='query_delete'),
    path('new/', CreateQueryView.as_view(), name='query_create'),
    path('play/', PlayQueryView.as_view(), name='explorer_playground'),
    path('schema/<slug:connection>/', SchemaView.as_view(), name='explorer_schema'),
    path('logs/', ListQueryLogView.as_view(), name='explorer_logs'),
    path('format/', format_sql, name='format_sql'),
    path('browse/', ConnectionBrowserListView.as_view(), name='connection_browser_list'),
    path('browse/<slug:connection>/', TableBrowserListView.as_view(), name='table_browser_list'),
    path(
        'browse/<slug:connection>/<slug:schema>/<slug:table>/',
        TableBrowserDetailView.as_view(),
        name='table_browser_detail',
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)),] + urlpatterns

# Build schema cache at startup in background
if not settings.MULTIUSER_DEPLOYMENT and not settings.TEST:

    def build_schema():
        for alias in settings.EXPLORER_CONNECTIONS:
            build_schema_cache_async(alias)

    t = threading.Thread(target=build_schema, args=(), kwargs={})
    t.setDaemon(True)
    t.start()
