import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
from apps.users.models import User
from apps.qrcodes.models import QRCode
from apps.regions.models import Mahalla

print("🧪 Testing FULL Claim Workflow\n")

base_url = "http://127.0.0.1:8000"

# Create NEW test user
client, created = User.objects.get_or_create(
    phone="+998901111222",
    defaults={
        "role": "client",
        "first_name": "",
        "last_name": "",
    },
)

if not created:
    # Reset user data
    client.first_name = ""
    client.last_name = ""
    client.save()

print(f"User: {client.phone}")
print(f"Before: first_name='{client.first_name}', last_name='{client.last_name}'")

# Get unclaimed QR code
qr = QRCode.objects.filter(house__isnull=True).first()
if not qr:
    print("❌ No unclaimed QR codes")
    exit(1)

print(f"\nQR Code: {qr.uuid}")
print(f"QR has house: {qr.house is not None}\n")

# Get mahalla
mahalla = Mahalla.objects.first()
if not mahalla:
    print("❌ No mahalla")
    exit(1)

print(f"Mahalla: {mahalla.name} (ID: {mahalla.id})\n")

# Headers
headers = {"Authorization": f"Phone {client.phone}"}

# Claim data
claim_data = {
    "first_name": "Aziz",
    "last_name": "Azizov",
    "address": "Chilonzor 12-mavze",
    "house_number": "45A",
    "mahalla": mahalla.id,
}

print("=" * 60)
print("CLAIM REQUEST")
print("=" * 60)
print(f"\nPOST /api/qrcodes/claim/{qr.uuid}/")
print(f"\nData:")
for k, v in claim_data.items():
    print(f"  {k}: {v}")

try:
    response = requests.post(
        f"{base_url}/api/qrcodes/claim/{qr.uuid}/", headers=headers, json=claim_data
    )

    print(f"\n📡 Status: {response.status_code}\n")

    if response.status_code == 200:
        print("✅ SUCCESS!")
        data = response.json()

        print(f"\nMessage: {data.get('message')}")

        print(f"\nHouse:")
        house = data.get("house", {})
        for k, v in house.items():
            print(f"  {k}: {v}")

        print(f"\nOwner:")
        owner = data.get("owner", {})
        for k, v in owner.items():
            print(f"  {k}: {v}")

        print(f"\nQR:")
        qr_data = data.get("qr", {})
        for k, v in qr_data.items():
            if k != "qr_url":
                print(f"  {k}: {v}")

        # Verify
        client.refresh_from_db()
        qr_obj = QRCode.objects.get(uuid=qr.uuid)

        print(f"\n" + "=" * 60)
        print("VERIFICATION")
        print("=" * 60)
        print(f"\nUser updated:")
        print(f"  first_name: {client.first_name}")
        print(f"  last_name: {client.last_name}")

        print(f"\nQR Code linked:")
        print(f"  house: {qr_obj.house}")
        if qr_obj.house:
            print(f"  house.owner: {qr_obj.house.owner.phone}")
            print(f"  house.address: {qr_obj.house.address}")

    elif response.status_code == 500:
        print("❌ SERVER ERROR")
        # Try to extract error from HTML
        text = response.text
        if "IntegrityError" in text:
            print("\n⚠️  Database IntegrityError detected")
            if "UNIQUE constraint" in text:
                print("  Issue: UNIQUE constraint violation")
                # Extract constraint name
                import re

                match = re.search(r"UNIQUE constraint failed: (\w+\.\w+)", text)
                if match:
                    print(f"  Field: {match.group(1)}")
        print(f"\nFirst 500 chars of response:")
        print(text[:500])

    elif response.status_code == 400:
        print("❌ BAD REQUEST")
        data = response.json()
        print(f"\nError: {data}")
    else:
        print(f"⚠️  Unexpected status")
        print(response.text[:300])

except requests.exceptions.ConnectionError:
    print("❌ Server not running")
    print("\nStart: python manage.py runserver 0.0.0.0:8000")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
