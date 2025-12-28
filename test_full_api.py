import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
from apps.users.models import User, PhoneOTP
from rest_framework.authtoken.models import Token

print("🧪 Testing Full QR Code API Endpoints\n")

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

# Create token for authentication
token, _ = Token.objects.get_or_create(user=client)
headers = {"Authorization": f"Token {token.key}"}

print(f"Client: {client.phone} (role: {client.role})")
print(f"Token: {token.key[:20]}...\n")

# Get first QR code UUID
from apps.qrcodes.models import QRCode

qr = QRCode.objects.first()

if not qr:
    print("❌ No QR codes in database")
    exit(1)

print(f"Test QR UUID: {qr.uuid}\n")

# Test endpoints
tests = [
    {
        "name": "List QR Codes",
        "method": "GET",
        "url": f"{base_url}/api/qrcodes/",
        "headers": headers,
    },
    {
        "name": "Get QR Code Detail by UUID",
        "method": "GET",
        "url": f"{base_url}/api/qrcodes/{qr.uuid}/",
        "headers": headers,
    },
    {
        "name": "Scan QR Code (POST)",
        "method": "POST",
        "url": f"{base_url}/api/qrcodes/scan/",
        "headers": headers,
        "data": {"uuid": qr.uuid},
    },
]

print("=" * 60)
print("RUNNING API TESTS")
print("=" * 60)

for test in tests:
    print(f"\n📡 {test['name']}")
    print(f"   {test['method']} {test['url']}")

    try:
        if test["method"] == "GET":
            response = requests.get(test["url"], headers=test.get("headers", {}))
        elif test["method"] == "POST":
            response = requests.post(
                test["url"], headers=test.get("headers", {}), json=test.get("data", {})
            )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print(f"   ✅ Success!")
            data = response.json()
            if isinstance(data, list):
                print(f"   Response: [{len(data)} items]")
            else:
                print(f"   Response keys: {list(data.keys())}")
        elif response.status_code == 500:
            print(f"   ❌ SERVER ERROR!")
            print(f"   Response: {response.text[:200]}")
        else:
            print(f"   ⚠️  Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")

    except requests.exceptions.ConnectionError:
        print(f"   ❌ Server not running!")
        print(f"\n   Please start server: python manage.py runserver")
        break
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

print("\n" + "=" * 60)
