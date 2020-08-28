"""
WSGI config for data_explorer project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from paste.translogger import TransLogger

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'explorer.settings.base')

application = TransLogger(get_wsgi_application())
