# accounts/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator, validate_email
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="A valid email address is required.")
    confirm_email = forms.EmailField(required=True, help_text="Please confirm your email.")
    role = forms.ChoiceField(choices=[('enduser', 'End User'), ('supplier', 'Supplier')], required=True)
    language = forms.ChoiceField(choices=[('en', 'English'), ('ar', 'Arabic')], required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'confirm_email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'role', 'language')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Invalid email address.")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_confirm_email(self):
        email = self.cleaned_data.get("email")
        confirm_email = self.cleaned_data.get("confirm_email")
        if email != confirm_email:
            raise ValidationError("Emails do not match.")
        return confirm_email

    def clean_password2(self):
        password = self.cleaned_data.get('password1')
        confirm_password = self.cleaned_data.get('password2')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return confirm_password

class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True, help_text="Enter your registered email.")
    password = forms.CharField(widget=forms.PasswordInput, required=True, help_text="Enter your password.")
