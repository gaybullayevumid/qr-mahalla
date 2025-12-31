import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.houses.models import House
from .models import QRCode

logger = logging.getLogger(__name__)

MINIMUM_UNCLAIMED_HOUSES = 10


@receiver(post_save, sender=House)
def create_qr_code_for_house(sender, instance, created, **kwargs):
    """
    Automatically create QR code when a new house is created.

    Args:
        sender: Model class (House)
        instance: The actual House instance being saved
        created: Boolean indicating if this is a new object
        **kwargs: Additional keyword arguments
    """
    if created:
        QRCode.objects.create(house=instance)


@receiver(post_save, sender=House)
def maintain_unclaimed_houses(sender, instance, created, **kwargs):
    """
    Maintain minimum number of unclaimed houses.

    When a house gets an owner, check unclaimed houses count
    and create new ones if needed to maintain the minimum.

    Args:
        sender: Model class (House)
        instance: The actual House instance being saved
        created: Boolean indicating if this is a new object
        **kwargs: Additional keyword arguments
    """
    if created or not instance.owner:
        return

    unclaimed_count = House.objects.filter(owner__isnull=True).count()

    if unclaimed_count < MINIMUM_UNCLAIMED_HOUSES:
        houses_needed = MINIMUM_UNCLAIMED_HOUSES - unclaimed_count
        mahalla = instance.mahalla

        for i in range(houses_needed):
            house_count = House.objects.filter(mahalla=mahalla).count()
            House.objects.create(
                mahalla=mahalla,
                address=f"{mahalla.name}, avtomatik yaratilgan uy",
                house_number=f"AUTO-{house_count + i + 1}",
                owner=None,
            )

        logger.info(
            f"Created {houses_needed} new unclaimed houses to maintain "
            f"minimum of {MINIMUM_UNCLAIMED_HOUSES}"
        )
