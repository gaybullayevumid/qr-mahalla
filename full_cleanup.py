import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.houses.models import House
from apps.qrcodes.models import QRCode

print("🧹 Complete database cleanup\n")

# Delete all houses
houses = House.objects.all()
print(f"Deleting {houses.count()} houses...")
houses.delete()

# Set all QR codes house to NULL
qr_count = QRCode.objects.exclude(house__isnull=True).count()
if qr_count > 0:
    print(f"Setting {qr_count} QR codes house to NULL...")
    QRCode.objects.update(house=None)

print(f"\n✅ Cleanup complete")
print(f"Houses: {House.objects.count()}")
print(f"QR codes with house: {QRCode.objects.exclude(house__isnull=True).count()}")
print(f"QR codes without house: {QRCode.objects.filter(house__isnull=True).count()}")
