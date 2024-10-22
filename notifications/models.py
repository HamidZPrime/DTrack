from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail

import accounts.models
from notification_templates.models import EmailTemplate, SMSTemplate, VoiceTemplate
from twilio.rest import Client

# Twilio setup
TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER = settings.TWILIO_PHONE_NUMBER

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


class NotificationMethod(models.Model):
    METHOD_CHOICES = (
        ('email', _("Email")),
        ('sms', _("SMS")),
        ('voice', _("Voice Call")),
    )

    method = models.CharField(_("Notification Method"), max_length=20, choices=METHOD_CHOICES, unique=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Notification Method")
        verbose_name_plural = _("Notification Methods")

    def __str__(self):
        return self.method


class NotificationRule(models.Model):
    RULE_TRIGGER_CHOICES = (
        ('expiry', _("Certificate Expiry")),
        ('approval', _("Certificate Approval")),
        ('reminder', _("Reminder")),
        ('custom', _("Custom Rule")),
        ('email_verification', _("Email Verification Reminder")),
        ('profile_completion', _("Profile Completion Reminder")),
        ('task', _("Task Reminder")),
    )

    name = models.CharField(_("Rule Name"), max_length=255)
    trigger = models.CharField(_("Trigger"), max_length=50, choices=RULE_TRIGGER_CHOICES)
    notification_methods = models.ManyToManyField(NotificationMethod, related_name="notification_rules", verbose_name=_("Notification Methods"))
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="notification_rules", verbose_name=_("Email Template"))
    sms_template = models.ForeignKey(SMSTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="notification_rules", verbose_name=_("SMS Template"))
    voice_template = models.ForeignKey(VoiceTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="notification_rules", verbose_name=_("Voice Template"))
    condition = models.CharField(_("Condition"), max_length=255, blank=True, help_text=_("Custom condition logic, e.g., 'expiry_date < today + 3 months'"))
    is_active = models.BooleanField(_("Is Active"), default=True)
    priority = models.PositiveIntegerField(_("Priority"), default=1, help_text=_("Higher numbers indicate higher priority."))

    class Meta:
        verbose_name = _("Notification Rule")
        verbose_name_plural = _("Notification Rules")

    def __str__(self):
        return self.name


class NotificationHistory(models.Model):
    user = models.ForeignKey(accounts.models.CustomUser, on_delete=models.CASCADE, related_name="notification_history", verbose_name=_("User"))
    rule = models.ForeignKey(NotificationRule, on_delete=models.SET_NULL, null=True, verbose_name=_("Notification Rule"))
    method = models.ForeignKey(NotificationMethod, on_delete=models.SET_NULL, null=True, verbose_name=_("Notification Method"))
    status = models.CharField(_("Status"), max_length=20, choices=[('sent', _("Sent")), ('failed', _("Failed"))], default='sent')
    message_id = models.CharField(_("Message ID"), max_length=100, blank=True)
    sent_at = models.DateTimeField(_("Sent At"), auto_now_add=True)
    additional_data = models.JSONField(_("Additional Data"), null=True, blank=True)

    class Meta:
        verbose_name = _("Notification History")
        verbose_name_plural = _("Notification Histories")
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['method']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Notification to {self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user}"


class UserNotificationPreferences(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences", verbose_name=_("User"))
    email_notifications = models.BooleanField(_("Email Notifications"), default=True)
    sms_notifications = models.BooleanField(_("SMS Notifications"), default=True)
    voice_notifications = models.BooleanField(_("Voice Notifications"), default=False)
    preferred_language = models.CharField(_("Preferred Language"), max_length=5, choices=[('en', 'English'), ('ar', 'Arabic')], default='en')

    class Meta:
        verbose_name = _("User Notification Preferences")
        verbose_name_plural = _("User Notification Preferences")

    def __str__(self):
        return f"Notification Preferences for {self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user}"


class Notification(models.Model):
    user = models.ForeignKey(
        accounts.models.CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("User")
    )
    rule = models.ForeignKey(NotificationRule, on_delete=models.SET_NULL, null=True, related_name="notifications", verbose_name=_("Notification Rule"))
    method = models.ForeignKey(NotificationMethod, on_delete=models.SET_NULL, null=True, related_name="notifications", verbose_name=_("Notification Method"))
    status = models.CharField(_("Status"), max_length=20, choices=[('sent', _("Sent")), ('failed', _("Failed")), ('pending', _("Pending"))], default='pending')
    sent_at = models.DateTimeField(_("Sent At"), null=True, blank=True)
    message_id = models.CharField(_("Message ID"), max_length=100, blank=True)
    additional_data = models.JSONField(_("Additional Data"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Notification to {self.user.get_full_name() if hasattr(self.user, 'get_full_name') else self.user}"

    def send_notification(self):
        if self.method.method == 'email':
            self.send_email_notification()
        elif self.method.method == 'sms':
            self.send_sms_notification()
        elif self.method.method == 'voice':
            self.send_voice_notification()

    def send_email_notification(self):
        """
        Send email using the selected template and user preferences.
        """
        if self.rule.email_template:
            subject = self.rule.email_template.subject
            body = self.rule.email_template.html_body
            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [self.user.email])
                self.status = 'sent'
                NotificationHistory.objects.create(user=self.user, rule=self.rule, method=self.method, status='sent', message_id=self.message_id)
            except Exception as e:
                self.status = 'failed'
                self.additional_data = {"error": str(e)}
            finally:
                self.sent_at = timezone.now()
                self.save()

    def send_sms_notification(self):
        """
        Send SMS using Twilio and the selected template and user preferences.
        """
        if self.rule.sms_template and self.user.phone_number:
            try:
                message = client.messages.create(
                    body=self.rule.sms_template.body,
                    from_=TWILIO_PHONE_NUMBER,
                    to=self.user.phone_number
                )
                self.message_id = message.sid
                self.status = 'sent'
                NotificationHistory.objects.create(user=self.user, rule=self.rule, method=self.method, status='sent', message_id=message.sid)
            except Exception as e:
                self.status = 'failed'
                self.additional_data = {"error": str(e)}
            finally:
                self.sent_at = timezone.now()
                self.save()

    def send_voice_notification(self):
        """
        Make a voice call using Twilio and play the recorded message.
        """
        if self.rule.voice_template and self.user.phone_number:
            try:
                call = client.calls.create(
                    twiml=f'<Response><Play>{self.rule.voice_template.message_file.url}</Play></Response>',
                    from_=TWILIO_PHONE_NUMBER,
                    to=self.user.phone_number
                )
                self.message_id = call.sid
                self.status = 'sent'
                NotificationHistory.objects.create(user=self.user, rule=self.rule, method=self.method, status='sent', message_id=call.sid)
            except Exception as e:
                self.status = 'failed'
                self.additional_data = {"error": str(e)}
            finally:
                self.sent_at = timezone.now()
                self.save()


class NotificationSchedule(models.Model):
    rule = models.ForeignKey(NotificationRule, on_delete=models.CASCADE, related_name="schedules", verbose_name=_("Notification Rule"))
    schedule_time = models.DateTimeField(_("Schedule Time"), help_text=_("Time to send the notification"))
    is_recurring = models.BooleanField(_("Is Recurring"), default=False)
    recurrence_interval = models.PositiveIntegerField(_("Recurrence Interval (days)"), default=0, help_text=_("Interval in days for recurring notifications"))
    last_sent_at = models.DateTimeField(_("Last Sent At"), null=True, blank=True)

    class Meta:
        verbose_name = _("Notification Schedule")
        verbose_name_plural = _("Notification Schedules")

    def __str__(self):
        return f"Schedule for {self.rule.name} at {self.schedule_time}"
