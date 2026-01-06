"""
Quick API endpoint check
"""

import requests

BASE_URL = "http://localhost:8000"


def check_endpoints():
    """Check if bulk endpoints are available"""

    endpoints = [
        "/api/qrcodes/bulk/generate/",
        "/api/qrcodes/bulk/list/",
    ]

    print("🔍 Checking API endpoints...")
    print("=" * 60)

    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            # Try OPTIONS request (doesn't require auth)
            response = requests.options(url)
            if response.status_code in [200, 405, 403, 401]:
                print(f"✅ {endpoint}")
                print(f"   Status: {response.status_code}")
                if "Allow" in response.headers:
                    print(f"   Allowed methods: {response.headers['Allow']}")
            else:
                print(f"❌ {endpoint}")
                print(f"   Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}")
            print(f"   Error: {str(e)}")
        print()


if __name__ == "__main__":
    check_endpoints()
