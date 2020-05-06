"""
Django settings for data_explorer project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import os
import environ
import dj_database_url

from dotenv import load_dotenv
load_dotenv()

env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%=g9vzldwcd9rvg5pefh%^60#wn+mecd0v0@d^9^)(f_1c7ae*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='localhost').split(',')
ALLOWED_HOSTS += ['*']


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
    'core',
    'explorer',
    'dynamic_models',
    'debug_toolbar',
    'sass_processor',
    'webpack_loader',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
]
if env.bool('AUTO_LOGIN', False):
    MIDDLEWARE += ['data_explorer.middleware.AutoLoginMiddleware']
MIDDLEWARE += [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'data_explorer.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'data_explorer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


def sort_database_config(database_list):
    config = {}
    for database in database_list:
        config[database['name']] = database['credentials']['uri']
    return config


VCAP_SERVICES = env.json('VCAP_SERVICES', {})
if VCAP_SERVICES:
    VCAP_DATABASES = sort_database_config(VCAP_SERVICES['postgres'])

    DEFAULT_DATABASE_URL = VCAP_DATABASES[env('POSTGRES_DB')]
    DATASETS_DATABASE_URL = VCAP_DATABASES[env('DATASETS_DB')]


    DATABASES = {
        'default': dj_database_url.parse(DEFAULT_DATABASE_URL),
        'datasets': dj_database_url.parse(DATASETS_DATABASE_URL),
    }
else:
    DEFAULT_SCHEMA = env.str('APP_SCHEMA', 'public')
    DB_CONFIG = {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
                'options': f'-c search_path={DEFAULT_SCHEMA}'
        },
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
    }
    DATABASES = {
        'default': DB_CONFIG,
        'datasets': DB_CONFIG
    }

EXPLORER_CONNECTIONS = {'Default': 'default', 'Datasets': 'datasets'}
EXPLORER_DEFAULT_CONNECTION = 'datasets'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
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

ASSETS_FOLDER = os.path.join(BASE_DIR, '_static')

STATIC_ROOT = ASSETS_FOLDER

STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    ('data_explorer', STATIC_FOLDER),
]

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'data_explorer/js/bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

SASS_PROCESSOR_INCLUDE_DIRS = [
    STATIC_FOLDER,
]

if DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

SASS_PROCESSOR_INCLUDE_FILE_PATTERN = r'^.+\.scss$'

SASS_OUTPUT_STYLE = 'compressed'

SASS_PROCESSOR_ENABLED = DEBUG
SASS_PROCESSOR_AUTO_INCLUDE = DEBUG

# Internal IPs required by the django debug tool bar
INTERNAL_IPS = [
    '127.0.0.1',
]

# If using docker and you would like to use the tool bar
# remove comments to add the ip to the internal ips list

if DEBUG:
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1"]
