from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Custom storage for voice messages
voice_storage = FileSystemStorage(location="media/voice_messages/")


class TemplateCategory(models.Model):
    """
    Model to categorize templates based on their purpose.
    E.g., Notification, Welcome Email, Reminder, etc.
    """

    name = models.CharField(_("Category Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Template Category")
        verbose_name_plural = _("Template Categories")

    def __str__(self):
        return self.name


class EmailTemplate(models.Model):
    """
    Model to define HTML email templates.
    """

    name = models.CharField(_("Template Name"), max_length=255, unique=True)
    subject = models.CharField(_("Email Subject"), max_length=255)
    html_body = models.TextField(
        _("HTML Body"), help_text=_("HTML format email content")
    )
    text_body = models.TextField(
        _("Text Body"), blank=True, help_text=_("Optional plain text version")
    )
    category = models.ForeignKey(
        TemplateCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="email_templates",
        verbose_name=_("Category"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Created By"),
    )

    class Meta:
        verbose_name = _("Email Template")
        verbose_name_plural = _("Email Templates")

    def __str__(self):
        return self.name


class SMSTemplate(models.Model):
    """
    Model to define SMS templates.
    """

    name = models.CharField(_("Template Name"), max_length=255, unique=True)
    body = models.CharField(
        _("SMS Body"), max_length=160, help_text=_("160 characters max for SMS")
    )
    category = models.ForeignKey(
        TemplateCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sms_templates",
        verbose_name=_("Category"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Created By"),
    )

    class Meta:
        verbose_name = _("SMS Template")
        verbose_name_plural = _("SMS Templates")

    def __str__(self):
        return self.name


class VoiceTemplate(models.Model):
    """
    Model to define recorded voice message templates.
    """

    name = models.CharField(_("Message Name"), max_length=255, unique=True)
    message_file = models.FileField(
        _("Recorded Voice Message"), storage=voice_storage, upload_to="voice_messages/"
    )
    description = models.TextField(_("Description"), blank=True)
    category = models.ForeignKey(
        TemplateCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="voice_templates",
        verbose_name=_("Category"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Created By"),
    )

    class Meta:
        verbose_name = _("Voice Template")
        verbose_name_plural = _("Voice Templates")

    def __str__(self):
        return self.name


class TemplateTag(models.Model):
    """
    Model to tag templates for easier categorization and filtering.
    """

    name = models.CharField(_("Tag Name"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Template Tag")
        verbose_name_plural = _("Template Tags")

    def __str__(self):
        return self.name


class TemplateUsage(models.Model):
    """
    Model to log the usage of each template in notifications or other areas.
    """

    template_name = models.CharField(_("Template Name"), max_length=255)
    used_in = models.CharField(
        _("Used In"),
        max_length=255,
        help_text=_("E.g., Certificate Expiry Notification"),
    )
    used_at = models.DateTimeField(_("Used At"), auto_now_add=True)
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Used By"),
    )

    class Meta:
        verbose_name = _("Template Usage")
        verbose_name_plural = _("Template Usages")

    def __str__(self):
        return f"Used {self.template_name} for {self.used_in}"
