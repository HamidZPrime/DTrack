from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views

# Redirect to the DRF API login if the root is accessed
def api_root(_request):
    return HttpResponseRedirect("/api-auth/login/")  # Redirect to the login page

urlpatterns = [
    # Home root that redirects to DRF login
    path("", api_root, name="api-root"),

    # DRF authentication and browsable API
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),

    # Login and Logout URLs for Django authentication
    path("accounts/login/", auth_views.LoginView.as_view(), name='login'),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name='logout'),

    # Include your other apps' URL configurations
    path("api/accounts/", include("accounts.urls")),
]

# Serving media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
