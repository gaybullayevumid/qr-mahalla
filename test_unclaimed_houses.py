import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.houses.models import House
from apps.qrcodes.models import QRCode
from apps.regions.models import Mahalla

print("=" * 50)
print("UNCLAIMED HOUSES CHECK")
print("=" * 50)

# Check current unclaimed houses
unclaimed_houses = House.objects.filter(owner__isnull=True)
print(f"\n✅ Current unclaimed houses: {unclaimed_houses.count()}")

# If less than 10, create more
MINIMUM = 10
if unclaimed_houses.count() < MINIMUM:
    needed = MINIMUM - unclaimed_houses.count()
    print(f"\n⚠️  Need {needed} more houses to reach minimum of {MINIMUM}")

    # Get first mahalla
    mahalla = Mahalla.objects.first()
    print(f"📍 Creating houses in mahalla: {mahalla.name}")

    for i in range(needed):
        house = House.objects.create(
            mahalla=mahalla,
            address=f"{mahalla.name}, egasiz uy #{i+1}",
            house_number=f"UNCLAIMED-{i+1}",
            owner=None,
        )
        print(f"   ✅ Created house #{house.id}")

    print(
        f"\n✅ Now total unclaimed houses: {House.objects.filter(owner__isnull=True).count()}"
    )
else:
    print(
        f"✅ Already have {unclaimed_houses.count()} unclaimed houses (minimum is {MINIMUM})"
    )

# Show some unclaimed QR codes
print("\n" + "=" * 50)
print("UNCLAIMED QR CODES (First 10)")
print("=" * 50)

unclaimed_qrs = QRCode.objects.filter(house__owner__isnull=True)[:10]
for qr in unclaimed_qrs:
    print(f"QR #{qr.id} (UUID: {qr.uuid})")
    print(f"  House: {qr.house.address}")
    print(f"  Mahalla: {qr.house.mahalla.name}")
    print()

print("=" * 50)
print(
    f"✅ Total unclaimed QR codes: {QRCode.objects.filter(house__owner__isnull=True).count()}"
)
print("=" * 50)
