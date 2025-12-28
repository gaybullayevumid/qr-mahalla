import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User, PhoneOTP

# Create test user
phone = "+998991112233"
try:
    user = User.objects.get(phone=phone)
except User.DoesNotExist:
    user = User.objects.create(
        phone=phone,
        first_name="Auth",
        last_name="Test",
        role="client",
        is_verified=False,
    )

# Create OTP code
PhoneOTP.objects.filter(phone=phone).update(is_used=True)
otp = PhoneOTP.objects.create(phone=phone, code="123456", is_used=False)

print(f"Created OTP: {otp.code} for {phone}")

# Now test auth endpoint
from rest_framework.test import APIClient

client = APIClient()

print("\n" + "=" * 70)
print("🧪 TESTING AUTH ENDPOINT")
print("=" * 70)

# Step 1: Request SMS
print("\n1️⃣ POST /api/users/auth/ (request SMS)")
response = client.post("/api/users/auth/", {"phone": phone}, format="json")
print(f"Status: {response.status_code}")
print(f"Response: {response.data}")

# Step 2: Verify with code (use the new code from response)
print("\n2️⃣ POST /api/users/auth/ (verify with code)")

# Get the latest code
latest_otp = (
    PhoneOTP.objects.filter(phone=phone, is_used=False).order_by("-created_at").first()
)
print(f"Using code: {latest_otp.code if latest_otp else 'No code found'}")

response = client.post(
    "/api/users/auth/",
    {
        "phone": phone,
        "code": latest_otp.code if latest_otp else "000000",
        "device_id": "test-device",
        "device_name": "Test Device",
    },
    format="json",
)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    import json

    print("Response:")
    print(json.dumps(response.data, indent=2, ensure_ascii=False))

    if "user" in response.data and "id" in response.data["user"]:
        print(f"\n✅ User ID exists in auth response: {response.data['user']['id']}")
    else:
        print(f"\n❌ User ID NOT FOUND in auth response!")
        print(f"User keys: {list(response.data.get('user', {}).keys())}")
else:
    print(f"Error: {response.data}")

print("\n" + "=" * 70)
