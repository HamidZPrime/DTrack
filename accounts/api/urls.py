from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("operator-permissions/", views.OperatorPermissionView.as_view(), name="operator-permissions"),
    path("verify-email/<uuid:token>/", views.EmailVerificationView.as_view(), name="verify-email"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("2fa/", views.TwoFactorAuthView.as_view(), name="2fa"),
]
