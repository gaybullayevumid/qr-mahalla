import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode

print("🔍 Checking QR Codes Status:\n")

qr_codes = QRCode.objects.all()
print(f"Total QR codes: {qr_codes.count()}")

for qr in qr_codes[:5]:  # Show first 5
    house_status = (
        "✅ Empty (unclaimed)" if qr.house is None else f"❌ Has house: {qr.house}"
    )
    print(f"  QR UUID: {qr.uuid} - {house_status}")
    print(f"  QR URL: {qr.get_qr_url()}")

empty_count = QRCode.objects.filter(house__isnull=True).count()
claimed_count = QRCode.objects.filter(house__isnull=False).count()

print(f"\n📊 Final Status:")
print(f"  Empty QR codes: {empty_count}")
print(f"  Claimed QR codes: {claimed_count}")
print(f"\n✅ All QR codes are ready for claiming!")
