import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
from apps.users.models import User

print("🧪 Testing QR Code List API with different roles...\n")

# Create test users if needed
test_users = {
    "admin": {"phone": "+998901234567", "role": "admin"},
    "client": {"phone": "+998901234568", "role": "client"},
}

base_url = "http://127.0.0.1:8000"

for role, user_data in test_users.items():
    print(f"\n{'='*60}")
    print(f"Testing as {role.upper()}")
    print("=" * 60)

    # Check if user exists, create if not
    user, created = User.objects.get_or_create(
        phone=user_data["phone"],
        defaults={
            "role": user_data["role"],
            "first_name": f"Test",
            "last_name": role.capitalize(),
        },
    )
    if created:
        print(f"✅ Created test user: {user.phone}")

    # Login via SMS (simplified - just get or create session)
    from apps.users.models import SMSSession

    session, _ = SMSSession.objects.get_or_create(
        phone=user.phone, defaults={"code": "1234", "is_verified": True}
    )
    session.is_verified = True
    session.save()

    # Login endpoint
    try:
        login_response = requests.post(
            f"{base_url}/api/users/sms-verify/",
            json={"phone": user.phone, "code": "1234"},
        )

        if login_response.status_code == 200:
            auth_data = login_response.json()
            auth_token = auth_data.get("auth_token")
            print(f"✅ Logged in successfully")

            # Get QR codes list
            headers = {"Authorization": f"Token {auth_token}"}
            list_response = requests.get(f"{base_url}/api/qrcodes/", headers=headers)

            print(f"\n📡 QR Codes List Response:")
            print(f"  Status: {list_response.status_code}")

            if list_response.status_code == 200:
                qr_codes = list_response.json()
                print(f"  ✅ Success! Found {len(qr_codes)} QR codes")

                if qr_codes:
                    print(f"\n  First QR code:")
                    qr = qr_codes[0]
                    print(f"    UUID: {qr.get('uuid')}")
                    print(f"    is_claimed: {qr.get('is_claimed')}")
                    print(f"    owner: {qr.get('owner')}")
                    print(f"    qr_url: {qr.get('qr_url')}")
            else:
                print(f"  ❌ Error: {list_response.status_code}")
                print(f"  Response: {list_response.text}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Server is not running!")
        print("Start with: python manage.py runserver")
        break
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()

print("\n" + "=" * 60)
