"""
Test QR code scanning with different user roles
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.users.models import User
from apps.houses.models import House
import requests

# Get a house with owner
house_with_owner = House.objects.filter(owner__isnull=False).first()
house_without_owner = House.objects.filter(owner__isnull=True).first()

# Create test users if not exist
admin_user, _ = User.objects.get_or_create(
    phone="+998901111111",
    defaults={"first_name": "Admin", "last_name": "User", "role": "admin"},
)

client_user, _ = User.objects.get_or_create(
    phone="+998902222222",
    defaults={"first_name": "Client", "last_name": "User", "role": "client"},
)

leader_user, _ = User.objects.get_or_create(
    phone="+998903333333",
    defaults={"first_name": "Leader", "last_name": "User", "role": "leader"},
)

gov_user, _ = User.objects.get_or_create(
    phone="+998904444444",
    defaults={"first_name": "Gov", "last_name": "User", "role": "gov"},
)

print("=" * 80)
print("ROLE-BASED QR CODE SCAN TEST")
print("=" * 80)

# Get QR codes
qr_unclaimed = QRCode.objects.filter(house__owner__isnull=True).first()
qr_claimed = QRCode.objects.filter(house__owner__isnull=False).first()

if qr_unclaimed:
    print(f"\nTest QR (Unclaimed): {qr_unclaimed.uuid}")
    print(f"House: {qr_unclaimed.house.address}")
    print(f"Telegram URL: {qr_unclaimed.get_qr_url()}")
    telegram_url = qr_unclaimed.get_qr_url()

    # Test 1: Anonymous user (telefon kamerasi, login bo'lmagan)
    print("\n" + "-" * 80)
    print("TEST 1: ANONYMOUS USER (telefon kamerasidan scan, login yo'q)")
    print("-" * 80)

    response = requests.post(
        "http://127.0.0.1:8000/api/qrcodes/scan/", json={"url": telegram_url}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Response status: {data.get('status')}")
        print(f"Message: {data.get('message')}")
        print(f"Can claim: {data.get('can_claim')}")
        print(f"QR URL included: {'qr_url' in data.get('qr', {})}")
        if "owner" in data:
            print(f"Owner data: {data.get('owner')}")
    else:
        print(f"ERROR: {response.status_code}")
        print(response.text)

    # Test 2: Client user (oddiy foydalanuvchi)
    print("\n" + "-" * 80)
    print("TEST 2: CLIENT USER (telefon kamerasidan scan, client role)")
    print("-" * 80)

    # Login qilish (token olish)
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(client_user)
    access_token = str(refresh.access_token)

    response = requests.post(
        "http://127.0.0.1:8000/api/qrcodes/scan/",
        json={"url": telegram_url},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Response status: {data.get('status')}")
        print(f"Can claim: {data.get('can_claim')}")
        print(f"Claim URL: {data.get('claim_url', 'NOT PROVIDED')}")
        print(f"QR URL included: {'qr_url' in data.get('qr', {})}")
    else:
        print(f"ERROR: {response.status_code}")
        print(response.text)

    # Test 3: Admin user
    print("\n" + "-" * 80)
    print("TEST 3: ADMIN USER (telefon kamerasidan scan, admin role)")
    print("-" * 80)

    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)

    response = requests.post(
        "http://127.0.0.1:8000/api/qrcodes/scan/",
        json={"url": telegram_url},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Can claim: {data.get('can_claim')}")
        print(f"House ID shown: {'id' in data.get('house', {})}")
        print(f"QR ID shown: {'id' in data.get('qr', {})}")
    else:
        print(f"ERROR: {response.status_code}")

if qr_claimed:
    print("\n" + "=" * 80)
    print(f"Test QR (Claimed): {qr_claimed.uuid}")
    print(f"House: {qr_claimed.house.address}")
    print(
        f"Owner: {qr_claimed.house.owner.first_name} {qr_claimed.house.owner.last_name}"
    )
    print(f"Owner role: {qr_claimed.house.owner.role}")
    telegram_url = qr_claimed.get_qr_url()

    # Test 4: Anonymous user scanning claimed house
    print("\n" + "-" * 80)
    print("TEST 4: ANONYMOUS - Claimed house scan")
    print("-" * 80)

    response = requests.post(
        "http://127.0.0.1:8000/api/qrcodes/scan/", json={"url": telegram_url}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Response status: {data.get('status')}")
        owner = data.get("owner", {})
        print(f"Owner info shown:")
        print(f"  - ID: {'id' in owner}")
        print(
            f"  - Name: {owner.get('first_name', 'N/A')} {owner.get('last_name', 'N/A')}"
        )
        print(f"  - Phone: {owner.get('phone', 'N/A')}")
        print(f"  - Role: {'role' in owner}")
        print(f"  - Is verified: {'is_verified' in owner}")

    # Test 5: Admin scanning claimed house
    print("\n" + "-" * 80)
    print("TEST 5: ADMIN - Claimed house scan (to'liq ma'lumot)")
    print("-" * 80)

    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)

    response = requests.post(
        "http://127.0.0.1:8000/api/qrcodes/scan/",
        json={"url": telegram_url},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        owner = data.get("owner", {})
        print(f"Owner info shown (admin ko'rishi kerak):")
        print(f"  - ID: {'id' in owner}")
        print(
            f"  - Name: {owner.get('first_name', 'N/A')} {owner.get('last_name', 'N/A')}"
        )
        print(f"  - Phone: {owner.get('phone', 'N/A')}")
        print(f"  - Role: {owner.get('role', 'NOT SHOWN')}")
        print(f"  - Is verified: {owner.get('is_verified', 'NOT SHOWN')}")

print("\n" + "=" * 80)
print("SUMMARY:")
print("- Anonymous: Minimal info, can't claim")
print("- Client: Can claim unclaimed houses, minimal info on others")
print("- Admin/Gov/Leader: Full info including role & verification status")
print("=" * 80)
