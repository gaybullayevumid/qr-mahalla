#!/usr/bin/env python
"""Test house CRUD operations."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from apps.houses.views import HouseViewSet
from apps.regions.models import Mahalla
from apps.houses.models import House
import json

print("=" * 80)
print("=== TEST: House CRUD Operations ===")
print("=" * 80)

# Get mahalla
mahalla = Mahalla.objects.select_related("district__region").first()
print(f"\n✅ Using Mahalla: {mahalla.name} (ID: {mahalla.id})")

factory = RequestFactory()
create_viewset = HouseViewSet.as_view({"post": "create"})
update_viewset = HouseViewSet.as_view({"put": "update", "patch": "partial_update"})

# TEST 1: Create house
print("\n" + "=" * 80)
print("=== TEST 1: POST /api/houses/ (Create) ===")
print("=" * 80)

create_data = {
    "region": mahalla.district.region.id,
    "district": mahalla.district.id,
    "mahalla": mahalla.id,
    "ownerFirstName": "Ali",
    "ownerLastName": "Valiyev",
    "phone": "905555555",
    "address": "Test manzil 1",
    "houseNumber": "100",
}

print("\nRequest:")
print(json.dumps(create_data, indent=2))

request = factory.post(
    "/api/houses/", data=json.dumps(create_data), content_type="application/json"
)
response = create_viewset(request)

print(f"\n✅ Status: {response.status_code}")
print("\nResponse:")
print(json.dumps(response.data, indent=2, ensure_ascii=False))

house_id = response.data.get("id")

# TEST 2: Update house (PUT - full update)
print("\n" + "=" * 80)
print("=== TEST 2: PUT /api/houses/{id}/ (Full Update) ===")
print("=" * 80)

update_data = {
    "region": mahalla.district.region.id,
    "district": mahalla.district.id,
    "mahalla": mahalla.id,
    "ownerFirstName": "Vali",
    "ownerLastName": "Aliyev",
    "phone": "906666666",  # Different owner
    "address": "Yangilangan manzil",
    "houseNumber": "200",
}

print("\nRequest:")
print(json.dumps(update_data, indent=2))

request = factory.put(
    f"/api/houses/{house_id}/",
    data=json.dumps(update_data),
    content_type="application/json",
)
response = update_viewset(request, pk=house_id)

print(f"\n✅ Status: {response.status_code}")
print("\nResponse:")
print(json.dumps(response.data, indent=2, ensure_ascii=False))

# TEST 3: Partial update (PATCH)
print("\n" + "=" * 80)
print("=== TEST 3: PATCH /api/houses/{id}/ (Partial Update) ===")
print("=" * 80)

patch_data = {
    "address": "Qisman yangilangan manzil",
    "houseNumber": "300",
    # owner va mahalla o'zgartirilmaydi
}

print("\nRequest:")
print(json.dumps(patch_data, indent=2))

request = factory.patch(
    f"/api/houses/{house_id}/",
    data=json.dumps(patch_data),
    content_type="application/json",
)
response = update_viewset(request, pk=house_id)

print(f"\n✅ Status: {response.status_code}")
print("\nResponse:")
print(json.dumps(response.data, indent=2, ensure_ascii=False))

# TEST 4: Update owner only
print("\n" + "=" * 80)
print("=== TEST 4: PATCH /api/houses/{id}/ (Change Owner Only) ===")
print("=" * 80)

patch_owner_data = {
    "phone": "907777777",
    "ownerFirstName": "Sardor",
    "ownerLastName": "Karimov",
}

print("\nRequest:")
print(json.dumps(patch_owner_data, indent=2))

request = factory.patch(
    f"/api/houses/{house_id}/",
    data=json.dumps(patch_owner_data),
    content_type="application/json",
)
response = update_viewset(request, pk=house_id)

print(f"\n✅ Status: {response.status_code}")
print("\nResponse:")
print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Verify final state
print("\n" + "=" * 80)
print("=== Final House State ===")
print("=" * 80)

house = House.objects.select_related("owner", "mahalla__district__region").get(
    id=house_id
)
print(f"\nHouse ID: {house.id}")
print(f"Owner: {house.owner.first_name} {house.owner.last_name} ({house.owner.phone})")
print(f"Mahalla: {house.mahalla.name}")
print(f"Address: {house.address}")
print(f"House Number: {house.house_number}")

print("\n" + "=" * 80)
print("=== ✅ ALL CRUD TESTS COMPLETED ===")
print("=" * 80)
