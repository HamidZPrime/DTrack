# utils.py

from .models import UserActivityLog

def log_activity(user, action, ip_address=None, additional_data=None):
    """Logs an activity to UserActivityLog"""
    UserActivityLog.objects.create(
        user=user,
        action=action,
        ip_address=ip_address,
        additional_data=additional_data or {}
    )
