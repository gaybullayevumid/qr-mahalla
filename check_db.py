#!/usr/bin/env python
"""Check database state for QRCode and House relationships."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House
from django.db.models import Count

print("=" * 60)
print("=== QRCode Table ===")
qrs = QRCode.objects.all()
print(f"Total QRCodes: {qrs.count()}")
for qr in qrs[:10]:
    print(
        f"  QR {qr.uuid[:8]}: house_id={qr.house_id}, has_house_obj={qr.house is not None}"
    )

print("\n" + "=" * 60)
print("=== House Table ===")
houses = House.objects.all()
print(f"Total Houses: {houses.count()}")
for h in houses[:10]:
    owner_phone = h.owner.phone if h.owner else None
    print(f"  House {h.id}: owner={owner_phone}, address={h.address[:30]}...")

print("\n" + "=" * 60)
print("=== Checking for orphaned house_id references ===")
all_house_ids = set(House.objects.values_list("id", flat=True))
qr_house_ids = set(
    QRCode.objects.filter(house_id__isnull=False).values_list("house_id", flat=True)
)
orphaned = qr_house_ids - all_house_ids
print(f"Orphaned house_ids in QRCode table: {len(orphaned)}")
if orphaned:
    print(f"  IDs: {sorted(list(orphaned))[:20]}")

print("\n" + "=" * 60)
print("=== Checking for duplicate house_id in QRCode ===")
duplicates = (
    QRCode.objects.filter(house_id__isnull=False)
    .values("house_id")
    .annotate(count=Count("house_id"))
    .filter(count__gt=1)
)
print(f"Duplicate house_id: {duplicates.count()}")
for dup in duplicates[:10]:
    house_id = dup["house_id"]
    count = dup["count"]
    print(f"  house_id {house_id}: used {count} times")
    qrs_with_this_house = QRCode.objects.filter(house_id=house_id)
    for qr in qrs_with_this_house:
        print(f"    - QR UUID: {qr.uuid}")

print("\n" + "=" * 60)
print("=== Summary ===")
if orphaned:
    print("❌ PROBLEM: Orphaned house_id references found!")
    print(f"   {len(orphaned)} QRCode records point to non-existent houses")
if duplicates.count() > 0:
    print("❌ PROBLEM: Duplicate house_id references found!")
    print(f"   {duplicates.count()} house_id values are used by multiple QRCodes")
if not orphaned and duplicates.count() == 0:
    print("✅ Database is clean - no orphaned or duplicate house_id references")
