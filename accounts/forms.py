# forms.py

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form inheriting from Django's UserCreationForm.
    """

    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
        label=_("Email Address"),
    )

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "password1", "password2")
        widgets = {
            'first_name': forms.TextInput(attrs={'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'family-name'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with that email already exists."))
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match."))

        return password2

class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form inheriting from Django's AuthenticationForm.
    """
    username = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
        label=_("Email Address"),
    )

    class Meta:
        model = CustomUser
        fields = ("username", "password")

class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form.
    """
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
        label=_("Email Address"),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if not CustomUser.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError(_("There is no active user associated with this email address."))
        return email

class CustomSetPasswordForm(SetPasswordForm):
    """
    Custom set password form for password reset confirmation.
    """

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Enter a strong password."),
    )
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match."))

        return password2
