"""
Delete all claimed QR codes, keep only unclaimed ones.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode


def delete_claimed_qrcodes():
    """Delete all claimed QR codes."""

    total = QRCode.objects.count()
    claimed = QRCode.objects.filter(house__isnull=False).count()
    unclaimed = QRCode.objects.filter(house__isnull=True).count()

    print("=" * 60)
    print("DELETE CLAIMED QR CODES")
    print("=" * 60)

    print(f"\n📊 Current status:")
    print(f"   Total QR codes: {total}")
    print(f"   Claimed (will be deleted): {claimed}")
    print(f"   Unclaimed (will remain): {unclaimed}")

    if claimed == 0:
        print(f"\n✓ No claimed QR codes to delete.")
        return

    confirm = input(f"\n⚠️  Delete {claimed} claimed QR codes? (yes/no): ")

    if confirm.lower() in ["yes", "y", "ha"]:
        # Delete claimed QR codes
        deleted = QRCode.objects.filter(house__isnull=False).delete()

        remaining = QRCode.objects.count()

        print(f"\n" + "=" * 60)
        print(f"✅ Successfully deleted {deleted[0]} claimed QR codes!")
        print(f"=" * 60)
        print(f"Remaining QR codes: {remaining}")
        print(f"All remaining QR codes are unclaimed ✓")
    else:
        print("\n❌ Deletion cancelled.")


if __name__ == "__main__":
    delete_claimed_qrcodes()
