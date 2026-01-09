from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import House
from .services import (
    send_house_registration_notification,
    send_agent_house_notification,
)
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=House)
def house_post_save(sender, instance, created, **kwargs):
    """
    Send notification when a new house is created.
    Different notification for agent vs client created houses.
    """
    if created:
        logger.info(f"🏠 New house created: ID={instance.id}, created_by_agent={instance.created_by_agent}, owner={instance.owner}")
        try:
            if instance.created_by_agent:
                logger.info(f"📨 Sending agent house notification for house ID: {instance.id}")
                # Send agent house notification
                send_agent_house_notification(instance)
            else:
                logger.info(f"📨 Sending regular house notification for house ID: {instance.id}")
                # Send regular house notification
                send_house_registration_notification(instance)
        except Exception as e:
            logger.error(f"Failed to send house registration notification: {e}")
