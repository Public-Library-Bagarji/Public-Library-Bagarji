from django.contrib.auth import logout
from django.contrib.auth.models import User

class LogoutDeletedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                User.objects.get(pk=user.pk)
            except User.DoesNotExist:
                logout(request)
        return self.get_response(request) 