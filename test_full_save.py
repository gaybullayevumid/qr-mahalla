import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from apps.users.models import User
from apps.qrcodes.models import QRCode
from apps.houses.models import House
from apps.regions.models import Mahalla

print("🧪 Testing with full save() (no update_fields)\n")

# Create user
user, _ = User.objects.get_or_create(
    phone="+998901444555",
    defaults={"role": "client", "first_name": "", "last_name": ""},
)
print(f"User: {user.phone}")

# Get unclaimed QR
qr = QRCode.objects.filter(house__isnull=True).first()
if not qr:
    print("❌ No unclaimed QR codes")
    exit(1)

print(f"QR: {qr.uuid}")

# Get mahalla
mahalla = Mahalla.objects.first()
print(f"Mahalla: {mahalla.name}\n")

print("=" * 60)
print("CLAIM PROCESS")
print("=" * 60)

try:
    with transaction.atomic():
        # Lock QR
        qr_locked = QRCode.objects.select_for_update().get(uuid=qr.uuid)

        # Update user
        user.first_name = "Full"
        user.last_name = "Save"
        user.save(update_fields=["first_name", "last_name"])
        print("✅ User updated")

        # Create house
        house = House.objects.create(
            address="Full save test",
            house_number="888",
            mahalla=mahalla,
            owner=user,
        )
        print(f"✅ House created: ID {house.id}")

        # Link and save WITHOUT update_fields
        qr_locked.house = house
        print(f"   Linking QR to house...")
        qr_locked.save()  # Full save
        print(f"✅ QR saved successfully!")

    print("\n✅ TRANSACTION COMMITTED!")

    # Verify
    qr.refresh_from_db()
    print(f"\n✅ Verification:")
    print(f"  QR house: {qr.house}")
    if qr.house:
        print(f"  House ID: {qr.house.id}")
        print(f"  Owner: {qr.house.owner.phone}")

    print(f"\n✅ SUCCESS! Claim completed without errors.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
