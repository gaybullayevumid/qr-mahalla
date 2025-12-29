import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.houses.models import House
from apps.qrcodes.models import QRCode

print("🧹 Cleaning up orphaned data\n")

# Find houses without QR codes
all_houses = House.objects.all()
print(f"Total houses: {all_houses.count()}")

for house in all_houses:
    try:
        qr = house.qr_code
        print(f"  House {house.id}: ✅ Has QR {qr.uuid}")
    except QRCode.DoesNotExist:
        print(f"  House {house.id}: ❌ NO QR CODE - ORPHANED")
        print(f"     Address: {house.address}")
        print(f"     Owner: {house.owner.phone if house.owner else 'None'}")

        # Delete orphaned house
        house.delete()
        print(f"     🗑️  Deleted")

# Find QR codes with invalid house_id
print(f"\n🔍 Checking QR codes...")
all_qr = QRCode.objects.exclude(house__isnull=True)
print(f"QR codes with house_id: {all_qr.count()}")

for qr in all_qr:
    try:
        house = qr.house
        print(f"  QR {qr.uuid}: ✅ House {house.id} exists")
    except House.DoesNotExist:
        print(f"  QR {qr.uuid}: ❌ INVALID house_id={qr.house_id}")
        qr.house = None
        qr.save(update_fields=["house"])
        print(f"     🔧 Fixed - set house to NULL")

print(f"\n✅ Cleanup complete")
