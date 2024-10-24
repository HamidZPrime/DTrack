from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("qr/", include("qr_generator.urls", namespace="qr_generator")),  # Include qr_generator URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
