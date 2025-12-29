import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
from apps.users.models import User
from apps.qrcodes.models import QRCode
from apps.regions.models import Mahalla

print("🧪 Testing ClaimHouseView - Uy egasi ma'lumotlarini qo'shish\n")

base_url = "http://127.0.0.1:8000"

# Create test user (foydalanuvchi)
client, _ = User.objects.get_or_create(
    phone="+998901234888",
    defaults={
        "role": "client",
        "first_name": "",  # Bo'sh, claim da to'ldiriladi
        "last_name": "",
    },
)

print(f"Client: {client.phone} (role: {client.role})")
print(
    f"Before claim - First name: '{client.first_name}', Last name: '{client.last_name}'"
)

# Get unclaimed QR code
qr = QRCode.objects.filter(house__isnull=True).first()
if not qr:
    qr = QRCode.objects.first()

if not qr:
    print("❌ No QR codes in database")
    exit(1)

print(f"\nTest QR UUID: {qr.uuid}")
print(f"QR has house: {qr.house is not None}")

# Get mahalla for test
mahalla = Mahalla.objects.first()
if not mahalla:
    print("❌ No mahalla in database")
    exit(1)

print(f"Test Mahalla: {mahalla.name} (ID: {mahalla.id})\n")

# Use Phone authentication
headers = {"Authorization": f"Phone {client.phone}"}

# Claim data
claim_data = {
    "first_name": "Test",
    "last_name": "Testov",
    "address": "Test ko'chasi",
    "house_number": "123",
    "mahalla": mahalla.id,
}

# Test claim endpoint
url = f"{base_url}/api/qrcodes/claim/{qr.uuid}/"

print("=" * 60)
print("Testing POST /api/qrcodes/claim/<uuid>/")
print("=" * 60)
print(f"\nClaim data:")
for key, value in claim_data.items():
    print(f"  {key}: {value}")

try:
    response = requests.post(url, headers=headers, json=claim_data)

    print(f"\n📡 Response Status: {response.status_code}")

    if response.status_code == 200:
        print("✅ SUCCESS!")
        data = response.json()
        print(f"\nResponse:")
        print(f"  message: {data.get('message')}")
        print(f"\nHouse info:")
        house = data.get("house", {})
        print(f"  id: {house.get('id')}")
        print(f"  address: {house.get('address')}")
        print(f"  number: {house.get('number')}")
        print(f"  mahalla: {house.get('mahalla')}")
        print(f"\nOwner info:")
        owner = data.get("owner", {})
        print(f"  phone: {owner.get('phone')}")
        print(f"  first_name: {owner.get('first_name')}")
        print(f"  last_name: {owner.get('last_name')}")
        print(f"  role: {owner.get('role')}")

        # Verify user was updated
        client.refresh_from_db()
        print(f"\n✅ User updated successfully:")
        print(f"  First name: {client.first_name}")
        print(f"  Last name: {client.last_name}")

    elif response.status_code == 500:
        print("❌ SERVER ERROR (500)!")
        print(f"\nError details:")
        print(response.text[:1000])
    elif response.status_code == 400:
        print("❌ BAD REQUEST (400)")
        data = response.json()
        print(f"\nError: {data}")
    else:
        print(f"⚠️  Status {response.status_code}")
        print(f"Response: {response.text[:500]}")

except requests.exceptions.ConnectionError:
    print("❌ Server not running!")
    print("\nPlease start server: python manage.py runserver 0.0.0.0:8000")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
