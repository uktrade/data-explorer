"""data_explorer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import threading

from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from explorer.tasks import build_schema_cache_async

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('explorer.urls')),
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Build schema cache at startup in background
if not settings.MULTIUSER_DEPLOYMENT:
    def build_schema():
        for alias in settings.EXPLORER_CONNECTIONS:
            build_schema_cache_async(alias)
    t = threading.Thread(target=build_schema, args=(), kwargs={})
    t.setDaemon(True)
    t.start()
