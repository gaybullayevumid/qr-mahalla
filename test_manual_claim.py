import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from apps.users.models import User
from apps.qrcodes.models import QRCode
from apps.houses.models import House
from apps.regions.models import Mahalla

print("🧪 Simulating ClaimHouseView logic manually\n")

# Create user
user, _ = User.objects.get_or_create(
    phone="+998901333444",
    defaults={"role": "client", "first_name": "", "last_name": ""},
)
print(f"User: {user.phone}")
print(f"Before: first_name='{user.first_name}', last_name='{user.last_name}'")

# Get unclaimed QR
qr = QRCode.objects.filter(house__isnull=True).first()
if not qr:
    print("❌ No unclaimed QR codes")
    exit(1)

print(f"\nQR: {qr.uuid} (ID: {qr.id})")
print(f"QR house: {qr.house}")
print(f"QR house_id: {qr.house_id}")

# Get mahalla
mahalla = Mahalla.objects.first()
print(f"\nMahalla: {mahalla.name} (ID: {mahalla.id})")

# Claim data
first_name = "Manual"
last_name = "Test"
address = "Manual test ko'chasi"
house_number = "777"

print("\n" + "=" * 60)
print("SIMULATING CLAIM PROCESS")
print("=" * 60)

try:
    with transaction.atomic():
        print("\n1. Locking QR code...")
        qr_locked = QRCode.objects.select_for_update().get(uuid=qr.uuid)
        print(f"   ✅ Locked: {qr_locked.uuid}")
        print(f"   house: {qr_locked.house}")
        print(f"   house_id: {qr_locked.house_id}")

        print("\n2. Updating user...")
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])
        print(f"   ✅ User updated: {user.first_name} {user.last_name}")

        print("\n3. Creating house...")
        house = House.objects.create(
            address=address,
            house_number=house_number,
            mahalla=mahalla,
            owner=user,
        )
        print(f"   ✅ House created: ID {house.id}")
        print(f"   Address: {house.address}")
        print(f"   Owner: {house.owner.phone}")

        print("\n4. Linking QR to house...")
        qr_locked.house = house
        print(f"   QR house set to: {qr_locked.house}")
        print(f"   QR house_id: {qr_locked.house_id}")

        print("\n5. Saving QR code...")
        qr_locked.save(update_fields=["house"])
        print(f"   ✅ QR saved")

    print("\n6. Transaction committed ✅")

    # Verify
    qr.refresh_from_db()
    print(f"\n✅ VERIFICATION:")
    print(f"  QR house: {qr.house}")
    if qr.house:
        print(f"  House ID: {qr.house.id}")
        print(f"  House owner: {qr.house.owner.phone}")
        print(f"  House address: {qr.house.address}")

    # Clean up for next test
    print(f"\n🧹 Cleaning up...")
    qr.house = None
    qr.save(update_fields=["house"])
    house.delete()
    user.first_name = ""
    user.last_name = ""
    user.save()
    print(f"   ✅ Cleaned")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
