import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
from apps.users.models import User
from apps.qrcodes.models import QRCode

print("🧪 Testing ScanQRCodeView (GET endpoint)\n")

base_url = "http://127.0.0.1:8000"

# Create test user
client, _ = User.objects.get_or_create(
    phone="+998930850955",
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

print(f"Test QR UUID: {qr.uuid}")
print(f"QR has house: {qr.house is not None}\n")

# Use Phone authentication
headers = {"Authorization": f"Phone {client.phone}"}

# Test scan endpoint (GET)
url = f"{base_url}/api/qrcodes/scan/{qr.uuid}/"

print("=" * 60)
print("Testing GET /api/qrcodes/scan/<uuid>/")
print("=" * 60)

try:
    response = requests.get(url, headers=headers)

    print(f"\n📡 Response Status: {response.status_code}")

    if response.status_code == 200:
        print("✅ SUCCESS!")
        data = response.json()
        print(f"\nResponse data:")
        print(f"  status: {data.get('status')}")
        print(f"  message: {data.get('message')}")
        print(f"  qr.uuid: {data.get('qr', {}).get('uuid')}")
        print(f"  house: {data.get('house')}")
    elif response.status_code == 500:
        print("❌ SERVER ERROR (500)!")
        print(f"\nResponse:\n{response.text[:500]}")
    else:
        print(f"⚠️  Status {response.status_code}")
        print(f"Response: {response.text[:300]}")

except requests.exceptions.ConnectionError:
    print("❌ Server not running!")
    print("\nPlease start server: python manage.py runserver 0.0.0.0:8000")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
