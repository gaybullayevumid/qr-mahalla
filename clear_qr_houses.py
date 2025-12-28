import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House

# Remove all house associations from QR codes
qr_count = QRCode.objects.count()
print(f"Total QR codes: {qr_count}")

# Count QR codes with houses
linked_qr_count = QRCode.objects.filter(house__isnull=False).count()
print(f"QR codes with houses: {linked_qr_count}")

# Update all QR codes to have no house
QRCode.objects.all().update(house=None)
print(f"✅ Removed house associations from all QR codes")

# Delete all houses
house_count = House.objects.count()
House.objects.all().delete()
print(f"✅ Deleted {house_count} houses")

# Verify all QR codes are now empty
empty_qr_count = QRCode.objects.filter(house__isnull=True).count()
print(f"\n📊 Summary:")
print(f"Total QR codes: {qr_count}")
print(f"Empty QR codes: {empty_qr_count}")
print(f"QR codes with houses: {QRCode.objects.filter(house__isnull=False).count()}")
