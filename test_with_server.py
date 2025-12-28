"""
Simple test to call QR list API and see exact error
Run this AFTER starting the server with: python manage.py runserver
"""

import requests

base_url = "http://127.0.0.1:8000"

print("🧪 Testing QR Code List Endpoint\n")
print("=" * 60)

# Test 1: Without authentication
print("\n1️⃣ Test without auth:")
try:
    response = requests.get(f"{base_url}/api/qrcodes/")
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 2: Create user and login
print("\n2️⃣ Creating test user and logging in:")

# First, create OTP
phone = "+998901234599"
try:
    # Request OTP
    otp_response = requests.post(f"{base_url}/api/users/auth/", json={"phone": phone})
    print(f"   OTP request status: {otp_response.status_code}")

    if otp_response.status_code == 200:
        otp_data = otp_response.json()
        code = otp_data.get("code")  # In development, code is returned
        print(f"   OTP code: {code}")

        # Verify OTP
        verify_response = requests.post(
            f"{base_url}/api/users/auth/", json={"phone": phone, "code": code}
        )
        print(f"   Verify status: {verify_response.status_code}")

        if verify_response.status_code == 200:
            auth_data = verify_response.json()
            phone_header = auth_data.get("phone")
            print(f"   ✅ Logged in! Phone header: {phone_header}")

            # Test 3: Get QR codes with auth
            print("\n3️⃣ Getting QR codes with authentication:")
            headers = {"Authorization": f"Phone {phone_header}"}

            list_response = requests.get(f"{base_url}/api/qrcodes/", headers=headers)

            print(f"   Status: {list_response.status_code}")

            if list_response.status_code == 200:
                qr_codes = list_response.json()
                print(f"   ✅ Success! Found {len(qr_codes)} QR codes")

                if qr_codes:
                    print(f"\n   Sample QR code:")
                    qr = qr_codes[0]
                    for key, value in qr.items():
                        print(f"     {key}: {value}")
            else:
                print(f"   ❌ Error response:")
                print(f"   {list_response.text}")
        else:
            print(f"   ❌ Verify failed: {verify_response.text}")
    else:
        print(f"   ❌ OTP request failed: {otp_response.text}")

except requests.exceptions.ConnectionError:
    print("\n❌ Server is not running!")
    print("Start server with: python manage.py runserver")
except Exception as e:
    print(f"\n❌ Unexpected error: {str(e)}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
