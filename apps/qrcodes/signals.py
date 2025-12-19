from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.houses.models import House
from apps.regions.models import Mahalla
from .models import QRCode


@receiver(post_save, sender=House)
def create_qr_code_for_house(sender, instance, created, **kwargs):
    """
    House birinchi marta yaratilganda
    unga avtomatik QR code yaratadi
    """
    if created:
        QRCode.objects.create(house=instance)


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
                print(f"✅ Auto-created new house and QR code for {mahalla.name}")
        except QRCode.DoesNotExist:
            pass
