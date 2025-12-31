import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.houses.models import House
from .models import QRCode

logger = logging.getLogger(__name__)

# Constants
MINIMUM_UNCLAIMED_HOUSES = 10  # Minimum number of unclaimed houses to maintain


# Constants
MINIMUM_UNCLAIMED_HOUSES = 10  # Minimum number of unclaimed houses to maintain


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
    # Skip if house is newly created or has no owner
    if created or not instance.owner:
        return

    # Check unclaimed houses count
    unclaimed_count = House.objects.filter(owner__isnull=True).count()

    # Create new houses if below minimum
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


# NOTE: is_delivered field has been removed from QRCode model
# This signal is disabled
# @receiver(pre_save, sender=QRCode)
# def auto_create_replacement_qr_on_delivery(sender, instance, **kwargs):
#     """
#     QR code topshirilganda (is_delivered=True) avtomatik
#     yangi bo'sh QR code yaratadi
#     """
#     if instance.pk:  # Agar QR code allaqachon mavjud bo'lsa
#         try:
#             old_instance = QRCode.objects.get(pk=instance.pk)
#             # Agar topshirilmagan -> topshirilgan holatga o'tsa
#             if not old_instance.is_delivered and instance.is_delivered:
#                 # Yangi uy yaratish (owner'siz)
#                 mahalla = instance.house.mahalla
#                 house_count = House.objects.filter(mahalla=mahalla).count()
#
#                 new_house = House.objects.create(
#                     mahalla=mahalla,
#                     address=f"{mahalla.name}, yangi uy",
#                     house_number=str(house_count + 1),
#                     owner=None,
#                 )
#                 # Signal avtomatik QR code yaratadi
#                 logger.info(f"Auto-created new house and QR code for {mahalla.name}")
#         except QRCode.DoesNotExist:
#             pass
