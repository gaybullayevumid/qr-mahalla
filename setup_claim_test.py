import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User
from apps.regions.models import Mahalla
from rest_framework_simplejwt.tokens import RefreshToken

# Create or get test user
phone = "+998901234567"
user, created = User.objects.get_or_create(
    phone=phone,
    defaults={
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
        "is_verified": True,
    },
)

if created:
    print(f"✅ Created user: {phone}")
else:
    print(f"✅ User exists: {phone}")

# Generate token
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

print(f"\n📝 Access Token:\n{access_token}\n")

# Check mahallas
mahallas = Mahalla.objects.all()[:3]
print("📍 Available Mahallas:")
for m in mahallas:
    print(f"  - ID: {m.id}, Name: {m.name}")

# Create claim test data
claim_data = {
    "first_name": "Umid",
    "last_name": "Gaybullayev",
    "address": "Test Street, 123",
    "house_number": "123A",
    "mahalla": mahallas[0].id if mahallas else 1,
}

print(f"\n📦 Claim Data:")
print(json.dumps(claim_data, indent=2))

# Save to file for curl
with open("test_claim_data.json", "w") as f:
    json.dump(claim_data, f, indent=2)

with open("test_token.txt", "w") as f:
    f.write(access_token)

print("\n✅ Token saved to: test_token.txt")
print("✅ Claim data saved to: test_claim_data.json")
print("\n🔧 To test claim, run:")
print(
    f'curl -X POST "http://192.168.0.126:8000/api/qrcodes/claim/65eb5437b84b4fc9/" -H "Authorization: Bearer {access_token[:30]}..." -H "Content-Type: application/json" -d @test_claim_data.json'
)
