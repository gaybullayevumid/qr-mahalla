import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User
from apps.houses.models import House
from apps.users.serializers import UserListSerializer
from django.test import RequestFactory

print("=" * 60)
print("=== Testing House Deletion Effect on User List ===")
print("=" * 60)

# Get user
user = User.objects.get(phone="+998906252919")

# Create a mock request with authenticated user
factory = RequestFactory()
request = factory.get("/api/users/list/")
request.user = user  # Simulate authenticated user

# Before deletion
print("\n📊 BEFORE DELETION:")
print(f"   User: {user.first_name} {user.last_name}")
print(f"   Houses count: {user.houses.count()}")

# Serialize user BEFORE deletion
serializer_before = UserListSerializer(user, context={"request": request})
data_before = serializer_before.data
print(f"\n   Serialized houses: {len(data_before['houses'])}")
if data_before["houses"]:
    for i, house in enumerate(data_before["houses"], 1):
        print(f"   House {i}: {house['address']} (ID: {house['id']})")

# Delete all houses
print("\n🗑️  DELETING HOUSES...")
deleted_count = user.houses.count()
user.houses.all().delete()
print(f"   Deleted {deleted_count} house(s)")

# After deletion
print("\n📊 AFTER DELETION:")
print(f"   Houses count: {user.houses.count()}")

# Serialize user AFTER deletion (with same request context)
serializer_after = UserListSerializer(user, context={"request": request})
data_after = serializer_after.data
print(f"   Serialized houses: {len(data_after['houses'])}")

print("\n" + "=" * 60)
print("=== Result ===")
print("=" * 60)
if len(data_after["houses"]) == 0:
    print("✅ SUCCESS: Deleted houses removed from user list!")
    print("✅ User list response automatically updates")
else:
    print("❌ FAIL: Houses still appear in user list")

print("\n" + "=" * 60)
print("=== User List Response After Deletion ===")
print("=" * 60)
import json

print(json.dumps(data_after, indent=2, ensure_ascii=False))
