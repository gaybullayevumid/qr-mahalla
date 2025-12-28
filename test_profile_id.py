import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User

# Create test user
try:
    user = User.objects.get(phone="+998991234567")
except User.DoesNotExist:
    user = User.objects.create(
        phone="+998991234567",
        first_name="Test",
        last_name="User",
        role="client",
        is_verified=True,
    )

client = APIClient()
client.force_authenticate(user=user)

print("=" * 70)
print("🧪 TESTING PROFILE ENDPOINT")
print("=" * 70)

# GET profile
print("\n1️⃣ GET /api/users/profile/")
response = client.get("/api/users/profile/")
print(f"Status: {response.status_code}")
print(f"Response data:")
import json

print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Check if id exists
if "id" in response.data:
    print(f"\n✅ ID field exists: {response.data['id']}")
else:
    print(f"\n❌ ID field NOT FOUND!")
    print(f"Available fields: {list(response.data.keys())}")

print("\n" + "=" * 70)
