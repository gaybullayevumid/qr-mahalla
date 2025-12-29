import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House
from apps.regions.models import Mahalla
from apps.users.models import User

print("🔍 Checking database state before claim\n")

# Get unclaimed QR code
unclaimed_qr = QRCode.objects.filter(house__isnull=True).first()

if unclaimed_qr:
    print(f"✅ Found unclaimed QR code: {unclaimed_qr.uuid}")
    print(f"   House: {unclaimed_qr.house}")
else:
    print("❌ No unclaimed QR codes found")
    all_qr = QRCode.objects.all()
    print(f"\nTotal QR codes: {all_qr.count()}")
    for qr in all_qr[:3]:
        print(
            f"  {qr.uuid} - house: {qr.house}, owner: {qr.house.owner if qr.house else None}"
        )

# Check if we can create a house
print("\n" + "=" * 60)
print("Testing House creation")
print("=" * 60)

mahalla = Mahalla.objects.first()
user, _ = User.objects.get_or_create(
    phone="+998901234777",
    defaults={"role": "client", "first_name": "Test", "last_name": "User"},
)

print(f"\nMahalla: {mahalla.name} (ID: {mahalla.id})")
print(f"User: {user.phone}")

try:
    # Try to create a house
    house = House.objects.create(
        address="Test address",
        house_number="999",
        mahalla=mahalla,
        owner=user,
    )
    print(f"✅ House created successfully: ID {house.id}")

    # Try to link to QR code
    if unclaimed_qr:
        unclaimed_qr.house = house
        unclaimed_qr.save()
        print(f"✅ QR code linked to house: {unclaimed_qr.uuid}")

        # Clean up
        unclaimed_qr.house = None
        unclaimed_qr.save()
        house.delete()
        print("✅ Test cleanup successful")

except Exception as e:
    print(f"❌ Error creating house: {str(e)}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("Checking for existing houses that might conflict")
print("=" * 60)

existing_houses = House.objects.all()
print(f"\nTotal houses in DB: {existing_houses.count()}")

if existing_houses.exists():
    print("\nFirst 3 houses:")
    for h in existing_houses[:3]:
        print(f"  ID {h.id}: {h.address} - {h.house_number}")
        print(f"    Mahalla: {h.mahalla.name}")
        print(f"    Owner: {h.owner.phone if h.owner else 'None'}")
        # Check if linked to QR
        try:
            qr_code = h.qr_code
            print(f"    QR Code: {qr_code.uuid}")
        except:
            print(f"    QR Code: None")
