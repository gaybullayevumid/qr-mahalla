"""
Script to clean up the entire database except users.
Only users will remain after this operation.
"""

import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.scans.models import ScanLog
from apps.houses.models import House
from apps.regions.models import Region, Mahalla, District
from apps.users.models import User


def cleanup_database():
    """Delete all data except users."""

    print("Current database statistics:")
    print(f"  Users: {User.objects.count()}")
    print(f"  QR Codes: {QRCode.objects.count()}")
    print(f"  Scan Logs: {ScanLog.objects.count()}")
    print(f"  Houses: {House.objects.count()}")
    print(f"  Mahallas: {Mahalla.objects.count()}")
    print(f"  Districts: {District.objects.count()}")
    print(f"  Regions: {Region.objects.count()}")

    print("\n" + "=" * 50)
    print("⚠️  WARNING: This will delete ALL data except users!")
    print("=" * 50)

    # Confirm deletion
    confirm = input("\nDo you want to proceed? Type 'DELETE ALL' to confirm: ")

    if confirm == "DELETE ALL":
        print("\nDeleting data...")

        # Delete in correct order (due to foreign keys)
        scan_logs_deleted = ScanLog.objects.all().delete()
        print(f"✓ Deleted scan logs: {scan_logs_deleted[0]}")

        qrcodes_deleted = QRCode.objects.all().delete()
        print(f"✓ Deleted QR codes: {qrcodes_deleted[0]}")

        houses_deleted = House.objects.all().delete()
        print(f"✓ Deleted houses: {houses_deleted[0]}")

        mahallas_deleted = Mahalla.objects.all().delete()
        print(f"✓ Deleted mahallas: {mahallas_deleted[0]}")

        districts_deleted = District.objects.all().delete()
        print(f"✓ Deleted districts: {districts_deleted[0]}")

        regions_deleted = Region.objects.all().delete()
        print(f"✓ Deleted regions: {regions_deleted[0]}")

        print("\n" + "=" * 50)
        print("✅ Database cleaned successfully!")
        print("=" * 50)
        print(f"\nRemaining users: {User.objects.count()}")

    else:
        print("\n❌ Cleanup cancelled. Database not modified.")


if __name__ == "__main__":
    print("=" * 50)
    print("DATABASE CLEANUP SCRIPT")
    print("=" * 50)
    print()

    cleanup_database()
