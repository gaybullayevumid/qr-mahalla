import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
import requests

print("🧪 Testing QR Code API...\n")

# Get first QR code
qr = QRCode.objects.first()
if not qr:
    print("❌ No QR codes found")
    exit(1)

print(f"Testing with QR UUID: {qr.uuid}")
print(f"QR URL: {qr.get_qr_url()}")
print(f"Image path: {qr.image.name if qr.image else 'No image'}")

# Test scan endpoint
url = "http://127.0.0.1:8000/api/qrcodes/scan/"
data = {"uuid": qr.uuid}

try:
    response = requests.post(url, json=data)
    print(f"\n📡 Response Status: {response.status_code}")

    if response.status_code == 200:
        print("✅ Success!")
        result = response.json()
        print(f"\nResponse data:")
        print(f"  Status: {result.get('status')}")
        print(f"  Message: {result.get('message')}")
        if result.get("qr"):
            print(f"  QR UUID: {result['qr'].get('uuid')}")
            print(f"  QR URL: {result['qr'].get('qr_url')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ Server is not running. Start with: python manage.py runserver")
except Exception as e:
    print(f"❌ Error: {str(e)}")
