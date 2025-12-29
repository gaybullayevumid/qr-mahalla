import requests
import json

# Test with local server
BASE_URL = "http://192.168.0.126:8000"

# First, authenticate
auth_data = {
    "phone": "+998901112233",  # Use created user phone
}

# Send SMS
response = requests.post(f"{BASE_URL}/api/users/auth/", json=auth_data)
print("SMS sent:", response.status_code, response.json())

# Enter code manually (check terminal/telegram for code)
code = input("Enter SMS code: ")

# Authenticate with code
auth_data["code"] = code
response = requests.post(f"{BASE_URL}/api/users/auth/", json=auth_data)
print("\nAuth response:", response.status_code)
auth_result = response.json()
print(json.dumps(auth_result, indent=2))

if response.status_code != 200:
    print("Authentication failed!")
    exit()

# Get token
token = auth_result.get("access")
print(f"\nToken: {token[:20]}...")

# Headers with token
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Try to claim a QR code
qr_uuid = "65eb5437b84b4fc9"

# First scan it
scan_response = requests.get(f"{BASE_URL}/api/qrcodes/scan/{qr_uuid}/", headers=headers)
print(f"\nScan response ({scan_response.status_code}):")
print(json.dumps(scan_response.json(), indent=2))

# Now claim it
claim_data = {
    "first_name": "Test",
    "last_name": "User",
    "address": "123 Main Street",
    "house_number": "123",
    "mahalla": 1,  # Make sure this mahalla exists
}

print(f"\nClaiming with data:")
print(json.dumps(claim_data, indent=2))

claim_response = requests.post(
    f"{BASE_URL}/api/qrcodes/claim/{qr_uuid}/", headers=headers, json=claim_data
)

print(f"\nClaim response ({claim_response.status_code}):")
print(claim_response.text[:500])

if claim_response.status_code == 200:
    print("\n✅ Claim successful!")
    print(json.dumps(claim_response.json(), indent=2))
else:
    print(f"\n❌ Claim failed: {claim_response.status_code}")
