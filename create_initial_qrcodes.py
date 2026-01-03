"""
Script to create initial pool of 10 unclaimed QR codes.
"""

import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode


def create_initial_qrcodes():
    """Create 10 unclaimed QR codes if they don't exist."""

    # Count existing unclaimed QR codes
    unclaimed_count = QRCode.objects.filter(house__isnull=True).count()
    total_count = QRCode.objects.count()

    print(f"Current QR codes: {total_count}")
    print(f"Unclaimed QR codes: {unclaimed_count}")

    REQUIRED_UNCLAIMED = 10

    if unclaimed_count >= REQUIRED_UNCLAIMED:
        print(f"\n✓ Already have {unclaimed_count} unclaimed QR codes.")
        print("No need to create more.")
        return

    qrcodes_needed = REQUIRED_UNCLAIMED - unclaimed_count

    print(f"\nCreating {qrcodes_needed} new unclaimed QR codes...")

    created_qrcodes = []
    for i in range(qrcodes_needed):
        qr = QRCode.objects.create()
        created_qrcodes.append(qr)
        print(f"  ✓ Created QR #{qr.id} - {qr.uuid}")

    # Final count
    final_unclaimed = QRCode.objects.filter(house__isnull=True).count()
    final_total = QRCode.objects.count()

    print(f"\n{'=' * 50}")
    print(f"✅ Successfully created {qrcodes_needed} QR codes!")
    print(f"{'=' * 50}")
    print(f"Total QR codes: {final_total}")
    print(f"Unclaimed QR codes: {final_unclaimed}")
    print(f"\n💡 AUTO-GENERATE is ACTIVE:")
    print(f"   When QR codes are claimed, new ones will be")
    print(f"   automatically created to maintain 10 unclaimed QRs.")


if __name__ == "__main__":
    print("=" * 50)
    print("Create Initial QR Codes Pool")
    print("=" * 50)
    print()

    create_initial_qrcodes()
