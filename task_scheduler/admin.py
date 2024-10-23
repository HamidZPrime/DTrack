from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ScheduledTask, TaskCondition

class TaskConditionInline(admin.TabularInline):
    """
    Inline interface for managing conditions within a scheduled task.
    """
    model = TaskCondition
    extra = 1
    fields = ('condition_type', 'operator', 'value', 'additional_data')
    verbose_name_plural = _("Task Conditions")


class ScheduledTaskAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Scheduled Tasks.
    """
    list_display = ('name', 'task_type', 'is_active', 'created_at', 'last_run_at', 'created_by')
    list_filter = ('task_type', 'is_active')
    search_fields = ('name', 'task_type', 'created_by__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_run_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'task_type', 'description', 'notification_rule', 'is_active', 'created_by')
        }),
        (_('Custom Dates'), {
            'fields': ('custom_dates',),
            'description': _("Custom date intervals in days, e.g., {'days': [30, 60, 90, 180]}"),
        }),
        (_('Important Dates'), {
            'fields': ('created_at', 'last_run_at'),
        }),
    )
    inlines = [TaskConditionInline]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Log task deletions or trigger any custom clean-up required.
        """
        # Custom actions can be implemented here if required
        super().delete_model(request, obj)


class TaskConditionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Task Conditions separately.
    """
    list_display = ('task', 'condition_type', 'operator', 'value')
    list_filter = ('condition_type', 'operator')
    search_fields = ('task__name', 'condition_type', 'value')
    ordering = ('task',)
    fieldsets = (
        (None, {
            'fields': ('task', 'condition_type', 'operator', 'value', 'additional_data')
        }),
    )

admin.site.register(ScheduledTask, ScheduledTaskAdmin)
admin.site.register(TaskCondition, TaskConditionAdmin)
