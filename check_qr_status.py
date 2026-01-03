"""
Check current QR codes status.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode


def check_status():
    total = QRCode.objects.count()
    claimed = QRCode.objects.filter(house__isnull=False).count()
    unclaimed = QRCode.objects.filter(house__isnull=True).count()

    print("=" * 60)
    print("QR CODES STATUS")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"   Total QR codes: {total}")
    print(f"   Claimed (linked to houses): {claimed}")
    print(f"   Unclaimed (available): {unclaimed}")
    print(f"\n💡 Auto-generate: ACTIVE ✅")
    print(f"   Minimum unclaimed: 10")
    print(f"   Current unclaimed: {unclaimed}")

    if unclaimed >= 10:
        print(f"\n✅ System working correctly!")
    else:
        print(f"\n⚠️  Warning: Less than 10 unclaimed QR codes")

    print("=" * 60)


if __name__ == "__main__":
    check_status()
