import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.houses.models import House
from apps.qrcodes.models import QRCode

# Get user
user = User.objects.get(phone="+998901234567")
print(f"User: {user.phone} ({user.first_name} {user.last_name})")
print(f"User ID: {user.id}")

# Check user's houses
houses = House.objects.filter(owner=user)
print(f"\n=== User's Houses ({houses.count()}) ===")
for h in houses:
    try:
        qr = h.qr_code
        qr_info = f"QR: {qr.uuid}"
    except:
        qr_info = "No QR attached"
    print(f"House {h.id}: {h.address} | {qr_info}")

# Check if there's an orphaned house
orphaned = House.objects.filter(qr_code__isnull=True)
print(f"\n=== Orphaned Houses (no QR) ({orphaned.count()}) ===")
for h in orphaned[:5]:
    print(f"House {h.id}: {h.address} | Owner: {h.owner}")

# Let's try to clean up and test again
print("\n=== Cleanup ===")
if houses.exists():
    print(f"Deleting {houses.count()} houses owned by user...")
    houses.delete()
    print("✅ Deleted")
else:
    print("No houses to delete")
