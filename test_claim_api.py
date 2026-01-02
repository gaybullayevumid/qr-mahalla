#!/usr/bin/env python
"""Test claim API endpoint directly."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from apps.qrcodes.views import ClaimHouseView
from apps.qrcodes.models import QRCode
from apps.users.models import User
from apps.regions.models import Mahalla

print("=" * 60)
print("=== Testing Claim API Endpoint ===")
print("=" * 60)

# Get unclaimed QR code
qr = QRCode.objects.filter(house__isnull=True).first()
if not qr:
    print("❌ No unclaimed QR codes found!")
    exit(1)

print(f"\n✅ QR Code: {qr.uuid}")

# Get user
user = User.objects.first()
if not user:
    print("❌ No users found!")
    exit(1)

print(f"✅ User: {user.phone}")

# Get mahalla
mahalla = Mahalla.objects.first()
if not mahalla:
    print("❌ No mahallas found!")
    exit(1)

print(f"✅ Mahalla: {mahalla.name} (ID={mahalla.id})")

# Create request
factory = RequestFactory()
request_data = {
    "first_name": "Frontend",
    "last_name": "User",
    "address": "Test Address from API",
    "house_number": "999",
    "mahalla": mahalla.id,
}

print(f"\n📤 Request Data:")
for key, value in request_data.items():
    print(f"   {key}: {value}")

# Create POST request
request = factory.post(
    f"/api/qrcodes/{qr.uuid}/claim/", data=request_data, content_type="application/json"
)
request.user = user

print("\n" + "=" * 60)
print("=== Calling ClaimHouseView.post() ===")
print("=" * 60)

# Call view
view = ClaimHouseView()
response = view.post(request, uuid=qr.uuid)

print(f"\n📥 Response Status: {response.status_code}")
print(f"📥 Response Data:")
import json

print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Check database
print("\n" + "=" * 60)
print("=== Database After Claim ===")
print("=" * 60)

from apps.houses.models import House

houses = House.objects.all()
print(f"Total Houses: {houses.count()}")
for h in houses:
    print(f"  House {h.id}:")
    print(f"    Address: {h.address}")
    print(f"    Number: {h.house_number}")
    print(f"    Mahalla: {h.mahalla.name}")
    print(f"    Owner: {h.owner.phone if h.owner else None}")

qr.refresh_from_db()
print(f"\nQR {qr.uuid}:")
print(f"  house_id: {qr.house_id}")
print(f"  has house: {qr.house is not None}")

if response.status_code == 200:
    print("\n✅ SUCCESS!")
else:
    print("\n❌ FAILED!")
