import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User

# Get superuser
user = User.objects.get(phone="+998901234567")
client = APIClient()
client.force_authenticate(user=user)

print("=" * 70)
print("🧪 TESTING ALL NEIGHBORHOODS ENDPOINTS")
print("=" * 70)

# Test standalone neighborhoods endpoint
print("\n1️⃣ GET /api/neighborhoods/")
response = client.get("/api/neighborhoods/")
print(f"Status: {response.status_code}")
print(f"Count: {len(response.data) if response.status_code == 200 else 'N/A'}")

# Create a test neighborhood
print("\n2️⃣ POST /api/neighborhoods/ (should work now)")
# First create a district
region = client.post("/api/regions/", {"name": "Test Region"}, format="json")
district = client.post("/api/districts/", {"name": "Test District", "region": region.data['id']}, format="json")

neighborhood_data = {
    "name": "Test Neighborhood",
    "district": district.data['id']
}
response = client.post("/api/neighborhoods/", neighborhood_data, format="json")
print(f"Status: {response.status_code}")
print(f"Response: {response.data}")

# Test nested endpoints
print("\n3️⃣ GET /api/regions/{id}/neighborhoods/")
response = client.get(f"/api/regions/{region.data['id']}/neighborhoods/")
print(f"Status: {response.status_code}")
print(f"Count: {len(response.data)}")

print("\n4️⃣ GET /api/districts/{id}/neighborhoods/")
response = client.get(f"/api/districts/{district.data['id']}/neighborhoods/")
print(f"Status: {response.status_code}")
print(f"Count: {len(response.data)}")

print("\n5️⃣ POST /api/districts/{id}/neighborhoods/")
response = client.post(f"/api/districts/{district.data['id']}/neighborhoods/", 
                       {"name": "Another Neighborhood"}, format="json")
print(f"Status: {response.status_code}")
print(f"Response: {response.data}")

print("\n" + "=" * 70)
print("✅ ALL ENDPOINTS TESTED!")
print("=" * 70)
