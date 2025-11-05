from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
import logging

from .utils import get_ip

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login with username and IP address"""
    logger.info(f"Successful login for user {user.username} from IP: {get_ip(request)}")


@receiver(user_login_failed)
def log_user_login_failed(sender, request, credentials, **kwargs):
    """Log failed login attempts with username and IP address"""
    username = credentials.get('username', 'unknown')
    logger.warning(f"Failed login attempt for {username} from IP: {get_ip(request)}")
