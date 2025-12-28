import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from rest_framework.authtoken.models import Token
from apps.users.models import User
from apps.qrcodes.views import QRCodeListAPIView

print("🧪 Testing QRCodeListAPIView directly...\n")

# Create test admin
admin, _ = User.objects.get_or_create(
    phone="+998901111111",
    defaults={
        "role": "admin",
        "first_name": "Test",
        "last_name": "Admin",
    },
)

# Create token
token, _ = Token.objects.get_or_create(user=admin)
print(f"Admin: {admin.phone} (role: {admin.role})")
print(f"Token: {token.key}\n")

# Create request
factory = RequestFactory()
request = factory.get("/api/qrcodes/")
request.user = admin

# Test view
view = QRCodeListAPIView.as_view()

try:
    print("Calling view...")
    response = view(request)
    print(f"✅ Response status: {response.status_code}")

    if hasattr(response, "data"):
        print(f"   Data type: {type(response.data)}")
        print(
            f"   Data length: {len(response.data) if isinstance(response.data, list) else 'N/A'}"
        )

        if isinstance(response.data, list) and response.data:
            print(f"\n   First item:")
            for key, value in response.data[0].items():
                print(f"     {key}: {value}")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback

    traceback.print_exc()
