import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User
from apps.regions.models import Region

# Get or create test superuser with super_admin role
try:
    user = User.objects.get(phone="+998901234567")
    if user.role != "super_admin":
        user.role = "super_admin"
        user.save()
except User.DoesNotExist:
    user = User.objects.create_superuser(
        phone="+998901234567",
        password="testpass123",
        first_name="Admin",
        last_name="User",
    )
    user.role = "super_admin"
    user.save()

# Get or create a test region
region, _ = Region.objects.get_or_create(name="Test Region")

# Test API
client = APIClient()
client.force_authenticate(user=user)

print(f"🔐 User: {user.phone} (role: {user.role})")

# Test POST to districts
print("\n📍 Testing POST /api/districts/")
data = {"name": "Test District", "region": region.id}

response = client.post("/api/districts/", data, format="json")
print(f"Status: {response.status_code}")
print(f"Response: {response.data}")

# Test nested with mahallas
print("\n📍 Testing POST /api/districts/ (with nested mahallas)")
data_nested = {
    "name": "Test District Nested",
    "region": region.id,
    "mahallas": [{"name": "Mahalla 1"}, {"name": "Mahalla 2"}],
}

response = client.post("/api/districts/", data_nested, format="json")
print(f"Status: {response.status_code}")
print(f"Response: {response.data}")

# Test GET
print("\n📍 Testing GET /api/districts/")
response = client.get("/api/districts/")
print(f"Status: {response.status_code}")
print(f"Count: {len(response.data)}")
