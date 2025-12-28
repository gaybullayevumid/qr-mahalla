"""
Test script for QR Code scanning and claiming workflow
Bu script regular user uchun QR code skanerlash va claim qilish workflow ni test qiladi
"""

import requests
import json

# Configuration
BASE_URL = "http://192.168.0.158:8000"
# Bu token regular client (role=client) uchun bo'lishi kerak
TOKEN = "YOUR_USER_TOKEN_HERE"  # Login qilib tokenni oling

headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def test_scan_qr_by_uuid(uuid):
    """
    Test QR code scanning by UUID
    GET /api/qrcodes/scan-uuid/{uuid}/
    """
    print(f"\n{'='*60}")
    print(f"TEST 1: QR Code Skanerlash (UUID: {uuid})")
    print(f"{'='*60}")

    url = f"{BASE_URL}/api/qrcodes/scan-uuid/{uuid}/"

    try:
        response = requests.get(url, headers=headers)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_claim_house(uuid):
    """
    Test house claiming
    POST /api/qrcodes/claim-uuid/{uuid}/
    """
    print(f"\n{'='*60}")
    print(f"TEST 2: House Claim qilish (UUID: {uuid})")
    print(f"{'='*60}")

    url = f"{BASE_URL}/api/qrcodes/claim-uuid/{uuid}/"

    claim_data = {
        "first_name": "Alisher",
        "last_name": "Navoiy",
        "passport_id": "AA1234567",
        "address": "Toshkent, Mirobod tumani, Buyuk Ipak Yo'li 123",
    }

    print(f"\nSending data:")
    print(json.dumps(claim_data, indent=2, ensure_ascii=False))

    try:
        response = requests.post(url, headers=headers, json=claim_data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_full_workflow(uuid):
    """
    Test full workflow: scan then claim
    """
    print("\n" + "=" * 60)
    print("FULL WORKFLOW TEST")
    print("=" * 60)

    # Step 1: Scan QR code
    scan_result = test_scan_qr_by_uuid(uuid)

    if not scan_result:
        print("\n❌ Scan failed!")
        return

    # Check if can claim
    if scan_result.get("status") == "unclaimed" and scan_result.get("can_claim"):
        print("\n✅ House unclaimed, can proceed with claiming")

        # Step 2: Claim house
        claim_result = test_claim_house(uuid)

        if claim_result and claim_result.get("status") == "success":
            print("\n✅ House claimed successfully!")
        else:
            print("\n❌ Claim failed!")

    elif scan_result.get("status") == "claimed":
        print("\n⚠️  House already claimed!")
        print(f"Owner: {scan_result.get('first_name')} {scan_result.get('last_name')}")
        print(f"Phone: {scan_result.get('phone')}")

    else:
        print("\n❌ Unknown status!")


def get_unclaimed_qrcodes():
    """
    Get list of unclaimed QR codes to test with
    """
    print(f"\n{'='*60}")
    print("Getting list of unclaimed QR codes...")
    print(f"{'='*60}")

    url = f"{BASE_URL}/api/qrcodes/"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            qrcodes = response.json()
            print(f"\nFound {len(qrcodes)} QR codes")

            unclaimed = [qr for qr in qrcodes if not qr.get("house", {}).get("owner")]
            print(f"Unclaimed: {len(unclaimed)}")

            if unclaimed:
                print("\nUnclaimed QR codes:")
                for qr in unclaimed[:5]:  # Show first 5
                    print(
                        f"  - UUID: {qr.get('uuid')} | House: {qr.get('house', {}).get('address')}"
                    )

                return unclaimed[0]["uuid"]  # Return first unclaimed UUID
            else:
                print("⚠️  No unclaimed QR codes found!")
                return None
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("QR CODE WORKFLOW TEST SCRIPT")
    print("=" * 60)

    # Test configuration
    print("\nConfiguration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Token: {TOKEN[:20]}..." if len(TOKEN) > 20 else f"  Token: {TOKEN}")

    if TOKEN == "YOUR_USER_TOKEN_HERE":
        print("\n❌ ERROR: Please set your token first!")
        print("   1. Login as regular user")
        print("   2. Copy token")
        print("   3. Replace TOKEN variable in this script")
        exit(1)

    # Get unclaimed QR code
    unclaimed_uuid = get_unclaimed_qrcodes()

    if unclaimed_uuid:
        # Test full workflow
        test_full_workflow(unclaimed_uuid)
    else:
        print("\n⚠️  No unclaimed QR codes to test with!")
        print("   Create house without owner first:")
        print("   1. Login as admin")
        print("   2. Create mahalla")
        print("   3. Create house (without owner)")
        print("   4. QR code will be created automatically")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
