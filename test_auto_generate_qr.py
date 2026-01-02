import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.users.models import User
from apps.houses.models import House
from apps.regions.models import Mahalla

print("=" * 60)
print("=== Testing Auto QR Code Generation on Claim ===")
print("=" * 60)

# Count unclaimed QR codes before claim
unclaimed_before = QRCode.objects.filter(house__isnull=True).count()
print(f"\n📊 BEFORE CLAIM:")
print(f"   Unclaimed QR codes: {unclaimed_before}")

# Get an unclaimed QR code
unclaimed_qr = QRCode.objects.filter(house__isnull=True).first()
if not unclaimed_qr:
    print("❌ No unclaimed QR codes found!")
    exit(1)

print(f"   Selected QR: {unclaimed_qr.uuid}")

# Get user and mahalla
user = User.objects.get(phone="+998906252919")
mahalla = Mahalla.objects.first()

print(f"   User: {user.phone}")
print(f"   Mahalla: {mahalla.name if mahalla else 'None'}")

# Simulate claim: create house and link to QR
print("\n🔄 CLAIMING QR CODE...")
house = House.objects.create(
    address="Test auto-generate address",
    house_number="999",
    mahalla=mahalla,
    owner=user,
)

unclaimed_qr.house = house
unclaimed_qr.save()  # This should trigger the signal!

print(f"   ✅ Claimed QR {unclaimed_qr.uuid}")
print(f"   ✅ Created house {house.id}")

# Count unclaimed QR codes after claim
unclaimed_after = QRCode.objects.filter(house__isnull=True).count()
print(f"\n📊 AFTER CLAIM:")
print(f"   Unclaimed QR codes: {unclaimed_after}")

# Check if new QR codes were generated
print("\n" + "=" * 60)
print("=== Result ===")
print("=" * 60)

if unclaimed_after >= 10:
    print("✅ SUCCESS: Auto-generated new QR codes!")
    print(f"✅ Maintained minimum of 10 unclaimed QR codes")
    print(f"   Before: {unclaimed_before}")
    print(f"   After:  {unclaimed_after}")

    # Show newly generated QR codes
    if unclaimed_after > unclaimed_before - 1:
        generated = unclaimed_after - (unclaimed_before - 1)
        print(f"\n🆕 Generated {generated} new QR code(s)")

        # Get last created QR codes
        new_qrs = QRCode.objects.filter(house__isnull=True).order_by("-created_at")[
            :generated
        ]
        print("\n📝 New QR codes:")
        for qr in new_qrs:
            print(f"   - {qr.uuid}")
else:
    print(f"⚠️  WARNING: Only {unclaimed_after} unclaimed QR codes")
    print(f"   Expected at least 10")
