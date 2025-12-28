import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
from apps.users.models import User
from apps.qrcodes.models import QRCode

print("🧪 Testing API with PhoneAuthentication\n")

base_url = "http://127.0.0.1:8000"

# Create test user
client, _ = User.objects.get_or_create(
    phone="+998901234999",
    defaults={
        "role": "client",
        "first_name": "Test",
        "last_name": "Client",
    },
)

print(f"Client: {client.phone} (role: {client.role})")

# Get first QR code UUID
qr = QRCode.objects.first()
if not qr:
    print("❌ No QR codes in database")
    exit(1)

print(f"Test QR UUID: {qr.uuid}\n")

# Use Phone authentication
headers = {"Authorization": f"Phone {client.phone}"}

# Test endpoints
tests = [
    {
        "name": "List QR Codes",
        "method": "GET",
        "url": f"{base_url}/api/qrcodes/",
    },
    {
        "name": "Get QR Code Detail by UUID",
        "method": "GET",
        "url": f"{base_url}/api/qrcodes/{qr.uuid}/",
    },
    {
        "name": "Scan QR Code (POST with auth)",
        "method": "POST",
        "url": f"{base_url}/api/qrcodes/scan/",
        "data": {"uuid": qr.uuid},
    },
]

print("=" * 60)
print("RUNNING API TESTS")
print("=" * 60)

for test in tests:
    print(f"\n📡 {test['name']}")
    print(f"   {test['method']} {test['url']}")
    print(f"   Auth: {headers['Authorization']}")

    try:
        if test["method"] == "GET":
            response = requests.get(test["url"], headers=headers)
        elif test["method"] == "POST":
            response = requests.post(
                test["url"], headers=headers, json=test.get("data", {})
            )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print(f"   ✅ SUCCESS!")
            data = response.json()
            if isinstance(data, list):
                print(f"   Found {len(data)} items")
                if data:
                    print(f"   First item keys: {list(data[0].keys())}")
            else:
                print(f"   Response keys: {list(data.keys())}")
        elif response.status_code == 500:
            print(f"   ❌ SERVER ERROR (500)!")
            print(f"   Response: {response.text[:300]}")
        else:
            print(f"   ⚠️  Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")

    except requests.exceptions.ConnectionError:
        print(f"   ❌ Server not running!")
        print(f"\n   Please start server in another terminal:")
        print(f"   python manage.py runserver")
        break
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()

print("\n" + "=" * 60)
print("\nIf server is not running, start it with:")
print("python manage.py runserver")
