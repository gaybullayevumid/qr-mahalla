import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory, TestCase
from apps.users.models import User
from apps.qrcodes.models import QRCode
from apps.qrcodes.views import ClaimHouseView
from apps.regions.models import Mahalla
import json

print("🧪 Testing ClaimHouseView directly (no HTTP server needed)\n")

# Setup
factory = RequestFactory()

# Create user
user, _ = User.objects.get_or_create(
    phone="+998901222333",
    defaults={"role": "client", "first_name": "", "last_name": ""},
)
print(f"User: {user.phone}")

# Get unclaimed QR
qr = QRCode.objects.filter(house__isnull=True).first()
if not qr:
    print("❌ No unclaimed QR codes")
    exit(1)

print(f"QR: {qr.uuid}")
print(f"QR house: {qr.house}\n")

# Get mahalla
mahalla = Mahalla.objects.first()
print(f"Mahalla: {mahalla.name} (ID: {mahalla.id})\n")

# Claim data
claim_data = {
    "first_name": "Direct",
    "last_name": "Test",
    "address": "Direct test address",
    "house_number": "999",
    "mahalla": mahalla.id,
}

print("=" * 60)
print("CALLING ClaimHouseView.post() DIRECTLY")
print("=" * 60)

# Create request
request = factory.post(
    f"/api/qrcodes/claim/{qr.uuid}/",
    data=json.dumps(claim_data),
    content_type="application/json",
)
request.user = user

# Call view
view = ClaimHouseView.as_view()

try:
    response = view(request, uuid=qr.uuid)

    print(f"\n📡 Status: {response.status_code}\n")

    if response.status_code == 200:
        print("✅ SUCCESS!")
        print(f"\nResponse data:")
        print(response.data)

        # Verify
        qr.refresh_from_db()
        user.refresh_from_db()

        print(f"\n✅ Verification:")
        print(f"  User: {user.first_name} {user.last_name}")
        print(f"  QR house: {qr.house}")
        if qr.house:
            print(f"  House owner: {qr.house.owner.phone}")

    else:
        print(f"❌ Error (Status {response.status_code})")
        if hasattr(response, "data"):
            print(f"\nResponse: {response.data}")
        else:
            print(f"\nResponse: {response}")

except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback

    traceback.print_exc()

    # Check if IntegrityError
    if "IntegrityError" in str(e):
        print("\n⚠️  IntegrityError details:")
        print(f"  {e}")

print("\n" + "=" * 60)
