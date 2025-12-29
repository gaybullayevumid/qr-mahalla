import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House

print("=== QR Code 65eb5437b84b4fc9 ===")
try:
    qr = QRCode.objects.get(uuid="65eb5437b84b4fc9")
    print(f"QR ID: {qr.id}")
    print(f"QR UUID: {qr.uuid}")
    print(f"QR House: {qr.house}")
    print(f"QR House ID: {qr.house_id}")

    if qr.house:
        print(f"\nHouse Details:")
        print(f"  - ID: {qr.house.id}")
        print(f"  - Address: {qr.house.address}")
        print(f"  - Owner: {qr.house.owner}")
        print(f"  - Mahalla: {qr.house.mahalla}")
except QRCode.DoesNotExist:
    print("QR not found!")

print("\n=== All QR Codes with Houses ===")
for qr in QRCode.objects.filter(house__isnull=False):
    print(f"QR {qr.uuid} -> House {qr.house_id} (Owner: {qr.house.owner})")

print("\n=== All Houses ===")
for h in House.objects.all()[:5]:
    try:
        qr = h.qr_code
        qr_info = f"QR: {qr.uuid}"
    except:
        qr_info = "No QR"
    print(f"House {h.id}: {h.address} | Owner: {h.owner} | {qr_info}")
