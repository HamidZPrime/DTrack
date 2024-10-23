from django.contrib import admin
from .models import Profile
from django.utils.translation import gettext_lazy as _


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_full_name",
        "profile_complete",
        "date_of_birth",
        "city",
        "country",
        "phone_verified",
    )
    list_filter = (
        "profile_complete",
        "phone_verified",
        "country",
        "user__role",
        "user__is_active",
        "user__date_joined",
    )
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "company_name",
        "city",
        "industry",
    )
    readonly_fields = ("date_created", "date_updated")
    autocomplete_fields = ["user"]

    fieldsets = (
        (None, {"fields": ("user", "profile_picture")}),
        (
            "Personal Information",
            {"fields": ("date_of_birth", "address", "city", "country", "postal_code")},
        ),
        ("Verification", {"fields": ("phone_verified",)}),
        (
            "Supplier Information",
            {
                "fields": (
                    "company_name",
                    "company_registration_number",
                    "vat_number",
                    "supplier_type",
                    "industry",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Admin Notes", {"fields": ("admin_notes",), "classes": ("collapse",)}),
        (
            "Operator Information",
            {"fields": ("operator_level",), "classes": ("collapse",)},
        ),
        (
            "End User Preferences",
            {"fields": ("preferred_language", "interests"), "classes": ("collapse",)},
        ),
        (
            "Additional Information",
            {"fields": ("profile_complete", "date_created", "date_updated")},
        ),
    )

    def get_queryset(self, request):
        """
        Customizes the queryset to optimize performance, filter data appropriately, and prefetch related fields.
        """
        # Fetch related fields to reduce database hits (pre-fetching related user information)
        queryset = (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("user__groups")
        )

        # Example additional filtering: Only show active users or profiles based on some condition
        if not request.user.is_superuser:
            queryset = queryset.filter(
                user__is_active=True
            )  # Example: Non-superusers only see active users' profiles

        return queryset

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    get_full_name.short_description = _("Full Name")

    def save_model(self, request, obj, form, change):
        """
        Override save_model to implement additional checks or automatic updates.
        """
        # Automatically mark profile as complete if all mandatory fields are filled
        if not obj.profile_complete:
            obj.mark_complete()

        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Override delete_model to implement logic for deletion logging or soft deletes.
        """
        # Add any custom deletion logic here (e.g., soft deletes, audit logging)
        super().delete_model(request, obj)

    def has_view_or_change_permission(self, request, obj=None):
        """
        Override permissions to customize access based on user roles or status.
        """
        if request.user.is_superuser:
            return True
        # Add custom permission checks for other roles here
        return super().has_view_or_change_permission(request, obj)
