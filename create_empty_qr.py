"""
Bo'sh QR kodlar yaratish - House ga bog'lanmagan
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode

print("=" * 80)
print("BO'SH QR KODLAR YARATISH")
print("=" * 80)

# Nechta QR kod yaratish kerakligini so'rash
count = int(input("\nNechta bo'sh QR kod yaratish kerak? (masalan: 50): "))

print(f"\n🔨 {count} ta bo'sh QR kod yaratilmoqda...")

created_count = 0
for i in range(count):
    qr = QRCode.objects.create()  # house=None (bo'sh)
    created_count += 1

    if (i + 1) % 10 == 0:
        print(f"   ✓ {i + 1}/{count} yaratildi...")

print(f"\n✅ {created_count} ta bo'sh QR kod yaratildi!")

# Namuna ko'rsatish
print("\n" + "=" * 80)
print("NAMUNA QR KODLAR (birinchi 5 ta)")
print("=" * 80)

sample_qrs = QRCode.objects.filter(house__isnull=True).order_by("-id")[:5]

for qr in sample_qrs:
    print(f"\n🆔 UUID: {qr.uuid}")
    print(f"   🔗 Telegram URL: {qr.get_qr_url()}")
    print(f"   🏠 House: Bo'sh (hali biriktirilmagan)")
    print(f"   📸 Image: {qr.image}")

# Statistika
print("\n" + "=" * 80)
print("STATISTIKA")
print("=" * 80)

total_qr = QRCode.objects.count()
empty_qr = QRCode.objects.filter(house__isnull=True).count()
with_house = QRCode.objects.filter(house__isnull=False).count()

print(f"\n📊 Jami QR kodlar: {total_qr}")
print(f"   ✅ House ga bog'langan: {with_house}")
print(f"   ❌ Bo'sh (house yo'q): {empty_qr}")

print("\n" + "=" * 80)
print("✅ TAYYOR!")
print("=" * 80)
print("\nEndi bu QR kodlarni frontend ga bering.")
print("User claim qilganda uy ma'lumotlarini kiritadi va uy yaratiladi.")
