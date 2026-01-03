#!/usr/bin/env python
"""Test house creation with owner details via POST /api/houses/."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from apps.houses.views import HouseViewSet
from apps.regions.models import Mahalla
import json

print("=" * 80)
print("=== TEST: POST /api/houses/ with Admin Format ===")
print("=" * 80)

# Get a mahalla
mahalla = Mahalla.objects.select_related("district__region").first()
if not mahalla:
    print("❌ No mahalla found!")
    exit(1)

print(f"\n✅ Using Mahalla: {mahalla.name}")
print(f"   District: {mahalla.district.name}")
print(f"   Region: {mahalla.district.region.name}")

# Test data - Admin format with IDs
test_data = {
    "region": mahalla.district.region.id,  # ID not name
    "district": mahalla.district.id,  # ID not name
    "mahalla": mahalla.id,
    "ownerFirstName": "hhh",
    "ownerLastName": "ggg",
    "phone": "111111111",
    "address": "999999",
    "houseNumber": "88888",
}

print("\n" + "=" * 80)
print("=== TEST 1: POST /api/houses/ (Admin Format) ===")
print("=" * 80)
print("\nRequest Data:")
print(json.dumps(test_data, indent=2))

# Create request
factory = RequestFactory()
request = factory.post(
    "/api/houses/", data=json.dumps(test_data), content_type="application/json"
)

# Call view
viewset = HouseViewSet.as_view({"post": "create"})
response = viewset(request)

print(f"\n✅ Response Status: {response.status_code}")
print("\nResponse Data:")
print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Test phone normalization
print("\n" + "=" * 80)
print("=== TEST 2: Phone Number Normalization ===")
print("=" * 80)

phone_tests = [
    "901234567",  # Should become +998901234567
    "998901234567",  # Should become +998901234567
    "+998901234567",  # Should stay same
]

for phone in phone_tests:
    data = test_data.copy()
    data["phone"] = phone
    data["houseNumber"] = phone[-4:]  # Unique house number

    request = factory.post(
        "/api/houses/", data=json.dumps(data), content_type="application/json"
    )

    response = viewset(request)
    if response.status_code == 201:
        result_phone = response.data["owner"]["phone"]
        print(f"✅ {phone:20s} → {result_phone}")
    else:
        print(f"❌ {phone:20s} → Error: {response.data}")

print("\n" + "=" * 80)
print("=== ✅ ALL TESTS COMPLETED ===")
print("=" * 80)
