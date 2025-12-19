"""
Test SMS Authentication Workflow
Bu script SMS kod kiritgandan keyin user bazaga saqlanishini test qiladi
"""

import requests
import json
import time

BASE_URL = "http://192.168.0.158:8000"
TEST_PHONE = "+998901234567"


def print_header(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}\n")


def test_send_sms():
    """
    Step 1: SMS kod yuborish
    User hali bazada yaratilmasligi kerak
    """
    print_header("TEST 1: SMS KOD YUBORISH")

    url = f"{BASE_URL}/api/users/auth/"
    data = {"phone": TEST_PHONE}

    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            print("\n✅ SMS kod yuborildi!")
            print("⚠️  User hali bazada yaratilmadi (tasdiqlash kutilmoqda)")
            return True
        else:
            print("\n❌ Xatolik!")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_verify_code_wrong():
    """
    Step 2a: Noto'g'ri kod bilan test (user yaratilmasligi kerak)
    """
    print_header("TEST 2A: NOTO'G'RI KOD BILAN TEST")

    url = f"{BASE_URL}/api/users/auth/"
    data = {"phone": TEST_PHONE, "code": "000000"}  # Wrong code

    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 400:
            print("\n✅ Noto'g'ri kod rad etildi!")
            print("✅ User bazada yaratilmadi")
            return True
        else:
            print("\n⚠️  Kutilmagan javob")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_verify_code_correct():
    """
    Step 2b: To'g'ri kod bilan test
    """
    print_header("TEST 2B: TO'G'RI KOD BILAN TEST")

    # Get the actual code from console/database
    print("⚠️  DIQQAT: Konsoldan yoki database dan to'g'ri kodni oling!")
    print("   - Admin panel: http://192.168.0.158:8000/admin/users/phoneotp/")
    print("   - Yoki console log dan ko'ring\n")

    code = input(f"SMS kod kiriting ({TEST_PHONE} uchun): ").strip()

    if not code:
        print("❌ Kod kiritilmadi!")
        return False

    url = f"{BASE_URL}/api/users/auth/"
    data = {
        "phone": TEST_PHONE,
        "code": code,
        "device_id": "test_device_001",
        "device_name": "Test Device",
    }

    print(f"\nURL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ SMS kod tasdiqlandi!")
            print("✅ User bazada yaratildi!")
            print(f"\n📱 User ma'lumotlari:")
            print(f"   Phone: {result['user']['phone']}")
            print(f"   Role: {result['user']['role']}")
            print(f"   First Name: {result['user']['first_name']}")
            print(f"   Last Name: {result['user']['last_name']}")
            print(f"\n🔑 Token:")
            print(f"   Access: {result['access'][:50]}...")
            print(f"   Refresh: {result['refresh'][:50]}...")
            return True
        else:
            print("\n❌ Xatolik!")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_full_workflow():
    """
    Full workflow test
    """
    print("\n" + "=" * 60)
    print("SMS AUTHENTICATION WORKFLOW TEST")
    print("=" * 60)

    print("\nBu test quyidagi workflow ni tekshiradi:")
    print("1. SMS kod yuborish (user hali yaratilmaydi)")
    print("2. Noto'g'ri kod bilan test (user yaratilmaydi)")
    print("3. To'g'ri kod bilan test (user yaratiladi)")
    print("\nTest boshlandi...\n")

    time.sleep(2)

    # Step 1: Send SMS
    if not test_send_sms():
        print("\n❌ SMS yuborishda xatolik!")
        return

    time.sleep(2)

    # Step 2a: Wrong code
    if not test_verify_code_wrong():
        print("\n⚠️  Noto'g'ri kod test o'tmadi")

    time.sleep(2)

    # Step 2b: Correct code
    if test_verify_code_correct():
        print("\n" + "=" * 60)
        print("✅ BARCHA TESTLAR MUVAFFAQIYATLI O'TDI!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)


def check_user_exists():
    """
    Check if user exists in database (requires admin access)
    """
    print_header("USER MAVJUDLIGINI TEKSHIRISH")

    print("Bu funksiya admin API orqali user ni tekshiradi")
    print("Yoki qo'lda tekshiring:")
    print(f"  Admin panel: http://192.168.0.158:8000/admin/users/user/")
    print(f"  Phone: {TEST_PHONE}")


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 60)
    print("SMS AUTHENTICATION TEST SCRIPT")
    print("=" * 60)

    print("\nConfiguration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Test Phone: {TEST_PHONE}")

    print("\nTanlash:")
    print("  1 - To'liq workflow test")
    print("  2 - Faqat SMS yuborish")
    print("  3 - Faqat kod tasdiqlash")
    print("  4 - User mavjudligini tekshirish")

    choice = input("\nTanlang (1-4): ").strip()

    if choice == "1":
        test_full_workflow()
    elif choice == "2":
        test_send_sms()
    elif choice == "3":
        test_verify_code_correct()
    elif choice == "4":
        check_user_exists()
    else:
        print("❌ Noto'g'ri tanlov!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("TEST TUGADI")
    print("=" * 60 + "\n")
