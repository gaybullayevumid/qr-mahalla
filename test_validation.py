#!/usr/bin/env python
"""Test validation with wrong region/district IDs."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from apps.houses.views import HouseViewSet
from apps.regions.models import Mahalla, Region, District
import json

print("=" * 80)
print("=== TEST: Region/District Validation ===")
print("=" * 80)

# Get mahalla and other region/district
mahalla = Mahalla.objects.select_related("district__region").first()
wrong_region = Region.objects.exclude(id=mahalla.district.region.id).first()
wrong_district = District.objects.exclude(id=mahalla.district.id).first()

print(f"\n✅ Mahalla: {mahalla.name} (ID: {mahalla.id})")
print(
    f"   Correct Region: {mahalla.district.region.name} (ID: {mahalla.district.region.id})"
)
print(f"   Correct District: {mahalla.district.name} (ID: {mahalla.district.id})")

if wrong_region:
    print(f"   Wrong Region: {wrong_region.name} (ID: {wrong_region.id})")
if wrong_district:
    print(f"   Wrong District: {wrong_district.name} (ID: {wrong_district.id})")

factory = RequestFactory()
viewset = HouseViewSet.as_view({"post": "create"})

# Test 1: Wrong region ID
if wrong_region:
    print("\n" + "=" * 80)
    print("=== TEST 1: Wrong Region ID ===")
    print("=" * 80)

    data = {
        "region": wrong_region.id,  # WRONG
        "district": mahalla.district.id,
        "mahalla": mahalla.id,
        "phone": "901111111",
        "ownerFirstName": "Test",
        "ownerLastName": "User",
        "address": "Test address",
        "houseNumber": "123",
    }

    print(f"\nSending region ID {wrong_region.id} ({wrong_region.name})")
    print(
        f"But mahalla belongs to region ID {mahalla.district.region.id} ({mahalla.district.region.name})"
    )

    request = factory.post(
        "/api/houses/", data=json.dumps(data), content_type="application/json"
    )
    response = viewset(request)

    print(f"\n✅ Status: {response.status_code}")
    print("Response:")
    print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Test 2: Wrong district ID
if wrong_district:
    print("\n" + "=" * 80)
    print("=== TEST 2: Wrong District ID ===")
    print("=" * 80)

    data = {
        "region": mahalla.district.region.id,
        "district": wrong_district.id,  # WRONG
        "mahalla": mahalla.id,
        "phone": "902222222",
        "ownerFirstName": "Test",
        "ownerLastName": "User",
        "address": "Test address",
        "houseNumber": "456",
    }

    print(f"\nSending district ID {wrong_district.id} ({wrong_district.name})")
    print(
        f"But mahalla belongs to district ID {mahalla.district.id} ({mahalla.district.name})"
    )

    request = factory.post(
        "/api/houses/", data=json.dumps(data), content_type="application/json"
    )
    response = viewset(request)

    print(f"\n✅ Status: {response.status_code}")
    print("Response:")
    print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Test 3: Correct IDs
print("\n" + "=" * 80)
print("=== TEST 3: Correct IDs ===")
print("=" * 80)

data = {
    "region": mahalla.district.region.id,  # CORRECT
    "district": mahalla.district.id,  # CORRECT
    "mahalla": mahalla.id,
    "phone": "903333333",
    "ownerFirstName": "Test",
    "ownerLastName": "User",
    "address": "Test address",
    "houseNumber": "789",
}

print(f"\nAll IDs correct:")
print(f"  Region: {mahalla.district.region.id}")
print(f"  District: {mahalla.district.id}")
print(f"  Mahalla: {mahalla.id}")

request = factory.post(
    "/api/houses/", data=json.dumps(data), content_type="application/json"
)
response = viewset(request)

print(f"\n✅ Status: {response.status_code}")
print("Response:")
print(json.dumps(response.data, indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
print("=== ✅ VALIDATION TESTS COMPLETED ===")
print("=" * 80)
