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
print("🧪 TESTING USER UPDATE")
print("=" * 70)

# Try to get user 8
print("\n1️⃣ GET /api/users/list/8/")
response = client.get("/api/users/list/8/")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"User data: {response.data}")
else:
    print(f"Error: {response.data}")

# Try to update user 8
print("\n2️⃣ PUT /api/users/list/8/")
update_data = {"first_name": "Updated", "last_name": "User", "role": "user"}
response = client.put("/api/users/list/8/", update_data, format="json")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Success: {response.data}")
else:
    print(f"❌ Error: {response.data}")

# Try with phone
print("\n3️⃣ PUT /api/users/list/8/ (with phone)")
update_data = {
    "phone": "+998991234567",
    "first_name": "Updated",
    "last_name": "User",
    "role": "user",
}
response = client.put("/api/users/list/8/", update_data, format="json")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Success")
else:
    print(f"❌ Error: {response.data}")

# Try PATCH
print("\n4️⃣ PATCH /api/users/list/8/")
update_data = {"first_name": "Patched Name"}
response = client.patch("/api/users/list/8/", update_data, format="json")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Success")
else:
    print(f"❌ Error: {response.data}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETED!")
print("=" * 70)
