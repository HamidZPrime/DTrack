# qr_generator/urls.py

from django.urls import path
from . import views

app_name = "qr_generator"  # Define the app_name

urlpatterns = [
    path('supplier/<uuid:qr_token>/', views.supplier_detail, name='supplier_detail'),
    path('product/<uuid:qr_token>/', views.product_detail, name='product_detail'),
    path('certificate/<uuid:qr_token>/', views.certificate_detail, name='certificate_detail'),
]
