"""
Test POST requests to verify frontend integration
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_test(name, passed, details=""):
    """Print test result"""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} - {name}")
    if details:
        print(f"  {details}")
    print()


def test_auth_send_sms():
    """Test sending SMS code"""
    print(f"{YELLOW}Test 1: Send SMS Code{RESET}")

    url = f"{BASE_URL}/api/auth/"
    data = {"phone": "+998901234567"}

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        passed = response.status_code == 200 and "message" in response.json()
        print_test("Send SMS", passed, f"Status: {response.status_code}")
        return response.json().get("phone")
    except Exception as e:
        print_test("Send SMS", False, f"Error: {str(e)}")
        return None


def test_auth_verify_code(phone):
    """Test verifying SMS code"""
    print(f"{YELLOW}Test 2: Verify SMS Code{RESET}")

    url = f"{BASE_URL}/api/auth/"
    # Get the latest code from database
    data = {
        "phone": phone,
        "code": "123456",  # Default code for testing
        "device_id": "test-device-001",
        "device_name": "Test Device",
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        passed = response.status_code == 200 and "access" in response.json()
        print_test("Verify Code", passed, f"Status: {response.status_code}")
        return response.json().get("access")
    except Exception as e:
        print_test("Verify Code", False, f"Error: {str(e)}")
        return None


def test_create_region(token):
    """Test creating a region"""
    print(f"{YELLOW}Test 3: Create Region{RESET}")

    url = f"{BASE_URL}/api/regions/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"name": "Test Region POST"}

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        passed = response.status_code in [200, 201]
        print_test("Create Region", passed, f"Status: {response.status_code}")
        return response.json().get("id") if passed else None
    except Exception as e:
        print_test("Create Region", False, f"Error: {str(e)}")
        return None


def test_create_district(token, region_id):
    """Test creating a district"""
    print(f"{YELLOW}Test 4: Create District{RESET}")

    url = f"{BASE_URL}/api/districts/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"name": "Test District POST", "region": region_id}

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        passed = response.status_code in [200, 201]
        print_test("Create District", passed, f"Status: {response.status_code}")
        return response.json().get("id") if passed else None
    except Exception as e:
        print_test("Create District", False, f"Error: {str(e)}")
        return None


def test_create_mahalla(token, district_id):
    """Test creating a mahalla"""
    print(f"{YELLOW}Test 5: Create Mahalla{RESET}")

    url = f"{BASE_URL}/api/mahallas/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"name": "Test Mahalla POST", "district": district_id}

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        passed = response.status_code in [200, 201]
        print_test("Create Mahalla", passed, f"Status: {response.status_code}")
        return response.json().get("id") if passed else None
    except Exception as e:
        print_test("Create Mahalla", False, f"Error: {str(e)}")
        return None


def test_create_house(token, mahalla_id):
    """Test creating a house"""
    print(f"{YELLOW}Test 6: Create House{RESET}")

    url = f"{BASE_URL}/api/houses/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "mahalla": mahalla_id,
        "house_number": "999",
        "address": "Test Address POST",
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        passed = response.status_code in [200, 201]
        print_test("Create House", passed, f"Status: {response.status_code}")
        return response.json().get("id") if passed else None
    except Exception as e:
        print_test("Create House", False, f"Error: {str(e)}")
        return None


def test_create_user(token):
    """Test creating a user with houses"""
    print(f"{YELLOW}Test 7: Create User with Houses{RESET}")

    url = f"{BASE_URL}/api/users/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "phone": "+998901234999",
        "first_name": "Test",
        "last_name": "User",
        "role": "client",
        "houses": [],
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        passed = response.status_code in [200, 201]
        print_test("Create User", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Create User", False, f"Error: {str(e)}")


def main():
    """Run all tests"""
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}POST Request Tests - Frontend Integration{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}\n")

    # Step 1: Send SMS
    phone = test_auth_send_sms()
    if not phone:
        print(f"{RED}Cannot continue without phone number{RESET}")
        return

    # Step 2: Verify code
    token = test_auth_verify_code(phone)
    if not token:
        print(f"{RED}Cannot continue without authentication token{RESET}")
        return

    print(f"{GREEN}✓ Authentication successful!{RESET}\n")

    # Step 3: Create region
    region_id = test_create_region(token)
    if not region_id:
        print(
            f"{YELLOW}Warning: Could not create region (may require admin role){RESET}\n"
        )

    # Step 4: Create district (if region created)
    district_id = None
    if region_id:
        district_id = test_create_district(token, region_id)

    # Step 5: Create mahalla (if district created)
    mahalla_id = None
    if district_id:
        mahalla_id = test_create_mahalla(token, district_id)

    # Step 6: Create house (if mahalla created)
    if mahalla_id:
        test_create_house(token, mahalla_id)

    # Step 7: Create user
    test_create_user(token)

    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}Tests Complete!{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}\n")


if __name__ == "__main__":
    main()
