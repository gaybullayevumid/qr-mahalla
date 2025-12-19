import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

from apps.houses.models import House
from apps.regions.models import Mahalla
from .models import QRCode


MINIMUM_UNCLAIMED_HOUSES = 10  # Har doim 10 ta egasiz uy bo'lishi kerak


@receiver(post_save, sender=House)
def create_qr_code_for_house(sender, instance, created, **kwargs):
    """
    House birinchi marta yaratilganda
    unga avtomatik QR code yaratadi
    """
    if created:
        QRCode.objects.create(house=instance)


@receiver(post_save, sender=House)
def maintain_unclaimed_houses(sender, instance, created, **kwargs):
    """
    House owner'ga berilganda, egasiz uylar sonini tekshiradi
    va har doim 10 ta egasiz uy bo'lishini ta'minlaydi
    """
    # Agar uy yangi yaratilgan yoki owner o'zgarmagan bo'lsa, hech narsa qilmaydi
    if created:
        return

    # Agar house ga owner berilgan bo'lsa
    if instance.owner:
        # Egasiz uylar sonini tekshirish
        unclaimed_count = House.objects.filter(owner__isnull=True).count()

        # Agar 10 dan kam bo'lsa, yangi uylar yaratish
        if unclaimed_count < MINIMUM_UNCLAIMED_HOUSES:
            houses_needed = MINIMUM_UNCLAIMED_HOUSES - unclaimed_count

            # Oxirgi uyning mahalla'sidan yangi uylar yaratish
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
                f"Created {houses_needed} new unclaimed houses to maintain minimum of {MINIMUM_UNCLAIMED_HOUSES}"
            )


@receiver(pre_save, sender=QRCode)
def auto_create_replacement_qr_on_delivery(sender, instance, **kwargs):
    """
    QR code topshirilganda (is_delivered=True) avtomatik
    yangi bo'sh QR code yaratadi
    """
    if instance.pk:  # Agar QR code allaqachon mavjud bo'lsa
        try:
            old_instance = QRCode.objects.get(pk=instance.pk)
            # Agar topshirilmagan -> topshirilgan holatga o'tsa
            if not old_instance.is_delivered and instance.is_delivered:
                # Yangi uy yaratish (owner'siz)
                mahalla = instance.house.mahalla
                house_count = House.objects.filter(mahalla=mahalla).count()

                new_house = House.objects.create(
                    mahalla=mahalla,
                    address=f"{mahalla.name}, yangi uy",
                    house_number=str(house_count + 1),
                    owner=None,
                )
                # Signal avtomatik QR code yaratadi
                logger.info(f"Auto-created new house and QR code for {mahalla.name}")
        except QRCode.DoesNotExist:
            pass
