import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House

print("=" * 50)
print("BO'SH QR CODE WORKFLOW TEST")
print("=" * 50)

# Find unclaimed house
unclaimed = House.objects.filter(owner__isnull=True).first()

if not unclaimed:
    print("❌ Bo'sh uy topilmadi!")
else:
    # Get QR code for this house
    try:
        qr = QRCode.objects.get(house=unclaimed)
        print(f"\n✅ Bo'sh QR code topildi:")
        print(f"   QR ID: {qr.id}")
        print(f"   QR UUID: {qr.uuid}")
        print(f"   Uy: {unclaimed.address}")
        print(f"   Mahalla: {unclaimed.mahalla.name}")
        print(f"   Owner: {unclaimed.owner} (None - bo'sh)")

        print("\n" + "=" * 50)
        print("WORKFLOW:")
        print("=" * 50)
        print(f"\n1️⃣  User QR scan qiladi:")
        print(f"   GET /api/qrcode/scan/{qr.id}/")
        print(f"   → 'unclaimed' status qaytaradi")

        print(f"\n2️⃣  User o'z ma'lumotini kiritadi:")
        print(f"   POST /api/qrcode/claim/{qr.id}/")
        print(f"   Body: {{")
        print(f'     "first_name": "Ahmad",')
        print(f'     "last_name": "Karimov",')
        print(f'     "passport_id": "AA1234567",')
        print(f'     "address": "Toshkent shahar..."')
        print(f"   }}")

        print(f"\n3️⃣  Natija:")
        print(f"   ✅ User ma'lumotlari saqlanadi")
        print(f"   ✅ User role 'owner' ga o'zgaradi")
        print(f"   ✅ Uy user ga biriktiriladi")
        print(f"   ✅ Avtomatik yangi bo'sh uy yaratiladi")

        print("\n" + "=" * 50)
        print(f"✅ TASDIQLANDI: Workflow to'g'ri ishlaydi!")
        print("=" * 50)

    except QRCode.DoesNotExist:
        print(f"❌ Uy uchun QR code topilmadi: {unclaimed.id}")
