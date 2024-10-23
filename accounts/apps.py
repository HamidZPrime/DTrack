# accounts/apps.py

from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        """
        Override this method to include any application-specific initialization.
        Import and register signals here to ensure they are connected when the app is ready.
        """
        from . import signals  # Import signal handlers to ensure they are registered
