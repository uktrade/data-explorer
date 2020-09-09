import threading

from django.conf import settings
from django.urls import include, path

from explorer.tasks import build_schema_cache_async
from explorer.views import (
    CreateQueryView,
    DeleteQueryView,
    DownloadFromSqlView,
    DownloadQueryView,
    ListQueryLogView,
    ListQueryView,
    PlayQueryView,
    QueryView,
)

urlpatterns = [
    path('', PlayQueryView.as_view(), name='explorer_index'),
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
    path('download/', DownloadFromSqlView.as_view(), name='download_sql'),
    path('queries/', ListQueryView.as_view(), name='list_queries'),
    path('queries/create/', CreateQueryView.as_view(), name='query_create'),
    path('queries/<int:query_id>/', QueryView.as_view(), name='query_detail'),
    path('queries/<int:query_id>/download/', DownloadQueryView.as_view(), name='download_query'),
    path('queries/<int:pk>/delete/', DeleteQueryView.as_view(), name='query_delete'),
    path('logs/', ListQueryLogView.as_view(), name='explorer_logs'),
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
