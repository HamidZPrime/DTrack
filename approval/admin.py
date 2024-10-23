from django.contrib import admin
from .models import ApprovalRequest, ApprovalLog, ApprovalAction


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = (
        "requester",
        "entity_type",
        "entity_id",
        "status",
        "reviewed_by",
        "request_time",
    )
    list_filter = ("entity_type", "status")
    search_fields = ("requester__email", "entity_type", "status")
    readonly_fields = ("request_time",)

    fieldsets = (
        (
            None,
            {"fields": ("requester", "entity_type", "entity_id", "status", "comments")},
        ),
        (
            "Review Info",
            {
                "fields": ("reviewed_by", "reviewed_at"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("request_time",),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Include additional filtering or ordering if needed
        return queryset


@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = (
        "approval_request",
        "previous_status",
        "new_status",
        "action_taken_by",
        "action_time",
    )
    list_filter = ("new_status",)
    search_fields = ("approval_request__entity_type", "action_taken_by__email")
    readonly_fields = ("action_time",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "approval_request",
                    "previous_status",
                    "new_status",
                    "action_taken_by",
                    "comments",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("action_time",),
            },
        ),
    )


@admin.register(ApprovalAction)
class ApprovalActionAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_default")
    search_fields = ("name",)
    list_filter = ("is_default",)

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "description", "is_default"),
            },
        ),
    )
