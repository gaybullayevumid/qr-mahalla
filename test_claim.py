import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
from apps.houses.models import House
from apps.regions.models import Mahalla
from apps.users.models import User

# Create test user
user, _ = User.objects.get_or_create(
    phone="+998901234567", defaults={"first_name": "Test", "last_name": "User"}
)

# Get QR code
qr = QRCode.objects.first()
if not qr:
    print("❌ No QR codes found!")
    exit(1)
print(f"QR: {qr.uuid}, has_house: {qr.house is not None}")

# Get mahalla
mahalla = Mahalla.objects.first()
print(f"Mahalla: {mahalla.id if mahalla else 'None'}")

if mahalla:
    # Try to create house
    max_house_id = (
        House.objects.aggregate(max_id=django.db.models.Max("id"))["max_id"] or 0
    )
    max_qr_house_id = (
        QRCode.objects.filter(house_id__isnull=False).aggregate(
            max_id=django.db.models.Max("house_id")
        )["max_id"]
        or 0
    )

    next_id = max(max_house_id, max_qr_house_id) + 1

    print(f"Max House ID: {max_house_id}")
    print(f"Max QR house_id: {max_qr_house_id}")
    print(f"Next ID: {next_id}")

    # Create house
    house = House(
        id=next_id,
        address="Test address",
        house_number="123",
        mahalla=mahalla,
        owner=user,
    )
    house.save(force_insert=True)
    print(f"Created house: {house.id}")

    # Link to QR
    qr.house = house
    qr.save()
    print(f"Linked QR to house: {qr.house.id}")

    print("\nSuccess!")
else:
    print("No mahalla found!")
