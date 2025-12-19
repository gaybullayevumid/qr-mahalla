import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House
from apps.users.models import User

print("=" * 50)
print("QR CODE WORKFLOW TEST")
print("=" * 50)

# Check QR codes
qr_codes = QRCode.objects.all()
print(f"\n✅ Total QR Codes: {qr_codes.count()}")

# Find unclaimed QR code (house without owner)
unclaimed_qr = QRCode.objects.filter(house__owner__isnull=True).first()

if unclaimed_qr:
    print(f"\n📍 Unclaimed QR Code Found:")
    print(f"   ID: {unclaimed_qr.id}")
    print(f"   UUID: {unclaimed_qr.uuid}")
    print(f"   House: {unclaimed_qr.house.address}")
    print(f"   Mahalla: {unclaimed_qr.house.mahalla.name}")
    print(f"   Owner: None (ready to claim)")
else:
    print("\n⚠️  No unclaimed QR codes found. Creating one...")
    from apps.regions.models import Mahalla

    mahalla = Mahalla.objects.first()
    house = House.objects.create(
        mahalla=mahalla, house_number="Test-123", address="Test uy manzili"
    )
    print(f"   ✅ House created: {house.id}")

# Check claimed houses
claimed_houses = House.objects.filter(owner__isnull=False)
print(f"\n✅ Claimed Houses: {claimed_houses.count()}")
for house in claimed_houses[:3]:
    print(f"   - {house.address} → Owner: {house.owner.phone}")

print("\n" + "=" * 50)
print("WORKFLOW ENDPOINTS:")
print("=" * 50)
print("1. Scan QR:  GET /api/qrcode/scan/{qr_id}/")
print("2. Claim:    POST /api/qrcode/claim/{qr_id}/")
print("   Body: {first_name, last_name, passport_id, address}")
print("3. Re-scan:  GET /api/qrcode/scan/{qr_id}/")
print("   (Shows owner info based on scanner role)")
print("=" * 50)
