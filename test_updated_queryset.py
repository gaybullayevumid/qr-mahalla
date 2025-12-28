import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.users.models import User
from django.db.models import Q

print("🧪 Testing UPDATED QRCodeDetailAPIView queryset logic\n")

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

# Test NEW client queryset (unclaimed + owned)
print("\n" + "=" * 60)
print("UPDATED Implementation (client sees unclaimed + owned)")
print("=" * 60)
queryset = QRCode.objects.select_related("house__owner", "house__mahalla")
client_queryset = queryset.filter(
    Q(house__isnull=True) | Q(house__owner__isnull=True) | Q(house__owner=client)
)
print(f"QR codes visible to client: {client_queryset.count()}")

# This should work now
print("\nTrying to get QR code by UUID...")
try:
    qr_found = client_queryset.get(uuid=qr.uuid)
    print(f"✅ Found: {qr_found.uuid}")
    print(f"   Client can now see unclaimed QR codes!")
except QRCode.DoesNotExist:
    print(f"❌ Still not found - something is wrong")

# Test all scenarios
print("\n" + "=" * 60)
print("Testing all QR code types")
print("=" * 60)

total = QRCode.objects.count()
unclaimed_no_house = QRCode.objects.filter(house__isnull=True).count()
unclaimed_no_owner = QRCode.objects.filter(
    house__isnull=False, house__owner__isnull=True
).count()
owned_by_client = QRCode.objects.filter(house__owner=client).count()

print(f"Total QR codes: {total}")
print(f"  No house: {unclaimed_no_house}")
print(f"  Has house but no owner: {unclaimed_no_owner}")
print(f"  Owned by client: {owned_by_client}")
print(f"\nClient can see: {client_queryset.count()}/{total}")
print(f"Expected: {unclaimed_no_house + unclaimed_no_owner + owned_by_client}")
