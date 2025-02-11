import redis
from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth import authenticate, login
from django.contrib.sessions.models import Session
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.contrib import admin
from django.apps import apps

redis_client = redis.StrictRedis.from_url(settings.CACHES["default"]["LOCATION"], decode_responses=True)


class CustomAdminSite(AdminSite):
    site_header = "Custom Admin"
    site_title = "Custom Admin Portal"
    index_title = "Welcome to Custom Admin"

    def login(self, request, extra_context=None):
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_active:
                user_session_key = f"user_session:{user.pk}"
                existing_session_id = redis_client.get(user_session_key)

                if existing_session_id:
                    # Remove old session if exists
                    Session.objects.filter(session_key=existing_session_id).delete()

                # Create new session
                login(request, user)
                redis_client.set(user_session_key, request.session.session_key)

                return redirect("admin:index")  # Redirect to admin dashboard

        return super().login(request, extra_context)

# Create a new instance of CustomAdminSite
custom_admin_site = CustomAdminSite(name="custom_admin")

# Register all models that were registered in admin.site
for model, model_admin in admin.site._registry.items():
    custom_admin_site.register(model, model_admin.__class__)