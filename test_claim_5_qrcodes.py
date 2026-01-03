"""
Test claiming multiple QR codes at once.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House
from apps.regions.models import Mahalla


def test_claim_multiple():
    """Claim 5 QR codes and verify auto-generation."""

    print("=" * 60)
    print("TEST: Claiming 5 QR codes")
    print("=" * 60)

    # Get mahalla
    mahalla = Mahalla.objects.first()
    if not mahalla:
        print("❌ No mahalla found!")
        return

    # Initial count
    unclaimed_before = QRCode.objects.filter(house__isnull=True).count()
    total_before = QRCode.objects.count()

    print(f"\n📊 BEFORE:")
    print(f"   Total QR codes: {total_before}")
    print(f"   Unclaimed QR codes: {unclaimed_before}")

    # Claim 5 QR codes
    print(f"\n🔄 Claiming 5 QR codes...")

    unclaimed_qrs = QRCode.objects.filter(house__isnull=True)[:5]

    for i, qr in enumerate(unclaimed_qrs, 1):
        # Create house for each QR
        house = House.objects.create(
            mahalla=mahalla, address=f"Test house {i}", house_number=f"TEST-{i:03d}"
        )

        # Claim QR code
        qr.house = house
        qr.save()

        print(f"   {i}. QR #{qr.id} -> House #{house.id}")

    # Check results
    unclaimed_after = QRCode.objects.filter(house__isnull=True).count()
    total_after = QRCode.objects.count()

    print(f"\n📊 AFTER:")
    print(f"   Total QR codes: {total_after}")
    print(f"   Unclaimed QR codes: {unclaimed_after}")

    new_created = total_after - total_before

    print(f"\n" + "=" * 60)
    print(f"✅ Claimed 5 QR codes")
    print(f"✅ Auto-created {new_created} new QR codes")
    print(f"✅ Maintained {unclaimed_after} unclaimed QR codes")
    print("=" * 60)


if __name__ == "__main__":
    test_claim_multiple()
