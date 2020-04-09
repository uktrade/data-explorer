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
import socket

env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%=g9vzldwcd9rvg5pefh%^60#wn+mecd0v0@d^9^)(f_1c7ae*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='localhost').split(',')


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
    'explorer',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
    DB_CONFIG = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
    }
    DATABASES = {
        'default': DB_CONFIG,
        'datasets': DB_CONFIG
    }


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
]

ASSETS_FOLDER = os.path.join(BASE_DIR, '_static')

STATIC_ROOT = ASSETS_FOLDER

STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

EXPLORER_CONNECTIONS = {'default db': 'datasets'}
EXPLORER_DEFAULT_CONNECTION = 'datasets'

# Internal IPs required by the django debug tool bar
INTERNAL_IPS = [
    '127.0.0.1',
]

# If using docker and you would like to not use the tool bar
# comment out adding the ip to the internal ips list
ip = socket.gethostbyname(socket.gethostname())
INTERNAL_IPS += [ip[:-1] + "1"]
