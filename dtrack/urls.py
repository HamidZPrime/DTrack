from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard import views as dashboard_views  # Import views from your dashboard app

urlpatterns = [
    # Set the root landing page to the dashboard index view
    path("admin/", dashboard_views.index, name="dashboard"),

    # Set the DRF browsable API under /api/v1/
    path("api/v1/", include("rest_framework.urls")),

    # Include other API routes if needed
    # path("api/v1/some_app/", include("some_app.urls")),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
