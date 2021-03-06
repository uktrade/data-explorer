"""
Django settings for data_explorer project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import os


import dj_database_url
import environ
import sentry_sdk
from django.conf.locale.en import formats as en_formats
from django.db.models.signals import class_prepared
from django.urls import reverse_lazy
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

load_dotenv()

env = environ.Env()

TEST = False
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%=g9vzldwcd9rvg5pefh%^60#wn+mecd0v0@d^9^)(f_1c7ae*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

# In our deployments we don't have this exposed directly to the Internet and have
# host-header-based routing already, so don't need Django to enforce this for us.
ALLOWED_HOSTS = ['*']

DEFAULT_SCHEMA = env.str('APP_SCHEMA', 'public')

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_COLLAPSED': True,
}

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'explorer.apps.ExplorerAppConfig',
    'dynamic_models',
    'debug_toolbar',
    'sass_processor',
    'webpack_loader',
    'authbroker_client',
]

AUTO_LOGIN = env.bool('AUTO_LOGIN', False)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
]
if AUTO_LOGIN:
    MIDDLEWARE += ['explorer.middleware.AutoLoginMiddleware']
MIDDLEWARE += [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if not AUTO_LOGIN:
    MIDDLEWARE += ['authbroker_client.middleware.ProtectAllViewsMiddleware']


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'authbroker_client.backends.AuthbrokerBackend',
]

LOGIN_URL = reverse_lazy('authbroker:login')

LOGIN_REDIRECT_URL = reverse_lazy('explorer_index')


ROOT_URLCONF = 'explorer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'explorer.context_processors.expose_multiuser_setting',
            ],
        },
    },
]

WSGI_APPLICATION = 'explorer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


def sort_database_config(database_list):
    config = {}
    for database in database_list:
        config[database['name']] = database['credentials']['uri']
    return config


MULTIUSER_DEPLOYMENT = env.bool('MULTIUSER_DEPLOYMENT', default=False)

VCAP_SERVICES = env.json('VCAP_SERVICES', {})

if VCAP_SERVICES:
    MULTIUSER_DEPLOYMENT = True
    VCAP_DATABASES = sort_database_config(VCAP_SERVICES['postgres'])

    DEFAULT_DATABASE_URL = VCAP_DATABASES[env('POSTGRES_DB')]
    DATASETS_DATABASE_URL = VCAP_DATABASES[env('DATASETS_DB')]

    DATABASES = {
        'default': dj_database_url.parse(DEFAULT_DATABASE_URL),
        'datasets': dj_database_url.parse(DATASETS_DATABASE_URL),
    }
else:
    POSTGRES_DB = env.str('POSTGRES_DB')
    POSTGRES_USER = env.str('POSTGRES_USER')
    POSTGRES_PASSWORD = env.str('POSTGRES_PASSWORD')
    POSTGRES_HOST = env.str('POSTGRES_HOST')
    POSTGRES_PORT = env.str('POSTGRES_PORT')

    DB_CONFIG = {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {'options': f'-c search_path={DEFAULT_SCHEMA}'},
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
    }

    DATASETS_DB_CONFIG = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('DATASETS_POSTGRES_DB', POSTGRES_DB),
        'USER': env.str('DATASETS_POSTGRES_USER', POSTGRES_USER),
        'PASSWORD': env.str('DATASETS_POSTGRES_PASSWORD', POSTGRES_PASSWORD),
        'HOST': env.str('DATASETS_POSTGRES_HOST', POSTGRES_HOST),
        'PORT': env.str('DATASETS_POSTGRES_PORT', POSTGRES_PORT),
    }

    DATABASES = {'default': DB_CONFIG, 'datasets': DATASETS_DB_CONFIG}

EXPLORER_CONNECTIONS = {'datasets': 'datasets'}
EXPLORER_DEFAULT_CONNECTION = 'datasets'

EXPLORER_SCHEMA_EXCLUDE_TABLE_PREFIXES = (
    'auth_',
    'contenttypes_',
    'sessions_',
    'admin_',
    'data_explorer_',
    'django',
    'dynamic_models',
)

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

STATIC_ROOT = os.path.join(BASE_DIR, '_static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, '../', 'assets',),
)

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
if DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

SASS_PROCESSOR_INCLUDE_FILE_PATTERN = r'^.+\.scss$'

SASS_OUTPUT_STYLE = 'compressed'

SASS_PROCESSOR_ENABLED = DEBUG
SASS_PROCESSOR_AUTO_INCLUDE = DEBUG

ENABLE_DEBUG_TOOLBAR = env.bool('ENABLE_DEBUG_TOOLBAR', default=DEBUG)

if DEBUG and ENABLE_DEBUG_TOOLBAR:
    import socket

    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS = [
        '127.0.0.1',
    ]
    INTERNAL_IPS += [ip[:-1] + "1"]


# authbroker config
AUTHBROKER_URL = env.str('AUTHBROKER_URL', '')
AUTHBROKER_CLIENT_ID = env.str('AUTHBROKER_CLIENT_ID', '')
AUTHBROKER_CLIENT_SECRET = env.str('AUTHBROKER_CLIENT_SECRET', '')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if env.str("SENTRY_DSN", default='') != '':
    if not MULTIUSER_DEPLOYMENT:

        def _get_pool_options(_, __):
            # We use self-signed certs in the (Data Workspace) proxy
            return {'num_pools': 2, 'cert_reqs': 'CERT_NONE'}

        sentry_sdk.transport.HttpTransport._get_pool_options = _get_pool_options

    sentry_sdk.init(env.str('SENTRY_DSN'), integrations=[DjangoIntegration()])

if not MULTIUSER_DEPLOYMENT:
    # Data Workspace Setup

    # to make clear which tables in the user schema belong to data-explorer
    # the tables are prefixed with data_explorer
    def add_db_prefix(sender, **kwargs):

        managed = sender._meta.managed
        prefix = 'data_explorer_'

        if not managed:
            return

        if not sender._meta.db_table.startswith(prefix):
            sender._meta.db_table = prefix + sender._meta.db_table

    class_prepared.connect(add_db_prefix)

    # because schema permissions remain the same during a session, asynchronous schema loading
    # is disabled. the schema cache is build only once at startup in the urls module.
    EXPLORER_TASKS_ENABLED = False
    EXPLORER_ASYNC_SCHEMA = False

    # Cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'TIMEOUT': None,  # never expire
        }
    }

else:
    # asynchronous schema loading
    EXPLORER_TASKS_ENABLED = True
    EXPLORER_ASYNC_SCHEMA = True

    # Celery
    CELERY_BROKER_URL = env.str('REDIS_URL', '')
    CELERY_ACCEPT_CONTENT = ['pickle', 'json']

    # Cache
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': env.str('REDIS_URL', ''),
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
            'TIMEOUT': 600,  # 10 min
        }
    }

# date and time formats
en_formats.SHORT_DATE_FORMAT = "d/m/Y"
en_formats.SHORT_DATETIME_FORMAT = "d/m/Y H:i"
