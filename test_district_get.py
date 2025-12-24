import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User
from apps.regions.models import Region

# Get superuser
user = User.objects.get(phone="+998901234567")
client = APIClient()
client.force_authenticate(user=user)

# Create region
simple_region = client.post(
    "/api/regions/", {"name": "Test Region Debug"}, format="json"
)
region_id = simple_region.data["id"]

# Create district with mahallas
district_data = {
    "name": "Debug District",
    "region": region_id,
    "mahallas": [{"name": "Debug Mahalla A"}, {"name": "Debug Mahalla B"}],
}

response = client.post("/api/districts/", district_data, format="json")
print(f"POST Response:")
print(f"  Status: {response.status_code}")
print(f"  Data: {response.data}")

district_id = response.data["id"]

# Now GET the same district
print(f"\nGET /api/districts/{district_id}/")
response = client.get(f"/api/districts/{district_id}/")
print(f"  Status: {response.status_code}")
print(f"  Data: {response.data}")

# Also check list
print(f"\nGET /api/districts/ (last item)")
response = client.get(f"/api/districts/")
if response.data:
    last_item = [d for d in response.data if d["id"] == district_id]
    if last_item:
        print(f"  Data: {last_item[0]}")
