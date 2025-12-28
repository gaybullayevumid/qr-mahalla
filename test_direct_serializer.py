import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from apps.qrcodes.serializers import QRCodeSerializer
from apps.qrcodes.models import QRCode

User = get_user_model()

print("🧪 Direct Serializer Test (without HTTP)\n")

# Create/get test admin user
admin, created = User.objects.get_or_create(
    phone="+998901111111",
    defaults={
        "role": "admin",
        "first_name": "Test",
        "last_name": "Admin",
    },
)
print(f"Admin user: {admin.phone} (role: {admin.role})")

# Get all QR codes
qr_codes = QRCode.objects.all()
print(f"\nTotal QR codes in DB: {qr_codes.count()}")

# Test serialization
print("\n" + "=" * 60)
print("Testing Serialization...")
print("=" * 60)

try:
    serializer = QRCodeSerializer(qr_codes, many=True)
    data = serializer.data
    print(f"✅ Successfully serialized {len(data)} QR codes\n")

    # Show first 3
    for i, qr in enumerate(data[:3]):
        print(f"QR #{i+1}:")
        print(f"  UUID: {qr['uuid']}")
        print(f"  is_claimed: {qr['is_claimed']}")
        print(f"  owner: {qr['owner']}")
        print(f"  qr_url: {qr['qr_url'][:60]}...")
        print()

except Exception as e:
    print(f"❌ Serialization failed: {str(e)}")
    import traceback

    traceback.print_exc()
