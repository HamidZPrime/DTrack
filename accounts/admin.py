from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, OperatorPermission, UserActivityLog
from .utils import log_activity
from profiles.models import Profile


# Inline Profile Admin within the CustomUserAdmin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = _('Profile Details')
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    inlines = [ProfileInline]
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'email_verified', 'is_approved')
    list_filter = ('role', 'is_active', 'email_verified', 'is_approved')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone_number', 'language')}),
        (_('Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Verification & Approval'), {'fields': ('email_verified', 'is_approved', 'approval_status')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2', 'role', 'language',
                       'is_active'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    def save_model(self, request, obj, form, change):
        if change:
            action = f"User {obj.email} updated by {request.user.email}"
        else:
            action = f"User {obj.email} created by {request.user.email}"

        log_activity(
            user=request.user,
            action=action,
            additional_data={'user': obj.email},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        action = f"User {obj.email} deleted by {request.user.email}"

        log_activity(
            user=request.user,
            action=action,
            additional_data={'user': obj.email},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        super().delete_model(request, obj)


admin.site.register(CustomUser, CustomUserAdmin)


# Register the OperatorPermission model
@admin.register(OperatorPermission)
class OperatorPermissionAdmin(admin.ModelAdmin):
    list_display = ('operator', 'get_permissions', 'view_only')
    search_fields = ('operator__email',)
    filter_horizontal = ('app_level_permissions',)

    def get_permissions(self, obj):
        return ", ".join([perm.name for perm in obj.app_level_permissions.all()])
    get_permissions.short_description = "App-Level Permissions"


# Register the UserActivityLog model
@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    search_fields = ('user__email', 'action')
