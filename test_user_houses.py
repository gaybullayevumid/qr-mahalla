#!/usr/bin/env python
"""Test user list endpoint with houses."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from apps.users.views import UserViewSet
from apps.users.models import User

print("=" * 60)
print("=== Testing User List Endpoint with Houses ===")
print("=" * 60)

# Get user
user = User.objects.get(phone="+998906252919")
print(f"\n✅ User: {user.phone}")
print(f"   First name: {user.first_name}")
print(f"   Last name: {user.last_name}")
print(f"   Role: {user.role}")

# Check houses
houses = user.houses.all()
print(f"\n📊 User houses: {houses.count()}")
for house in houses:
    print(f"   House {house.id}: {house.address}")

# Create mock request
factory = RequestFactory()
request = factory.get("/api/users/list/")
request.user = user

# Call viewset
viewset = UserViewSet()
viewset.request = request
viewset.format_kwarg = None

# Get serializer
from apps.users.serializers import UserListSerializer

serializer = UserListSerializer(user, context={"request": request})
data = serializer.data

print("\n" + "=" * 60)
print("=== User List Serializer Response ===")
print("=" * 60)

import json

print(json.dumps(data, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("=== Result ===")
print("=" * 60)

if "houses" in data and len(data["houses"]) > 0:
    print("✅ SUCCESS: Houses included in user data!")
    print(f"✅ Houses count: {len(data['houses'])}")
else:
    print("❌ FAILED: Houses not included!")
