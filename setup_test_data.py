import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.regions.models import Region, District, Mahalla
from apps.qrcodes.models import QRCode
from apps.users.models import User

print("🔧 Setting up test data\n")

# Create Region
region, _ = Region.objects.get_or_create(id=1, defaults={"name": "Toshkent"})
print(f"✅ Region: {region.name}")

# Create District
district, _ = District.objects.get_or_create(
    id=1, defaults={"name": "Chilonzor", "region": region}
)
print(f"✅ District: {district.name}")

# Create Mahalla
mahalla, _ = Mahalla.objects.get_or_create(
    id=1, defaults={"name": "Qatortol", "district": district}
)
print(f"✅ Mahalla: {mahalla.name}")

# Create test user
user, _ = User.objects.get_or_create(
    phone="+998901234567",
    defaults={"role": "client", "first_name": "Test", "last_name": "User"},
)
print(f"✅ User: {user.phone}")

# Create 5 empty QR codes
print(f"\n🔲 Creating QR codes...")
for i in range(5):
    qr = QRCode.objects.create()
    qr.generate_qr_image()  # Generate image manually
    qr.save()
    print(f"  ✅ QR {i+1}: {qr.uuid}")

print(f"\n✅ Setup complete!")
print(f"Total QR codes: {QRCode.objects.count()}")
