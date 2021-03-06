from django.contrib.auth import get_backends, login
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin

USERNAME = 'user'


class AutoLoginMiddleware(MiddlewareMixin):
    """
        Middleware to login user automatically when the application
        is running as part of another environment
    """

    def process_request(self, request):
        if hasattr(request, 'user'):
            return

        User.objects.filter(username=USERNAME).exists() or User.objects.create_user(USERNAME)
        user = User.objects.filter(username=USERNAME)
        backend = get_backends()[0]
        user = user[0]
        user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
        login(request, user)
