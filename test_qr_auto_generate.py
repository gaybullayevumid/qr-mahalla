"""
Test script to verify auto-generation of QR codes.
This will claim a QR code and check if new ones are auto-generated.
"""

import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House
from apps.regions.models import Region, District, Mahalla


def test_auto_generate():
    """Test auto-generation by claiming QR codes."""

    print("=" * 60)
    print("TESTING AUTO-GENERATE QR CODES")
    print("=" * 60)

    # Initial state
    unclaimed_before = QRCode.objects.filter(house__isnull=True).count()
    total_before = QRCode.objects.count()

    print(f"\n📊 BEFORE:")
    print(f"   Total QR codes: {total_before}")
    print(f"   Unclaimed QR codes: {unclaimed_before}")

    # Create region, district, mahalla for house
    print(f"\n🏗️  Creating test region/district/mahalla...")
    region, _ = Region.objects.get_or_create(name="Test Region")
    district, _ = District.objects.get_or_create(name="Test District", region=region)
    mahalla, _ = Mahalla.objects.get_or_create(name="Test Mahalla", district=district)

    # Create a house
    print(f"🏠 Creating test house...")
    house = House.objects.create(
        mahalla=mahalla, address="Test address", house_number="TEST-001"
    )

    # Get an unclaimed QR code
    unclaimed_qr = QRCode.objects.filter(house__isnull=True).first()

    if not unclaimed_qr:
        print("❌ No unclaimed QR codes found!")
        return

    print(f"\n📌 Claiming QR #{unclaimed_qr.id} ({unclaimed_qr.uuid})...")

    # Claim the QR code by assigning it to a house
    unclaimed_qr.house = house
    unclaimed_qr.save()

    print(f"   ✓ QR code claimed and linked to house #{house.id}")

    # Check results
    unclaimed_after = QRCode.objects.filter(house__isnull=True).count()
    total_after = QRCode.objects.count()

    print(f"\n📊 AFTER:")
    print(f"   Total QR codes: {total_after}")
    print(f"   Unclaimed QR codes: {unclaimed_after}")

    # Check if auto-generation worked
    new_qrcodes_created = total_after - total_before

    print(f"\n" + "=" * 60)
    if unclaimed_after >= 10:
        print("✅ AUTO-GENERATE WORKING!")
        print(f"   {new_qrcodes_created} new QR code(s) were automatically created")
        print(f"   Maintained {unclaimed_after} unclaimed QR codes")
    else:
        print("⚠️  Warning: Less than 10 unclaimed QR codes")
        print(f"   Expected: 10, Got: {unclaimed_after}")
    print("=" * 60)


if __name__ == "__main__":
    test_auto_generate()
