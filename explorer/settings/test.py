from dotenv import find_dotenv, load_dotenv


from explorer.settings.base import *  # noqa: F403

load_dotenv(find_dotenv())

env = environ.Env()  # noqa: F405

TEST_DB_CONFIG = dj_database_url.parse(env('TEST_DATABASE_URL'))  # noqa: F405

TEST = True
DATABASES = {
    'default': TEST_DB_CONFIG,
    'alt': {
        **TEST_DB_CONFIG,
        'NAME': TEST_DB_CONFIG['NAME'] + '_alt',
        'TEST': {'NAME': TEST_DB_CONFIG['NAME'] + '_alt'},
    },
    'unregistered': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'unregistered',
        'TEST': {'NAME': 'unregistered'},
    },
}

EXPLORER_CONNECTIONS = {
    'Postgres': 'default',
    'Alt': 'alt',
}
EXPLORER_DEFAULT_CONNECTION = 'default'
EXPLORER_SCHEMA_EXCLUDE_TABLE_PREFIXES = []
