# accounts/admins.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission
from .models import CustomUser, OperatorPermission, UserActivityLog, EmailVerificationToken
from profiles.models import Profile

<<<<<<< HEAD
# Unregister the default Group admin to customize it later (if needed)
admin.site.unregister(Group)


=======
# Inline Profile Admin within the CustomUserAdmin
>>>>>>> heroku/main
class ProfileInline(admin.StackedInline):
    """
    Inline admin descriptor for Profile model.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = _("Profile Details")
    fk_name = "user"


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Admin panel configuration for CustomUser model.
    """
    model = CustomUser
    inlines = (ProfileInline,)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "email_verified",
        "is_approved",
        "date_joined",
        "last_login",
    )
    list_filter = ("role", "is_active", "email_verified", "is_approved", "date_joined")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")

    # Make 'last_login' and 'date_joined' read-only fields
    readonly_fields = ("date_joined", "last_login")

    # Define the fields to be displayed in the admin form
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name", "phone_number", "language")}),
        (_("Permissions"), {
            "fields": (
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "is_approved",
                "approval_status",
                "groups",
                "user_permissions",
            ),
        }),
        (_("Important Dates"), {"fields": ("date_joined", "last_login")}),
        (_("Verification"), {"fields": ("email_verified",)}),
    )

    # Fields to display when creating a new user via the admin
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "first_name",
                "last_name",
                "phone_number",
                "language",
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "is_approved",
                "approval_status",
                "email_verified",
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
<<<<<<< HEAD
        super().save_model(request, obj, form, change)
        action = "updated" if change else "created"
        UserActivityLog.objects.create(
            user=request.user,
            action=f"User {obj.email} {action} by admin {request.user.email}",
            ip_address=self._get_client_ip(request),
            additional_data={"user_id": obj.id},
        )

    def delete_model(self, request, obj):
        UserActivityLog.objects.create(
=======
        is_new = not obj.pk
        super().save_model(request, obj, form, change)

        # Create a profile for new users after they are saved
        if is_new and obj.role == 'supplier':
            Profile.objects.create(user=obj)

        action = f"User {obj.email} {'updated' if change else 'created'} by {request.user.email}"
        log_activity(
            user=request.user,
            action=action,
            additional_data={'user': obj.email},
            ip_address=request.META.get('REMOTE_ADDR')
        )

    def delete_model(self, request, obj):
        action = f"User {obj.email} deleted by {request.user.email}"
        log_activity(
>>>>>>> heroku/main
            user=request.user,
            action=f"User {obj.email} deleted by admin {request.user.email}",
            ip_address=self._get_client_ip(request),
            additional_data={"user_id": obj.id},
        )
        super().delete_model(request, obj)

<<<<<<< HEAD
    @staticmethod
    def _get_client_ip(request):
        """
        Retrieve the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@admin.register(OperatorPermission)
class OperatorPermissionAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for OperatorPermission model.
    """
    list_display = ("operator", "view_only", "display_permissions")
    search_fields = ("operator__email", "operator__first_name", "operator__last_name")
    filter_horizontal = ("app_level_permissions",)
    list_filter = ("view_only",)

    def display_permissions(self, obj):
        """
        Display app-level permissions in a readable format.
        """
        permissions = obj.app_level_permissions.all()
        if permissions:
            return ", ".join([perm.name for perm in permissions])
        return _("No Permissions Assigned")

    display_permissions.short_description = _("App-Level Permissions")


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for UserActivityLog model.
    """
    list_display = ("user", "action_short", "timestamp", "ip_address")
    search_fields = ("user__email", "action", "ip_address")
    list_filter = ("timestamp",)
    readonly_fields = ("user", "action", "timestamp", "ip_address", "additional_data")
    date_hierarchy = "timestamp"

    def action_short(self, obj):
        """
        Shorten the action text for display purposes.
        """
        return (obj.action[:75] + '...') if len(obj.action) > 75 else obj.action

    action_short.short_description = _("Action")


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for EmailVerificationToken model.
    """
    list_display = ("user", "token", "created_at", "expires_at", "is_valid")
    search_fields = ("user__email", "token")
    list_filter = ("created_at", "expires_at")
    readonly_fields = ("token", "created_at", "expires_at")

    def is_valid(self, obj):
        """
        Indicate whether the token is still valid.
        """
        return obj.is_valid()

    is_valid.boolean = True
    is_valid.short_description = _("Is Valid")


# Optional: Customize the Group admin interface if needed
@admin.register(Group)
class CustomGroupAdmin(admin.ModelAdmin):
    """
    Custom admin panel for the Group model.
    """
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("permissions",)


# Register the Permission model for better management
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Permission model.
    """
    list_display = ("name", "content_type", "codename")
    search_fields = ("name", "codename")
    list_filter = ("content_type",)
=======

admin.site.register(CustomUser, CustomUserAdmin)
>>>>>>> heroku/main
