from datetime import timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from notifications.models import NotificationRule, Notification, NotificationHistory
from accounts.models import CustomUser
from certificates.models import Certificate

class TaskCondition(models.Model):
    CONDITION_TYPE_CHOICES = [
        ('certificate_expiry', _("Certificate Expiry Date")),
        ('profile_completion', _("Profile Completion")),
        ('email_verification', _("Email Verification")),
        ('user_activity', _("User Activity")),
        ('phone_verification', _("Phone Verification")),
        ('role_assignment', _("User Role Assignment")),
        ('custom', _("Custom Condition")),
    ]

    OPERATOR_CHOICES = [
        ('<', _("Less Than")),
        ('<=', _("Less Than or Equal")),
        ('=', _("Equal")),
        ('>=', _("Greater Than or Equal")),
        ('>', _("Greater Than")),
        ('in', _("In Range")),
    ]

    task = models.ForeignKey("ScheduledTask", on_delete=models.CASCADE, related_name="conditions",
                             verbose_name=_("Scheduled Task"))
    condition_type = models.CharField(_("Condition Type"), max_length=50, choices=CONDITION_TYPE_CHOICES)
    operator = models.CharField(_("Operator"), max_length=20, choices=OPERATOR_CHOICES)
    value = models.CharField(_("Value"), max_length=255, help_text=_("Value to compare with"))
    additional_data = models.JSONField(_("Additional Data"), null=True, blank=True,
                                       help_text=_("Any additional metadata or configurations for the condition"))

    def __str__(self):
        return f"Condition for {self.task.name}: {self.condition_type} {self.operator} {self.value}"


class ScheduledTask(models.Model):
    TASK_TYPE_CHOICES = [
        ('certificate_expiry', _("Certificate Expiry Check")),
        ('profile_verification', _("Profile Verification Check")),
        ('email_verification', _("Email Verification Check")),
        ('profile_completion', _("Profile Completion Check")),
        ('inactive_users', _("Inactive User Check")),
        ('unresolved_tickets', _("Unresolved Ticket SLA Check")),
    ]

    name = models.CharField(_("Task Name"), max_length=255)
    task_type = models.CharField(_("Task Type"), max_length=50, choices=TASK_TYPE_CHOICES)
    description = models.TextField(_("Description"), blank=True)
    notification_rule = models.ForeignKey(
        NotificationRule,
        on_delete=models.SET_NULL,
        null=True,
        related_name="scheduled_tasks",
        verbose_name=_("Notification Rule"),
        help_text=_("Select a rule for triggering notifications.")
    )
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    last_run_at = models.DateTimeField(_("Last Run At"), null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name=_("Created By"))

    custom_dates = models.JSONField(
        _("Custom Date Intervals"),
        null=True,
        blank=True,
        help_text=_("Custom date intervals in days, e.g., {'days': [30, 60, 90, 180]}")
    )

    def __str__(self):
        return self.name

    def execute_task(self):
        if not self.is_active:
            return

        # Execute task based on task type
        users = self.get_users_for_task()
        for user in users:
            # Create notification for each user based on the associated rule
            notification = Notification.objects.create(
                user=user,
                rule=self.notification_rule,
                method=self.notification_rule.notification_methods.first(),
                status='pending'
            )
            # Record in history
            NotificationHistory.objects.create(
                user=user,
                rule=self.notification_rule,
                method=notification.method,
                status='pending',
                message_id=None
            )

    def get_users_for_task(self):
        today = timezone.now().date()
        users = []

        if self.task_type == 'certificate_expiry':
            # Fetch dynamic expiry dates based on custom_dates JSON field
            expiry_dates = [
                today + timedelta(days=days) for days in self.custom_dates.get('days', [])
            ]
            users = CustomUser.objects.filter(
                certificate__expiry_date__in=expiry_dates,
                certificate__approved=True,
                certificate__verified=True,
            ).distinct()

        elif self.task_type == 'profile_completion':
            users = CustomUser.objects.filter(profile__profile_complete=False)

        elif self.task_type == 'email_verification':
            users = CustomUser.objects.filter(email_verified=False)

        return users
