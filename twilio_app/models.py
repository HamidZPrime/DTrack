from django.db import models
from django.conf import settings
from twilio.rest import Client
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class TwilioMessageLog(models.Model):
    """
    Log of all messages sent via Twilio (SMS and Voice).
    """

    class MessageType(models.TextChoices):
        SMS = 'sms', _('SMS')
        VOICE = 'voice', _('Voice Call')

    class MessageStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SENT = 'sent', _('Sent')
        FAILED = 'failed', _('Failed')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_("User"))
    message_type = models.CharField(_("Message Type"), max_length=10, choices=MessageType.choices)
    message_sid = models.CharField(_("Message SID"), max_length=64, blank=True)
    status = models.CharField(_("Status"), max_length=20, choices=MessageStatus.choices, default=MessageStatus.PENDING)
    error_message = models.TextField(_("Error Message"), blank=True, null=True)
    sent_at = models.DateTimeField(_("Sent At"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Twilio Message Log")
        verbose_name_plural = _("Twilio Message Logs")
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['sent_at']),
        ]

    def __str__(self):
        return f"{self.message_type.title()} Message to {self.user}" if self.user else "Anonymous Message"


class TwilioService:
    """
    Service class to handle all Twilio interactions.
    """

    @staticmethod
    def validate_twilio_settings():
        """
        Validates that all necessary Twilio settings are present.
        """
        required_settings = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
        missing_settings = [setting for setting in required_settings if not getattr(settings, setting, None)]
        if missing_settings:
            raise ValueError(f"Missing required setting(s): {', '.join(missing_settings)}")

    @staticmethod
    def send_sms(to, body):
        """
        Send an SMS using Twilio.
        """
        if not to.startswith("+"):
            raise ValueError("Phone number must be in international format starting with '+'.")
        if not body:
            raise ValueError("SMS body cannot be empty.")

        TwilioService.validate_twilio_settings()
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        try:
            message = client.messages.create(
                to=to,
                from_=settings.TWILIO_PHONE_NUMBER,
                body=body
            )
            logger.info(f"SMS sent successfully to {to} with SID {message.sid}")
            return message.sid, "sent"
        except Exception as e:
            logger.error(f"Failed to send SMS to {to}: {e}")
            return None, "failed", str(e)

    @staticmethod
    def make_voice_call(to, url):
        """
        Make a voice call using Twilio and play a message from a given URL.
        """
        if not to.startswith("+"):
            raise ValueError("Phone number must be in international format starting with '+'.")
        if not url:
            raise ValueError("URL for voice call cannot be empty.")

        TwilioService.validate_twilio_settings()
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        try:
            call = client.calls.create(
                to=to,
                from_=settings.TWILIO_PHONE_NUMBER,
                url=url
            )
            logger.info(f"Voice call initiated to {to} with SID {call.sid}")
            return call.sid, "sent"
        except Exception as e:
            logger.error(f"Failed to make voice call to {to}: {e}")
            return None, "failed", str(e)
