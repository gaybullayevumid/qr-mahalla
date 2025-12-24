import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User

# Get superuser
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

client = APIClient()
client.force_authenticate(user=user)

print("=" * 70)
print("🧪 TESTING NESTED CRUD")
print("=" * 70)

# Test 1: Create Region with nested Districts and Mahallas
print("\n1️⃣ CREATE Region with nested Districts and Mahallas")
print("-" * 70)
region_data = {
    "name": "Nested Test Region",
    "districts": [
        {
            "name": "First District",
            "mahallas": [
                {"name": "Mahalla 1A", "admin": None},
                {"name": "Mahalla 1B", "admin": None},
            ],
        },
        {
            "name": "Second District",
            "mahallas": [
                {"name": "Mahalla 2A"},
                {"name": "Mahalla 2B"},
                {"name": "Mahalla 2C"},
            ],
        },
    ],
}

response = client.post("/api/regions/", region_data, format="json")
print(f"Status: {response.status_code}")
if response.status_code == 201:
    print(f"✅ Created region ID: {response.data['id']}")
    print(f"   Region name: {response.data['name']}")
    print(f"   Districts count: {len(response.data.get('districts', []))}")
    for i, district in enumerate(response.data.get("districts", [])):
        print(f"     - District {i+1}: {district['name']} (ID: {district['id']})")
        print(f"       Mahallas: {len(district.get('mahallas', []))}")
    region_id = response.data["id"]
else:
    print(f"❌ Failed: {response.data}")
    region_id = None

# Test 2: GET Region with nested data
if region_id:
    print(f"\n2️⃣ GET Region {region_id} (check nested structure)")
    print("-" * 70)
    response = client.get(f"/api/regions/{region_id}/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Region: {response.data['name']}")
        for district in response.data.get("districts", []):
            print(f"   📍 District: {district['name']} (ID: {district['id']})")
            for mahalla in district.get("neighborhoods", []):
                print(f"      🏘️  Mahalla: {mahalla['name']} (ID: {mahalla['id']})")

# Test 3: UPDATE Region - add new district, modify existing
if region_id:
    print(f"\n3️⃣ UPDATE Region {region_id} - add/modify districts")
    print("-" * 70)

    # Get current data first
    response = client.get(f"/api/regions/{region_id}/")
    current_districts = response.data.get("districts", [])

    update_data = {
        "name": "Updated Nested Region",
        "districts": [
            {
                "id": current_districts[0]["id"],  # Keep first district
                "name": "Updated First District",
                "mahallas": [{"name": "New Mahalla 1C"}],  # Add new mahalla
            },
            # Second district removed (not in list)
            {
                # New district
                "name": "Third District (NEW)",
                "mahallas": [{"name": "Mahalla 3A"}],
            },
        ],
    }

    response = client.put(f"/api/regions/{region_id}/", update_data, format="json")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Updated!")
        print(f"   Districts now: {len(response.data.get('districts', []))}")
        for district in response.data.get("districts", []):
            print(
                f"     - {district['name']} (mahallas: {len(district.get('mahallas', []))})"
            )
    else:
        print(f"❌ Failed: {response.data}")

# Test 4: Create District with nested Mahallas directly
print("\n4️⃣ CREATE District with nested Mahallas (standalone)")
print("-" * 70)

# Create a simple region first
simple_region = client.post("/api/regions/", {"name": "Simple Region"}, format="json")
simple_region_id = simple_region.data["id"]

district_data = {
    "name": "Standalone Nested District",
    "region": simple_region_id,
    "mahallas": [{"name": "Standalone Mahalla A"}, {"name": "Standalone Mahalla B"}],
}

response = client.post("/api/districts/", district_data, format="json")
print(f"Status: {response.status_code}")
if response.status_code == 201:
    print(f"✅ Created district ID: {response.data['id']}")
    print(f"   District: {response.data['name']}")
    print(f"   Mahallas: {len(response.data.get('mahallas', []))}")
    for mahalla in response.data.get("mahallas", []):
        print(f"     - {mahalla['name']} (ID: {mahalla['id']})")
    district_id = response.data["id"]
else:
    print(f"❌ Failed: {response.data}")
    district_id = None

# Test 5: UPDATE District - modify nested mahallas
if district_id:
    print(f"\n5️⃣ UPDATE District {district_id} - modify mahallas")
    print("-" * 70)

    # Get current mahallas
    response = client.get(f"/api/districts/{district_id}/")
    current_mahallas = response.data.get(
        "neighborhoods", []
    )  # Changed from 'mahallas' to 'neighborhoods'

    if not current_mahallas:
        print("❌ No mahallas found to update")
    else:
        update_data = {
            "name": "Updated Standalone District",
            "region": simple_region_id,
            "mahallas": [
                {
                    "id": current_mahallas[0]["id"],  # Keep first
                    "name": "Updated Mahalla A",
                },
                # Second mahalla removed
                {"name": "New Mahalla C"},  # Add new
            ],
        }

        response = client.put(
            f"/api/districts/{district_id}/", update_data, format="json"
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Updated!")
            print(f"   Mahallas now: {len(response.data.get('mahallas', []))}")
            for mahalla in response.data.get("mahallas", []):
                print(f"     - {mahalla['name']} (ID: {mahalla['id']})")
        else:
            print(f"❌ Failed: {response.data}")

print("\n" + "=" * 70)
print("✅ NESTED CRUD TESTS COMPLETED!")
print("=" * 70)
