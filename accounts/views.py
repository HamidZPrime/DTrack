# views.py

from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login
from django.shortcuts import redirect

class UserRegistrationView(SuccessMessageMixin, CreateView):
    """
    User registration view.
    """
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    success_message = _("Your account has been created successfully. Please check your email to verify your account.")

    def form_valid(self, form):
        response = super().form_valid(form)
        # Send email verification here
        # Example: form.instance.send_verification_email()
        return response

class UserLoginView(auth_views.LoginView):
    """
    User login view.
    """
    template_name = 'accounts/login.html'
    authentication_form = CustomAuthenticationForm

class UserLogoutView(auth_views.LogoutView):
    """
    User logout view.
    """
    next_page = reverse_lazy('login')

class PasswordResetView(auth_views.PasswordResetView):
    """
    Password reset view.
    """
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')

class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    """
    Password reset done view.
    """
    template_name = 'accounts/password_reset_done.html'

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    Password reset confirm view.
    """
    template_name = 'accounts/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """
    Password reset complete view.
    """
    template_name = 'accounts/password_reset_complete.html'
