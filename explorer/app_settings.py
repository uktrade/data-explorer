from django.conf import settings

EXPLORER_CONNECTIONS = getattr(settings, 'EXPLORER_CONNECTIONS', {})
EXPLORER_DEFAULT_CONNECTION = getattr(settings, 'EXPLORER_DEFAULT_CONNECTION', None)

EXPLORER_DEFAULT_ROWS = getattr(settings, 'EXPLORER_DEFAULT_ROWS', 1000)
EXPLORER_QUERY_TIMEOUT_MS = getattr(settings, 'EXPLORER_QUERY_TIMEOUT_MS', 60000)
EXPLORER_DEFAULT_DOWNLOAD_ROWS = getattr(settings, 'EXPLORER_DEFAULT_DOWNLOAD_ROWS', 1000)

EXPLORER_SCHEMA_EXCLUDE_TABLE_PREFIXES = getattr(
    settings,
    'EXPLORER_SCHEMA_EXCLUDE_TABLE_PREFIXES',
    ('auth_', 'contenttypes_', 'sessions_', 'admin_', 'explorer_', 'django', 'dynamic_models',),
)

EXPLORER_SCHEMA_INCLUDE_TABLE_PREFIXES = getattr(
    settings, 'EXPLORER_SCHEMA_INCLUDE_TABLE_PREFIXES', None
)
EXPLORER_SCHEMA_INCLUDE_VIEWS = getattr(settings, 'EXPLORER_SCHEMA_INCLUDE_VIEWS', False)

EXPLORER_RECENT_QUERY_COUNT = getattr(settings, 'EXPLORER_RECENT_QUERY_COUNT', 10)
EXPLORER_ASYNC_SCHEMA = getattr(settings, 'EXPLORER_ASYNC_SCHEMA', False)

EXPLORER_DATA_EXPORTERS = getattr(
    settings,
    'EXPLORER_DATA_EXPORTERS',
    [
        ('csv', 'explorer.exporters.CSVExporter'),
        ('excel', 'explorer.exporters.ExcelExporter'),
        ('json', 'explorer.exporters.JSONExporter'),
    ],
)
CSV_DELIMETER = getattr(settings, "EXPLORER_CSV_DELIMETER", ",")

# API access
EXPLORER_TOKEN = getattr(settings, 'EXPLORER_TOKEN', 'CHANGEME')

# These are callable to aid testability by dodging the settings cache.
# There is surely a better pattern for this, but this'll hold for now.


def get_explorer_user_query_views():
    return getattr(settings, 'EXPLORER_USER_QUERY_VIEWS', {})


# Async task related. Note that the EMAIL_HOST settings must be set up for email to work.
ENABLE_TASKS = getattr(settings, "EXPLORER_TASKS_ENABLED", False)
UNSAFE_RENDERING = getattr(settings, "EXPLORER_UNSAFE_RENDERING", False)

TABLE_BROWSER_LIMIT = getattr(settings, "EXPLORER_TABLE_BROWSER_LIMIT", 20)
