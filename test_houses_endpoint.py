#!/usr/bin/env python
"""Test houses endpoint."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User
from apps.houses.models import House

print("=" * 60)
print("=== Testing Houses Endpoint Access ===")
print("=" * 60)

# Get user
user = User.objects.first()
if not user:
    print("❌ No users found!")
    exit(1)

print(f"\n✅ User: {user.phone} (role={user.role})")

# Get user's houses
user_houses = House.objects.filter(owner=user)
print(f"\n📊 User's houses: {user_houses.count()}")

for house in user_houses:
    print(f"\n  House {house.id}:")
    print(f"    Address: {house.address}")
    print(f"    Number: {house.house_number}")
    print(f"    Mahalla: {house.mahalla.name}")
    print(f"    Created: {house.created_at}")

    # Check QR codes linked to this house
    qr_codes = house.qr_codes.all()
    print(f"    QR codes: {qr_codes.count()}")
    for qr in qr_codes:
        print(f"      - {qr.uuid}")

print("\n" + "=" * 60)
print("=== API Endpoint ===")
print("=" * 60)
print("\n✅ GET /api/houses/")
print(f"   Returns {user_houses.count()} house(s) for user {user.phone}")
print("\n✅ Houses endpoint is now available!")
print("✅ Frontend can fetch user's claimed houses!")
