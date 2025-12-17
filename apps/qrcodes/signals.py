from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.houses.models import House
from .models import QRCode


@receiver(post_save, sender=House)
def create_qr_code_for_house(sender, instance, created, **kwargs):
    """
    House birinchi marta yaratilganda
    unga avtomatik QR code yaratadi
    """
    if created:
        QRCode.objects.create(house=instance)
