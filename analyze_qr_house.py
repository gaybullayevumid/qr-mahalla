import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House

print("🔍 Analyzing QR Code - House relationships\n")

# Check all houses
houses = House.objects.all()
print(f"Total houses: {houses.count()}\n")

for house in houses:
    print(f"House ID {house.id}: {house.address} - {house.house_number}")
    print(f"  Owner: {house.owner.phone if house.owner else 'None'}")

    # Find QR codes linked to this house
    qr_codes = QRCode.objects.filter(house=house)
    print(f"  QR codes linked: {qr_codes.count()}")

    for qr in qr_codes:
        print(f"    - {qr.uuid}")

    # Check reverse relation
    try:
        qr_reverse = house.qr_code
        print(f"  Reverse relation (house.qr_code): {qr_reverse.uuid}")
    except QRCode.DoesNotExist:
        print(f"  Reverse relation: None")
    except Exception as e:
        print(f"  Reverse relation error: {e}")

    print()

# Check all QR codes
print("\n" + "=" * 60)
print("All QR Codes")
print("=" * 60 + "\n")

qr_codes = QRCode.objects.all()
print(f"Total QR codes: {qr_codes.count()}\n")

for qr in qr_codes[:10]:
    print(f"QR {qr.uuid}:")
    print(f"  House: {qr.house}")
    if qr.house:
        print(f"  House ID: {qr.house.id}")
        print(f"  Address: {qr.house.address}")
    print()
