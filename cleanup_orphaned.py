#!/usr/bin/env python
"""Clean orphaned house_id references."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House

print("=" * 60)
print("=== Cleaning Orphaned house_id References ===")
print("=" * 60)

existing_house_ids = set(House.objects.values_list("id", flat=True))
used_house_ids = set(
    QRCode.objects.filter(house_id__isnull=False).values_list("house_id", flat=True)
)
orphaned_ids = used_house_ids - existing_house_ids

print(f"\nExisting Houses: {len(existing_house_ids)}")
print(f"QRCodes with house_id: {len(used_house_ids)}")
print(f"Orphaned house_ids: {len(orphaned_ids)}")

if orphaned_ids:
    print(f"\n❌ Found {len(orphaned_ids)} orphaned house_ids:")
    print(f"   IDs: {sorted(list(orphaned_ids))}")

    # Clean them
    cleaned = QRCode.objects.filter(house_id__in=orphaned_ids).update(house_id=None)
    print(f"\n✅ Cleaned {cleaned} QRCode records")
else:
    print("\n✅ No orphaned house_ids found. Database is clean.")

print("\n" + "=" * 60)
print("=== Final State ===")
print("=" * 60)
remaining = QRCode.objects.filter(house_id__isnull=False).count()
print(f"QRCodes with house_id: {remaining}")
print(f"All should have valid Houses: {remaining == House.objects.count()}")
