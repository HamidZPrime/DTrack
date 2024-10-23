from django.contrib import admin
from .models import TwilioMessageLog
from django.utils.translation import gettext_lazy as _


@admin.register(TwilioMessageLog)
class TwilioMessageLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "message_type",
        "status",
        "message_sid",
        "sent_at",
        "created_at",
    )
    search_fields = ("user__email", "message_sid", "status", "message_type")
    list_filter = ("status", "message_type", "sent_at")
    readonly_fields = (
        "user",
        "message_type",
        "message_sid",
        "status",
        "error_message",
        "sent_at",
        "created_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "message_type",
                    "message_sid",
                    "status",
                    "error_message",
                    "sent_at",
                    "created_at",
                )
            },
        ),
    )

    def has_add_permission(self, request, obj=None):
        # Disabling add permission as Twilio logs should not be created manually.
        return False

    def has_change_permission(self, request, obj=None):
        # Disabling change permission to maintain data integrity.
        return False

    def has_delete_permission(self, request, obj=None):
        # Disabling delete permission as logs should remain in the system.
        return False
