import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.houses.models import House
from apps.qrcodes.models import QRCode

# Check all houses
houses = House.objects.all()
print(f"Total houses: {houses.count()}")

for h in houses:
    try:
        qr = h.qr_code
        print(f"House {h.id}: {h.address[:30]} -> QR {qr.uuid}")
    except QRCode.DoesNotExist:
        print(f"House {h.id}: {h.address[:30]} -> NO QR (orphaned)")
        print(f"  Deleting...")
        h.delete()
        print(f"  Deleted!")

print("\nDone!")
