# dtrack/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Import settings
from django.conf.urls.static import static  # Import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),  # Ensure 'accounts' matches the app_name
    # Other URL patterns
]

if settings.DEBUG:
    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files during development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
