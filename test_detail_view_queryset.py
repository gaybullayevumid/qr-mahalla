import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.users.models import User
from django.db.models import Q

print("🧪 Testing QRCodeDetailAPIView queryset logic\n")

# Get or create test client
client, _ = User.objects.get_or_create(
    phone="+998901234999",
    defaults={
        "role": "client",
        "first_name": "Test",
        "last_name": "Client",
    },
)
print(f"Client user: {client.phone} (role: {client.role})")

# Get a QR code
qr = QRCode.objects.first()
if not qr:
    print("❌ No QR codes found")
    exit(1)

print(f"\nTesting with QR: {qr.uuid}")
print(f"  Has house: {qr.house is not None}")
if qr.house:
    print(f"  Has owner: {qr.house.owner is not None}")

# Test client queryset (current implementation)
print("\n" + "=" * 60)
print("Current Implementation (client sees only owned houses)")
print("=" * 60)
queryset = QRCode.objects.select_related("house__owner", "house__mahalla")
client_queryset = queryset.filter(house__owner=client)
print(f"QR codes visible to client: {client_queryset.count()}")

# This will fail if QR code has no house
print("\nTrying to get QR code by UUID...")
try:
    qr_found = client_queryset.get(uuid=qr.uuid)
    print(f"✅ Found: {qr_found.uuid}")
except QRCode.DoesNotExist:
    print(f"❌ Not found - Client can't see this QR code")
    print(f"   Reason: QR code has no house or client is not the owner")

# Admin can see all
print("\n" + "=" * 60)
print("Admin can see all QR codes")
print("=" * 60)
admin, _ = User.objects.get_or_create(
    phone="+998901111111",
    defaults={"role": "admin", "first_name": "Admin", "last_name": "User"},
)
admin_queryset = queryset
print(f"QR codes visible to admin: {admin_queryset.count()}")
try:
    qr_found = admin_queryset.get(uuid=qr.uuid)
    print(f"✅ Found: {qr_found.uuid}")
except QRCode.DoesNotExist:
    print(f"❌ Not found")
