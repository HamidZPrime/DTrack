# utils.py

import logging
from django.utils import timezone
from .models import UserActivityLog
from django.db import DatabaseError

logger = logging.getLogger(__name__)

def log_activity(user, action, ip_address=None, additional_data=None):
    """
    Logs an activity to UserActivityLog.
    """
    if additional_data is None:
        additional_data = {}

    try:
        UserActivityLog.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            additional_data=additional_data,
            timestamp=timezone.now(),
        )
    except DatabaseError as db_error:
        # Log the exception details for debugging
        logger.error(
            f"DatabaseError while logging activity for user {user.id}: {db_error}"
        )
        # Optionally, handle the error further or notify administrators
    except Exception as ex:
        # Catch any other exceptions that might occur
        logger.error(f"Unexpected error in log_activity: {ex}")
