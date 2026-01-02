#!/usr/bin/env python
"""Test multiple QR codes linked to same house."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House

print("=" * 60)
print("=== Test: Multiple QR codes per House ===")
print("=" * 60)

# Get existing house
house = House.objects.first()
if not house:
    print("❌ No houses found!")
    exit(1)

print(f"\n✅ House: {house.id} - {house.address}")
print(f"   Owner: {house.owner.phone if house.owner else None}")

# Get unclaimed QR codes
unclaimed_qrs = QRCode.objects.filter(house__isnull=True)[:2]

print(f"\n📝 Unclaimed QR codes: {unclaimed_qrs.count()}")

if unclaimed_qrs.count() < 2:
    print("❌ Need at least 2 unclaimed QR codes!")
    exit(1)

print("\n" + "=" * 60)
print("=== Linking Multiple QR codes to Same House ===")
print("=" * 60)

for qr in unclaimed_qrs:
    print(f"\n🔗 Linking QR {qr.uuid} to House {house.id}...")
    qr.house = house
    qr.save()
    print(f"   ✅ Success! QR {qr.uuid} linked to House {house.id}")

print("\n" + "=" * 60)
print("=== Results ===")
print("=" * 60)

# Check how many QR codes linked to this house
house_qr_codes = house.qr_codes.all()
print(f"\n✅ House {house.id} has {house_qr_codes.count()} QR codes:")
for qr in house_qr_codes:
    print(f"   - QR {qr.uuid}")

print("\n" + "=" * 60)
print("=== Database State ===")
print("=" * 60)

from django.db.models import Count

houses_with_multiple_qrs = House.objects.annotate(
    qr_count=Count('qr_codes')
).filter(qr_count__gt=1)

print(f"\nHouses with multiple QR codes: {houses_with_multiple_qrs.count()}")
for h in houses_with_multiple_qrs:
    print(f"  House {h.id}: {h.qr_count} QR codes")

print("\n✅ SUCCESS: Multiple QR codes can be linked to same house!")
print("✅ UNIQUE constraint removed from house_id field!")
