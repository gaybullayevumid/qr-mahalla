import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
from apps.users.models import User
from apps.qrcodes.models import QRCode
from apps.regions.models import Mahalla

# Get 2nd QR code
qr = QRCode.objects.filter(house__isnull=True)[1]  # 2-chi QR

user, _ = User.objects.get_or_create(phone="+998905005005", defaults={"role": "client"})

mahalla = Mahalla.objects.first()

claim_data = {
    "first_name": "Test",
    "last_name": "User",
    "address": "Test address",
    "house_number": "99",
    "mahalla": mahalla.id,
}

headers = {"Authorization": f"Phone {user.phone}"}

response = requests.post(
    f"http://127.0.0.1:8000/api/qrcodes/claim/{qr.uuid}/",
    headers=headers,
    json=claim_data,
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ SUCCESS!")
    print(response.json())
else:
    print("❌ Error")
    print(response.text[:500])
