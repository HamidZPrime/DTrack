# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.views import View
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .forms import UserRegistrationForm, UserLoginForm
from .models import EmailVerificationToken, CustomUser
from django.contrib.auth.views import LogoutView

class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'account/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                selected_role = form.cleaned_data.get('role')
                user = form.save(commit=False)
                user.is_active = False  # User inactive until email verification

                if selected_role in ['supplier', 'enduser']:
                    user.role = selected_role
                else:
                    raise ValidationError(_("Invalid role selected."))

                user.save()

                # Generate an email verification token
                token = EmailVerificationToken.objects.create(
                    user=user,
                    expires_at=timezone.now() + timezone.timedelta(hours=24)
                )
                token.send_verification_email()
                messages.success(request, _("A verification email has been sent. Please check your inbox."))
                return redirect('account:login')
            except ValidationError as e:
                messages.error(request, e)
            except Exception as e:
                messages.error(request, f"Error during registration: {e}")
        else:
            for error in form.errors.values():
                messages.error(request, error)
        return render(request, 'account/register.html', {'form': form})

class LoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'account/login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if not user.email_verified:
                    messages.error(request, _("Please verify your email first."))
                else:
                    login(request, user)
                    messages.success(request, _("You have successfully logged in."))
                    return redirect('home')
            else:
                messages.error(request, _("Invalid email or password."))
        else:
            for error in form.errors.values():
                messages.error(request, error)
        return render(request, 'account/login.html', {'form': form})

class VerifyEmailView(View):
    def get(self, request, token):
        try:
            verification_token = EmailVerificationToken.objects.get(token=token, expires_at__gt=timezone.now())
            user = verification_token.user
            user.is_active = True
            user.email_verified = True
            user.save()
            verification_token.delete()
            messages.success(request, _("Your email has been verified successfully."))
            return redirect('account:login')
        except EmailVerificationToken.DoesNotExist:
            messages.error(request, _("Invalid or expired verification token."))
            return redirect('account:register')

class CustomLogoutView(LogoutView):
    next_page = 'account:login'
