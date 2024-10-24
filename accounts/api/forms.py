from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "password"]
        labels = {
            "email": _("Email Address"),
            "first_name": _("First Name"),
            "last_name": _("Last Name"),
            "password": _("Password"),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
