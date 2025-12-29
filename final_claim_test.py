import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
from apps.users.models import User
from apps.qrcodes.models import QRCode

qr = QRCode.objects.first()
user = User.objects.first()

claim_data = {
    "first_name": "Aziz",
    "last_name": "Azizov",
    "address": "Chilonzor 12-mavze",
    "house_number": "25",
    "mahalla": 1,
}

headers = {"Authorization": f"Phone {user.phone}"}

print(f"Testing claim for QR: {qr.uuid}\n")

response = requests.post(
    f"http://127.0.0.1:8000/api/qrcodes/claim/{qr.uuid}/",
    headers=headers,
    json=claim_data,
)

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    print("✅ SUCCESS!")
    data = response.json()
    print(f"\nMessage: {data.get('message')}")
    print(f"\nHouse:")
    for k, v in data.get("house", {}).items():
        print(f"  {k}: {v}")
    print(f"\nOwner:")
    for k, v in data.get("owner", {}).items():
        print(f"  {k}: {v}")
else:
    print("❌ Error")
    if "IntegrityError" in response.text:
        print("IntegrityError detected")
    print(response.text[:300])
