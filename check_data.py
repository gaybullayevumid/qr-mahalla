import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.regions.models import Mahalla
from apps.users.models import User

print("=== QR Codes ===")
for qr in QRCode.objects.all()[:5]:
    print(
        f"UUID: {qr.uuid}, House: {qr.house_id}, Has Owner: {qr.house.owner if qr.house else None}"
    )

print("\n=== Mahallas ===")
for m in Mahalla.objects.all()[:3]:
    print(f"ID: {m.id}, Name: {m.name}")

print("\n=== Users ===")
for u in User.objects.all()[:3]:
    print(f"ID: {u.id}, Phone: {u.phone}, Role: {u.role}")

# Check for the specific QR code from error
try:
    qr = QRCode.objects.get(uuid="65eb5437b84b4fc9")
    print(f"\n=== QR {qr.uuid} ===")
    print(f"ID: {qr.id}")
    print(f"House: {qr.house}")
    if qr.house:
        print(f"House ID: {qr.house.id}")
        print(f"Owner: {qr.house.owner}")
        print(f"Mahalla: {qr.house.mahalla}")
except QRCode.DoesNotExist:
    print("\nQR code 65eb5437b84b4fc9 NOT FOUND")
