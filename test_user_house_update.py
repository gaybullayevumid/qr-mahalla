import os
import django
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User
from apps.houses.models import House
from apps.regions.models import Region, District, Mahalla

# Create test data
region = Region.objects.filter(name="Test Region").first()
if not region:
    region = Region.objects.create(name="Test Region")

district = District.objects.filter(name="Test District", region=region).first()
if not district:
    district = District.objects.create(name="Test District", region=region)

mahalla = Mahalla.objects.filter(name="Test Mahalla", district=district).first()
if not mahalla:
    mahalla = Mahalla.objects.create(name="Test Mahalla", district=district)

# Create user with house
user, created = User.objects.get_or_create(
    phone="+998991112233", defaults={"first_name": "Test", "role": "user"}
)

if created:
    print(f"✅ Created user: {user.id}")
else:
    print(f"✅ Using existing user: {user.id}")

# Delete old houses
House.objects.filter(owner=user).delete()

# Create house
house = House.objects.create(
    owner=user, mahalla=mahalla, address="Test Address", house_number="123"
)
print(f"✅ Created house: {house.id}")

# Test update with house data
import requests
from rest_framework_simplejwt.tokens import RefreshToken

# Generate token for user
refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)

url = f"http://127.0.0.1:8000/api/users/list/{user.id}/"

# Test 1: Update with existing house
data = {
    "first_name": "Updated Name",
    "houses": [
        {
            "id": house.id,
            "mahalla": mahalla.id,
            "address": "Updated Address",
            "house_number": "456",
        }
    ],
}

print(f"\n📤 PUT {url}")
print(f"Data: {data}")

response = requests.put(url, json=data, headers={"Authorization": f"Bearer {token}"})

print(f"\n📥 Response Status: {response.status_code}")
print(f"Response JSON:")
import json

try:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except:
    print(response.text)

if response.status_code == 400:
    print("\n❌ 400 ERROR DETAILS:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
