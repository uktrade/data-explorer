import dj_database_url
import environ
from dotenv import find_dotenv, load_dotenv

from explorer.settings.base import *  # noqa

load_dotenv(find_dotenv())

env = environ.Env()

TEST = True
DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'tmp', 'TEST': {'NAME': 'tmp'}},
    'postgres': dj_database_url.parse(env('TEST_DATABASE_URL')),
    'alt': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'tmp2', 'TEST': {'NAME': 'tmp2'}},
    'not_registered': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tmp3',
        'TEST': {'NAME': 'tmp3'},
    },
}

EXPLORER_CONNECTIONS = {'Postgres': 'postgres', 'SQLite': 'default', 'Another': 'alt'}
EXPLORER_DEFAULT_CONNECTION = 'default'
EXPLORER_SCHEMA_EXCLUDE_TABLE_PREFIXES = []
