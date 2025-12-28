"""
Unclaimed uylarni tekshirish - House egasi yo'q uylar
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.houses.models import House
from apps.qrcodes.models import QRCode
from apps.users.models import User

print("=" * 80)
print("UNCLAIMED UYLAR TEKSHIRUVI")
print("=" * 80)

# Barcha uylar
total_houses = House.objects.count()
print(f"\n📊 Jami uylar: {total_houses}")

# Claimed uylar (owner bor)
claimed_houses = House.objects.filter(owner__isnull=False).count()
print(f"✅ Claimed (egasi bor): {claimed_houses}")

# Unclaimed uylar (owner yo'q)
unclaimed_houses = House.objects.filter(owner__isnull=True).count()
print(f"❌ Unclaimed (egasi yo'q): {unclaimed_houses}")

# Unclaimed uylar ro'yxati
print("\n" + "=" * 80)
print("UNCLAIMED UYLAR RO'YXATI:")
print("=" * 80)

unclaimed_list = House.objects.filter(owner__isnull=True).select_related(
    "mahalla__district__region"
)[:20]

for i, house in enumerate(unclaimed_list, 1):
    try:
        qr = QRCode.objects.get(house=house)
        qr_info = f"QR: {qr.uuid}"
    except QRCode.DoesNotExist:
        qr_info = "QR: YO'Q"

    print(f"\n{i}. 🏠 {house.address}")
    print(f"   ID: {house.id}")
    print(f"   Number: {house.house_number}")
    print(f"   Mahalla: {house.mahalla.name}")
    print(f"   District: {house.mahalla.district.name}")
    print(f"   Region: {house.mahalla.district.region.name}")
    print(f"   {qr_info}")
    print(f"   Owner: {house.owner if house.owner else 'NULL'}")

# Claimed uylar ro'yxati
print("\n" + "=" * 80)
print("CLAIMED UYLAR RO'YXATI (birinchi 10 ta):")
print("=" * 80)

claimed_list = House.objects.filter(owner__isnull=False).select_related(
    "owner", "mahalla__district__region"
)[:10]

for i, house in enumerate(claimed_list, 1):
    try:
        qr = QRCode.objects.get(house=house)
        qr_info = f"QR: {qr.uuid}"
    except QRCode.DoesNotExist:
        qr_info = "QR: YO'Q"

    print(f"\n{i}. 🏠 {house.address}")
    print(f"   ID: {house.id}")
    print(f"   Number: {house.house_number}")
    print(f"   Mahalla: {house.mahalla.name}")
    print(f"   {qr_info}")
    print(f"   👤 Owner: {house.owner.first_name} {house.owner.last_name}")
    print(f"      Phone: {house.owner.phone}")
    print(f"      Role: {house.owner.role}")

# Specific QR tekshirish
print("\n" + "=" * 80)
print("SPECIFIC QR TEKSHIRISH: 9907a30444a444f8")
print("=" * 80)

try:
    qr = QRCode.objects.select_related(
        "house__owner", "house__mahalla__district__region"
    ).get(uuid="9907a30444a444f8")

    print(f"\n✅ QR topildi!")
    print(f"QR ID: {qr.id}")
    print(f"UUID: {qr.uuid}")
    print(f"House ID: {qr.house.id}")
    print(f"Address: {qr.house.address}")
    print(f"Number: {qr.house.house_number}")
    print(f"Mahalla: {qr.house.mahalla.name}")
    print(f"Owner: {qr.house.owner}")

    if qr.house.owner:
        print(f"Owner details:")
        print(f"  - Name: {qr.house.owner.first_name} {qr.house.owner.last_name}")
        print(f"  - Phone: {qr.house.owner.phone}")
        print(f"  - Role: {qr.house.owner.role}")
        print(f"❌ BU UY CLAIMED BO'LISHI KERAK, LEKIN UNCLAIMED DEB CHIQDI!")
    else:
        print(f"✅ Owner yo'q - bu unclaimed")

except QRCode.DoesNotExist:
    print("❌ QR topilmadi!")

# QR kodlar statistikasi
print("\n" + "=" * 80)
print("QR KODLAR STATISTIKASI")
print("=" * 80)

total_qr = QRCode.objects.count()
print(f"\n📊 Jami QR kodlar: {total_qr}")

qr_with_owner = QRCode.objects.filter(house__owner__isnull=False).count()
print(f"✅ QR (egasi bor): {qr_with_owner}")

qr_without_owner = QRCode.objects.filter(house__owner__isnull=True).count()
print(f"❌ QR (egasi yo'q): {qr_without_owner}")

print("\n" + "=" * 80)
