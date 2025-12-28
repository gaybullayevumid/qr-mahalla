import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.qrcodes.serializers import QRCodeSerializer

print("🧪 Testing QRCodeSerializer with empty houses...\n")

# Get QR codes
qr_codes = QRCode.objects.all()[:3]

for qr in qr_codes:
    print(f"\nQR UUID: {qr.uuid}")
    print(f"  Has house: {qr.house is not None}")
    if qr.house:
        print(f"  Has owner: {qr.house.owner is not None}")

    try:
        serializer = QRCodeSerializer(qr)
        data = serializer.data
        print(f"  ✅ Serialized successfully")
        print(f"     is_claimed: {data['is_claimed']}")
        print(f"     owner: {data['owner']}")
        print(f"     qr_url: {data['qr_url']}")
    except Exception as e:
        print(f"  ❌ Serialization error: {str(e)}")

print("\n\n🧪 Testing queryset serialization...")
try:
    serializer = QRCodeSerializer(qr_codes, many=True)
    data = serializer.data
    print(f"✅ Serialized {len(data)} QR codes successfully")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback

    traceback.print_exc()
