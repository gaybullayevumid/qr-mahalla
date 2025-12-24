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
print("🧪 TESTING NESTED ENDPOINTS")
print("=" * 70)

# Create a region
print("\n1️⃣ Create Region")
response = client.post(
    "/api/regions/", {"name": "Test Region for Nested"}, format="json"
)
print(f"Status: {response.status_code}")
region_id = response.data["id"]
print(f"Region ID: {region_id}")

# POST district to region
print(f"\n2️⃣ POST /api/regions/{region_id}/districts/")
district_data = {
    "name": "District via Nested Endpoint",
    "mahallas": [{"name": "Mahalla A"}, {"name": "Mahalla B"}],
}
response = client.post(
    f"/api/regions/{region_id}/districts/", district_data, format="json"
)
print(f"Status: {response.status_code}")
print(f"Response: {response.data}")

# GET districts from region
print(f"\n3️⃣ GET /api/regions/{region_id}/districts/")
response = client.get(f"/api/regions/{region_id}/districts/")
print(f"Status: {response.status_code}")
print(f"Districts count: {len(response.data)}")
if response.data:
    district_id = response.data[0]["id"]
    print(f"First district ID: {district_id}")

# POST mahalla to district
if response.data:
    print(f"\n4️⃣ POST /api/districts/{district_id}/neighborhoods/")
    mahalla_data = {"name": "Mahalla via Nested Endpoint"}
    response = client.post(
        f"/api/districts/{district_id}/neighborhoods/", mahalla_data, format="json"
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data}")

    # GET mahallas from district
    print(f"\n5️⃣ GET /api/districts/{district_id}/neighborhoods/")
    response = client.get(f"/api/districts/{district_id}/neighborhoods/")
    print(f"Status: {response.status_code}")
    print(f"Mahallas count: {len(response.data)}")
    for mahalla in response.data:
        print(f"  - {mahalla['name']} (ID: {mahalla['id']})")

# GET all mahallas from region
print(f"\n6️⃣ GET /api/regions/{region_id}/neighborhoods/")
response = client.get(f"/api/regions/{region_id}/neighborhoods/")
print(f"Status: {response.status_code}")
print(f"Total mahallas in region: {len(response.data)}")

print("\n" + "=" * 70)
print("✅ NESTED ENDPOINTS TESTS COMPLETED!")
print("=" * 70)
