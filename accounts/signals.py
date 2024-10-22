from django.dispatch import receiver, Signal
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, post_delete
from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser
from .utils import log_activity
import logging

# Configure logger for signal errors
logger = logging.getLogger(__name__)

# Custom signals
notification_sent = Signal()
user_verified = Signal()

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log when a user logs in."""
    try:
        ip_address = request.META.get('REMOTE_ADDR')
        log_activity(
            user=user,
            action="User logged in",
            ip_address=ip_address
        )
    except Exception as e:
        logger.error(f"Error logging user login: {str(e)}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log when a user logs out."""
    try:
        ip_address = request.META.get('REMOTE_ADDR')
        log_activity(
            user=user,
            action="User logged out",
            ip_address=ip_address
        )
    except Exception as e:
        logger.error(f"Error logging user logout: {str(e)}")


@receiver(post_save, sender=CustomUser)
def log_user_save(sender, instance, created, **kwargs):
    """Log when a user is created or updated."""
    try:
        action = "User created" if created else "User updated"
        log_activity(
            user=instance,
            action=action,
            additional_data={"user_email": instance.email}
        )
    except Exception as e:
        logger.error(f"Error logging user save: {str(e)}")


@receiver(post_delete, sender=CustomUser)
def log_user_delete(sender, instance, **kwargs):
    """Log when a user is deleted."""
    try:
        log_activity(
            user=instance,
            action="User deleted",
            additional_data={"user_email": instance.email}
        )
    except Exception as e:
        logger.error(f"Error logging user deletion: {str(e)}")


@receiver(notification_sent)
def log_notification(sender, user, message, **kwargs):
    """Log when a notification is sent."""
    try:
        log_activity(
            user=user,
            action="Notification sent",
            additional_data={"message": message}
        )
    except Exception as e:
        logger.error(f"Error logging notification sent: {str(e)}")


@receiver(user_verified)
def log_user_verification(sender, user, timestamp, **kwargs):
    """Log when a user is verified."""
    try:
        log_activity(
            user=user,
            action="User verified",
            additional_data={"verification_time": timestamp}
        )
    except Exception as e:
        logger.error(f"Error logging user verification: {str(e)}")


@receiver(post_save)
def log_generic_save(sender, instance, created, **kwargs):
    """Generic logging for any model's save event."""
    if sender._meta.app_label not in ['auth', 'sessions', 'contenttypes']:  # Exclude Django core models
        try:
            action = f"{sender._meta.verbose_name.title()} created" if created else f"{sender._meta.verbose_name.title()} updated"
            log_activity(
                user=getattr(instance, 'user', None),
                action=action,
                additional_data={"model": instance._meta.model_name, "instance_id": instance.pk}
            )
        except ObjectDoesNotExist:
            logger.warning(f"User reference not found in instance {instance} for model {sender}")
        except Exception as e:
            logger.error(f"Error logging generic save for model {sender}: {str(e)}")


@receiver(post_delete)
def log_generic_delete(sender, instance, **kwargs):
    """Generic logging for any model's delete event."""
    if sender._meta.app_label not in ['auth', 'sessions', 'contenttypes']:  # Exclude Django core models
        try:
            action = f"{sender._meta.verbose_name.title()} deleted"
            log_activity(
                user=getattr(instance, 'user', None),
                action=action,
                additional_data={"model": instance._meta.model_name, "instance_id": instance.pk}
            )
        except ObjectDoesNotExist:
            logger.warning(f"User reference not found in instance {instance} for model {sender}")
        except Exception as e:
            logger.error(f"Error logging generic delete for model {sender}: {str(e)}")
