# accounts/urls.py
from django.urls import path
from .views import RegisterView, LoginView, VerifyEmailView, CustomLogoutView

app_name = 'account'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'),
]
