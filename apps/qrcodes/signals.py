import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.houses.models import House
from .models import QRCode

logger = logging.getLogger(__name__)

MINIMUM_UNCLAIMED_HOUSES = 10
MINIMUM_UNCLAIMED_QRCODES = 10  # Maintain 10 unclaimed QR codes


@receiver(post_save, sender=House)
def create_qr_code_for_house(sender, instance, created, **kwargs):
    """
    Automatically create QR code when a new house is created.
    DISABLED: Admin creates QR codes manually now.

    Args:
        sender: Model class (House)
        instance: The actual House instance being saved
        created: Boolean indicating if this is a new object
        **kwargs: Additional keyword arguments
    """
    # Disabled - admin creates QR codes manually
    pass
    # if created:
    #     QRCode.objects.create(house=instance)


@receiver(post_save, sender=House)
def maintain_unclaimed_houses(sender, instance, created, **kwargs):
    """
    Maintain minimum number of unclaimed houses.
    DISABLED: Admin manages houses manually now.

    When a house gets an owner, check unclaimed houses count
    and create new ones if needed to maintain the minimum.

    Args:
        sender: Model class (House)
        instance: The actual House instance being saved
        created: Boolean indicating if this is a new object
        **kwargs: Additional keyword arguments
    """
    # Disabled - admin manages houses manually
    pass
    # if created or not instance.owner:
    #     return

    # unclaimed_count = House.objects.filter(owner__isnull=True).count()

    # if unclaimed_count < MINIMUM_UNCLAIMED_HOUSES:
    #     houses_needed = MINIMUM_UNCLAIMED_HOUSES - unclaimed_count
    #     mahalla = instance.mahalla

    #     for i in range(houses_needed):
    #         house_count = House.objects.filter(mahalla=mahalla).count()
    #         House.objects.create(
    #             mahalla=mahalla,
    #             address=f"{mahalla.name}, avtomatik yaratilgan uy",
    #             house_number=f"AUTO-{house_count + i + 1}",
    #             owner=None,
    #         )

    #     logger.info(
    #         f"Created {houses_needed} new unclaimed houses to maintain "
    #         f"minimum of {MINIMUM_UNCLAIMED_HOUSES}"
    #     )


@receiver(post_save, sender=QRCode)
def maintain_unclaimed_qrcodes(sender, instance, created, **kwargs):
    """
    Maintain minimum number of unclaimed QR codes.
    DISABLED: Admin creates QR codes manually now.

    When a QR code gets claimed (linked to a house), automatically
    generate a new unclaimed QR code to maintain the pool of 10.

    Args:
        sender: Model class (QRCode)
        instance: The actual QRCode instance being saved
        created: Boolean indicating if this is a new object
        **kwargs: Additional keyword arguments
    """
    # Disabled - admin creates QR codes manually
    pass
    # # Skip if this is a new QR code being created
    # if created:
    #     return

    # # Only act when QR code gets claimed (house assigned)
    # if not instance.house:
    #     return

    # # Check unclaimed QR codes count
    # unclaimed_count = QRCode.objects.filter(house__isnull=True).count()

    # if unclaimed_count < MINIMUM_UNCLAIMED_QRCODES:
    #     qrcodes_needed = MINIMUM_UNCLAIMED_QRCODES - unclaimed_count

    #     # Create new unclaimed QR codes
    #     for i in range(qrcodes_needed):
    #         QRCode.objects.create()

    #     logger.info(
    #         f"Created {qrcodes_needed} new unclaimed QR codes to maintain "
    #         f"minimum of {MINIMUM_UNCLAIMED_QRCODES}. Current unclaimed: {unclaimed_count + qrcodes_needed}"
    #     )
