import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode

qr_uuid = "df9dd4def795439b"

qr = QRCode.objects.get(uuid=qr_uuid)

print(f"QR UUID: {qr.uuid}")
print(f"QR ID: {qr.id}")
print(f"QR house: {qr.house}")
print(f"QR house_id: {qr.house_id}")
print(f"QR image: {qr.image}")

if qr.house:
    print(f"\nHouse details:")
    print(f"  ID: {qr.house.id}")
    print(f"  Address: {qr.house.address}")
    print(f"  Owner: {qr.house.owner}")

    # Check reverse
    try:
        reverse_qr = qr.house.qr_code
        print(f"  Reverse QR: {reverse_qr.uuid}")
    except:
        print(f"  Reverse QR: Error or None")

# Check all QR codes with this house_id
if qr.house_id:
    all_qr_with_house = QRCode.objects.filter(house_id=qr.house_id)
    print(f"\nAll QR codes with house_id={qr.house_id}:")
    for q in all_qr_with_house:
        print(f"  - {q.uuid} (ID: {q.id})")
