"""
Script to delete all used/scanned QR codes from the database.
Only unused QR codes will remain.
"""

import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.scans.models import ScanLog


def delete_used_qrcodes():
    """Delete all QR codes that have been scanned."""

    # Get all scanned QR codes (is_scanned=True)
    scanned_qrcodes = QRCode.objects.filter(is_scanned=True)
    scanned_count = scanned_qrcodes.count()

    # Also get QR codes that have scan logs
    qr_ids_with_scans = ScanLog.objects.values_list("qr_id", flat=True).distinct()
    qrcodes_with_logs = QRCode.objects.filter(id__in=qr_ids_with_scans)
    logs_count = qrcodes_with_logs.count()

    print(f"QR codes marked as scanned: {scanned_count}")
    print(f"QR codes with scan logs: {logs_count}")

    # Get total count before deletion
    total_before = QRCode.objects.count()
    unused_count = (
        QRCode.objects.filter(is_scanned=False)
        .exclude(id__in=qr_ids_with_scans)
        .count()
    )

    print(f"\nTotal QR codes: {total_before}")
    print(f"Unused QR codes: {unused_count}")
    print(f"To be deleted: {total_before - unused_count}")

    # Confirm deletion
    confirm = input("\nDo you want to proceed with deletion? (yes/no): ")

    if confirm.lower() in ["yes", "y", "ha"]:
        # Delete scanned QR codes
        deleted_scanned = scanned_qrcodes.delete()

        # Delete QR codes with scan logs (if any remaining)
        deleted_with_logs = qrcodes_with_logs.delete()

        # Get final count
        total_after = QRCode.objects.count()

        print(f"\n✓ Deletion completed!")
        print(f"Deleted QR codes: {total_before - total_after}")
        print(f"Remaining QR codes: {total_after}")
    else:
        print("\nDeletion cancelled.")


if __name__ == "__main__":
    print("=" * 50)
    print("Delete Used QR Codes Script")
    print("=" * 50)
    print()

    delete_used_qrcodes()
