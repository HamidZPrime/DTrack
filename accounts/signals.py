import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CustomUser
from .utils import log_activity

# Import get_client_ip from ipware, handle if not installed
try:
    from ipware import get_client_ip
except ImportError:
    # Define a fallback function if ipware is not installed
    def get_client_ip(request):
        return request.META.get('REMOTE_ADDR'), False

logger = logging.getLogger(__name__)

def _get_client_ip(request):
    """
    Utility function to retrieve client IP address, considering proxies.
    """
    client_ip, _ = get_client_ip(request)
    return client_ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log when a user logs in.
    """
    try:
        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        log_activity(
            user=user,
            action="User logged in",
            ip_address=ip_address,
            additional_data={"user_agent": user_agent},
        )
    except Exception as ex:
        logger.error(f"Error logging user login: {ex}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log when a user logs out.
    """
    try:
        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        log_activity(
            user=user,
            action="User logged out",
            ip_address=ip_address,
            additional_data={"user_agent": user_agent},
        )
    except Exception as ex:
        logger.error(f"Error logging user logout: {ex}")

@receiver(post_save, sender=CustomUser)
def log_user_save(sender, instance, created, **kwargs):
    """
    Log when a user is created or updated.
    """
    try:
        action = "User created" if created else "User updated"
        log_activity(
            user=instance,
            action=action,
            additional_data={"user_id": instance.id},
        )
    except Exception as ex:
        logger.error(f"Error logging user save: {ex}")

@receiver(post_delete, sender=CustomUser)
def log_user_delete(sender, instance, **kwargs):
    """
    Log when a user is deleted.
    """
    try:
        log_activity(
            user=instance,
            action="User deleted",
            additional_data={"user_id": instance.id},
        )
    except Exception as ex:
        logger.error(f"Error logging user deletion: {ex}")
