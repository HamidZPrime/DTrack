from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),  # Enable Django admin
    path('accounts/', include('accounts.urls', namespace='account')),  # Include the accounts app URLs
    path('', include('dashboard.urls')),  # Use the dashboard app for home
]
