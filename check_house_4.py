import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House

house_id = 4

print(f"🔍 Checking if House ID {house_id} is already linked\n")

# Check if house exists
try:
    house = House.objects.get(id=house_id)
    print(f"✅ House exists:")
    print(f"   ID: {house.id}")
    print(f"   Address: {house.address}")
    print(f"   Owner: {house.owner.phone if house.owner else 'None'}")
except House.DoesNotExist:
    print(f"❌ House ID {house_id} does not exist")
    exit(0)

# Check QR codes with this house
qr_codes = QRCode.objects.filter(house_id=house_id)
print(f"\n📊 QR codes linked to this house: {qr_codes.count()}")

for qr in qr_codes:
    print(f"   - QR {qr.uuid} (ID: {qr.id})")
    print(f"     house_id: {qr.house_id}")

# Check reverse relation
try:
    qr_reverse = house.qr_code
    print(f"\n🔄 Reverse relation (house.qr_code):")
    print(f"   UUID: {qr_reverse.uuid} (ID: {qr_reverse.id})")
except QRCode.DoesNotExist:
    print(f"\n⚠️  No reverse relation found (but filter found {qr_codes.count()})")
except Exception as e:
    print(f"\n❌ Reverse relation error: {e}")
