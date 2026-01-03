#!/usr/bin/env python
"""Test admin house creation with owner details."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from apps.houses.views import HouseViewSet
from apps.regions.models import Mahalla
import json

print("=" * 80)
print("=== TEST: Admin Create House with Owner Details ===")
print("=" * 80)

# Get a mahalla
mahalla = Mahalla.objects.select_related("district__region").first()
if not mahalla:
    print("❌ No mahalla found!")
    exit(1)

print(f"\n✅ Using Mahalla: {mahalla.name}")
print(f"   District: {mahalla.district.name}")
print(f"   Region: {mahalla.district.region.name}")

# Test data
test_data = {
    "region": mahalla.district.region.name,
    "district": mahalla.district.name,
    "mahalla": mahalla.id,
    "ownerFirstName": "hhh",
    "ownerLastName": "ggg",
    "phone": "111111111",
    "address": "999999",
    "houseNumber": "88888",
}

print("\n" + "=" * 80)
print("=== TEST: POST /api/houses/admin-create/ ===")
print("=" * 80)
print("\nRequest Data:")
print(json.dumps(test_data, indent=2))

# Create request
factory = RequestFactory()
request = factory.post(
    "/api/houses/admin-create/",
    data=json.dumps(test_data),
    content_type="application/json",
)

# Call view
viewset = HouseViewSet.as_view({"post": "admin_create"})
response = viewset(request)

print(f"\n✅ Response Status: {response.status_code}")
print("\nResponse Data:")
print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Test with invalid mahalla
print("\n" + "=" * 80)
print("=== TEST: Invalid Region/District ===")
print("=" * 80)

invalid_data = test_data.copy()
invalid_data["region"] = "WrongRegion"

request = factory.post(
    "/api/houses/admin-create/",
    data=json.dumps(invalid_data),
    content_type="application/json",
)

response = viewset(request)
print(f"\n✅ Response Status: {response.status_code}")
print("\nResponse Data:")
print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Test phone normalization
print("\n" + "=" * 80)
print("=== TEST: Phone Number Normalization ===")
print("=" * 80)

phone_tests = [
    "901234567",  # Should become +998901234567
    "998901234567",  # Should become +998901234567
    "+998901234567",  # Should stay same
]

for phone in phone_tests:
    data = test_data.copy()
    data["phone"] = phone

    request = factory.post(
        "/api/houses/admin-create/",
        data=json.dumps(data),
        content_type="application/json",
    )

    response = viewset(request)
    if response.status_code == 201:
        result_phone = response.data["owner"]["phone"]
        print(f"✅ {phone:20s} → {result_phone}")
    else:
        print(f"❌ {phone:20s} → Error: {response.data}")

print("\n" + "=" * 80)
print("=== ✅ TEST COMPLETED ===")
print("=" * 80)
