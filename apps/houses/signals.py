from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import House
from .services import send_house_registration_notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=House)
def house_post_save(sender, instance, created, **kwargs):
    """
    Send notification when a new house is created.
    Skip QR code generation if created by agent.
    """
    if created and not instance.created_by_agent:
        try:
            send_house_registration_notification(instance)
        except Exception as e:
            logger.error(f"Failed to send house registration notification: {e}")
