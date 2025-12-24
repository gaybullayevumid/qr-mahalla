import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User

# Get user
user = User.objects.get(phone="+998901234567")
client = APIClient()
client.force_authenticate(user=user)

print("=" * 70)
print("🧪 TESTING PROFILE ENDPOINTS")
print("=" * 70)

# GET profile
print("\n1️⃣ GET /api/users/profile/")
response = client.get("/api/users/profile/")
print(f"Status: {response.status_code}")
print(f"Data: {response.data}")

# POST profile update
print("\n2️⃣ POST /api/users/profile/ (update)")
update_data = {
    "first_name": "Updated",
    "last_name": "Name",
    "passport_id": "AB1234567",
    "address": "New Address 123",
}
response = client.post("/api/users/profile/", update_data, format="json")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Updated successfully")
    print(f"   First name: {response.data.get('first_name')}")
    print(f"   Last name: {response.data.get('last_name')}")
    print(f"   Passport: {response.data.get('passport_id')}")
else:
    print(f"❌ Error: {response.data}")

# PUT profile update
print("\n3️⃣ PUT /api/users/profile/ (full update)")
update_data = {"first_name": "Admin", "last_name": "User"}
response = client.put("/api/users/profile/", update_data, format="json")
print(f"Status: {response.status_code}")
print(f"First name: {response.data.get('first_name')}")

# PATCH profile update
print("\n4️⃣ PATCH /api/users/profile/ (partial update)")
update_data = {"address": "Final Address"}
response = client.patch("/api/users/profile/", update_data, format="json")
print(f"Status: {response.status_code}")
print(f"Address: {response.data.get('address')}")

print("\n" + "=" * 70)
print("✅ PROFILE TESTS COMPLETED!")
print("=" * 70)
