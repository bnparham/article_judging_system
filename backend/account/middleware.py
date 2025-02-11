import redis
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

redis_client = redis.StrictRedis.from_url(settings.CACHES["default"]["LOCATION"], decode_responses=True)

class OneSessionPerUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_session_key = f"user_session:{request.user.pk}"
            session_id = redis_client.get(user_session_key)

            if session_id and session_id != request.session.session_key:
                logout(request)
                messages.warning(request, "دستگاه دیگری به حساب کاربری شما وارد شده است")
                return redirect("admin:login")  # Redirect to login page

        response = self.get_response(request)
        return response
