#!/usr/bin/env python
"""Test houses GET endpoint."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from apps.houses.views import HouseViewSet
import json

print("=" * 80)
print("=== TEST: GET /api/houses/ ===")
print("=" * 80)

factory = RequestFactory()
viewset = HouseViewSet.as_view({"get": "list"})

# GET all houses
request = factory.get("/api/houses/")
response = viewset(request)

print(f"\n✅ Status: {response.status_code}")
print("\nResponse Data:")
print(json.dumps(response.data, indent=2, ensure_ascii=False))

# GET single house
if response.data and len(response.data) > 0:
    house_id = response.data[0]["id"]

    print("\n" + "=" * 80)
    print(f"=== TEST: GET /api/houses/{house_id}/ ===")
    print("=" * 80)

    detail_viewset = HouseViewSet.as_view({"get": "retrieve"})
    request = factory.get(f"/api/houses/{house_id}/")
    response = detail_viewset(request, pk=house_id)

    print(f"\n✅ Status: {response.status_code}")
    print("\nResponse Data:")
    print(json.dumps(response.data, indent=2, ensure_ascii=False))
