from django.contrib import admin
from .models import (
    NotificationMethod,
    NotificationRule,
    NotificationHistory,
    UserNotificationPreferences,
    Notification,
    NotificationSchedule,
)


@admin.register(NotificationMethod)
class NotificationMethodAdmin(admin.ModelAdmin):
    list_display = ("method", "description")
    search_fields = ("method",)
    list_filter = ("method",)


@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "trigger", "is_active", "priority")
    search_fields = ("name", "trigger")
    list_filter = ("trigger", "is_active")
    filter_horizontal = ("notification_methods",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "trigger",
                    "condition",
                    "notification_methods",
                    "is_active",
                    "priority",
                )
            },
        ),
        (
            "Templates",
            {
                "fields": ("email_template", "sms_template", "voice_template"),
            },
        ),
    )


@admin.register(NotificationHistory)
class NotificationHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "rule", "method", "status", "sent_at")
    search_fields = ("user__email", "rule__name", "status")
    list_filter = ("status", "method")
    readonly_fields = ("sent_at",)


@admin.register(UserNotificationPreferences)
class UserNotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "email_notifications",
        "sms_notifications",
        "voice_notifications",
        "preferred_language",
    )
    search_fields = ("user__email",)
    list_filter = (
        "email_notifications",
        "sms_notifications",
        "voice_notifications",
        "preferred_language",
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "rule", "method", "status", "sent_at")
    search_fields = ("user__email", "rule__name", "status")
    list_filter = ("status", "method")
    readonly_fields = ("sent_at",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "rule",
                    "method",
                    "status",
                    "message_id",
                    "additional_data",
                    "sent_at",
                    "created_at",
                )
            },
        ),
    )


@admin.register(NotificationSchedule)
class NotificationScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "rule",
        "schedule_time",
        "is_recurring",
        "recurrence_interval",
        "last_sent_at",
    )
    search_fields = ("rule__name",)
    list_filter = ("is_recurring",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "rule",
                    "schedule_time",
                    "is_recurring",
                    "recurrence_interval",
                    "last_sent_at",
                )
            },
        ),
    )
