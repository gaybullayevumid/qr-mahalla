"""
QR kodlarni o'chirib, Telegram URL formati bilan qayta generate qilish
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House

print("=" * 70)
print("🔄 QR KODLARNI QAYTA GENERATE QILISH")
print("=" * 70)

# 1. Hozirgi QR kodlar sonini ko'rish
old_count = QRCode.objects.count()
print(f"\n📊 Hozirgi QR kodlar: {old_count}")

# 2. Barcha QR kodlarni o'chirish
if old_count > 0:
    print(f"\n🗑️  {old_count} ta QR kodni o'chirish...")
    QRCode.objects.all().delete()
    print("✅ Barcha eski QR kodlar o'chirildi")

# 3. Barcha uylar uchun yangi QR kod yaratish
houses = House.objects.all()
total_houses = houses.count()

print(f"\n📦 {total_houses} ta uy topildi")
print("🔨 Yangi QR kodlarni generate qilish...")

created_count = 0
for i, house in enumerate(houses, 1):
    qr = QRCode.objects.create(house=house)
    created_count += 1

    if i % 100 == 0:
        print(f"   ✓ {i}/{total_houses} QR kod yaratildi...")

print(f"\n✅ {created_count} ta yangi QR kod yaratildi!")

# 4. Namuna QR kodlarni ko'rsatish
print("\n" + "=" * 70)
print("📱 NAMUNA QR KODLAR (birinchi 5 ta)")
print("=" * 70)

sample_qrs = QRCode.objects.select_related("house__mahalla__district__region")[:5]

for qr in sample_qrs:
    print(f"\n🏠 Uy: {qr.house.address}")
    print(f"   📍 Mahalla: {qr.house.mahalla.name}")
    print(f"   🆔 UUID: {qr.uuid}")
    print(f"   🔗 Telegram URL: {qr.get_qr_url()}")
    print(f"   👤 Egasi: {qr.house.owner if qr.house.owner else 'Unclaimed'}")

print("\n" + "=" * 70)
print("✅ YAKUNLANDI!")
print("=" * 70)
