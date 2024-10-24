from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from typing import Any

# Swagger schema view configuration
schema_view: Any = get_schema_view(
    openapi.Info(
        title="DTrack API",
        default_version='v1',
        description="API documentation for DTrack",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@dtrack.zprime.ai"),
        license=openapi.License(name="Commercial License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    # DRF authentication and browsable API
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # Swagger and ReDoc documentation URLs
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("redoc/", schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serving media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
