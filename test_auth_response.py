import os
import django
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User, PhoneOTP

# Create test user
phone = "+998991234567"

# Delete existing
User.objects.filter(phone=phone).delete()
PhoneOTP.objects.filter(phone=phone).delete()

# Create OTP
otp = PhoneOTP.objects.create(phone=phone, code="123456")
print(f"✅ Created OTP: {otp.code} for {phone}")

# Test auth with code
import requests

url = "http://127.0.0.1:8000/api/users/auth/"
data = {"phone": phone, "code": "123456"}

print(f"\n📤 POST {url}")
print(f"Data: {data}")

response = requests.post(url, json=data)

print(f"\n📥 Response Status: {response.status_code}")
print(f"Response JSON:")
import json

print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Check user.id field
response_data = response.json()
if "user" in response_data:
    user_data = response_data["user"]
    print(f"\n🔍 User data keys: {list(user_data.keys())}")
    print(f"✅ user.id = {user_data.get('id')}")

    if user_data.get("id"):
        print(f"✅✅✅ ID MAVJUD!")
    else:
        print(f"❌❌❌ ID YO'Q!")
else:
    print("❌ 'user' key not in response")
