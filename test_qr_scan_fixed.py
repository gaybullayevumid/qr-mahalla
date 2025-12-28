"""
Test QR code scanning with Telegram URL format
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.qrcodes.models import QRCode
import requests

# Get a QR code
qr = QRCode.objects.first()

if qr:
    print("=" * 70)
    print("QR CODE SCAN TEST")
    print("=" * 70)
    
    print(f"\nQR Code Info:")
    print(f"  ID: {qr.id}")
    print(f"  UUID: {qr.uuid}")
    print(f"  Telegram URL: {qr.get_qr_url()}")
    
    print(f"\nHouse Info:")
    print(f"  Address: {qr.house.address}")
    print(f"  Mahalla: {qr.house.mahalla.name}")
    print(f"  Owner: {qr.house.owner if qr.house.owner else 'Unclaimed'}")
    
    print("\n" + "=" * 70)
    print("TEST 1: Scan with direct UUID")
    print("=" * 70)
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/qrcodes/scan/",
            json={"uuid": qr.uuid},
            timeout=5
        )
    except Exception as e:
        print(f"ERROR Connection error: {e}")
        print("⚠️  Make sure server is running: python manage.py runserver")
        exit(1)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Full response: {data}")
        print(f"Status: {data.get('status')}")
        print(f"Message: {data.get('message')}")
        if 'qr' in data:
            print(f"QR UUID: {data['qr'].get('uuid')}")
            print(f"QR URL: {data['qr'].get('qr_url')}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "=" * 70)
    print("TEST 2: Scan with Telegram URL (phone camera)")
    print("=" * 70)
    
    telegram_url = qr.get_qr_url()
    response = requests.post(
        "http://127.0.0.1:8000/api/qrcodes/scan/",
        json={"uuid": telegram_url}
    )
    
    print(f"Input: {telegram_url}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"OK Response:")
        print(f"  Status: {data.get('status')}")
        if 'qr' in data:
            print(f"  QR UUID: {data['qr'].get('uuid')}")
            print(f"  QR URL: {data['qr'].get('qr_url')}")
    else:
        print(f"ERROR Error: {response.text}")
    
    print("\n" + "=" * 70)
    print("TEST 3: Scan with 'qr_code' parameter")
    print("=" * 70)
    
    response = requests.post(
        "http://127.0.0.1:8000/api/qrcodes/scan/",
        json={"qr_code": telegram_url}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"OK Success!")
        if 'qr' in data:
            print(f"  QR URL: {data['qr'].get('qr_url')}")
    else:
        print(f"ERROR Error: {response.text}")
        
    print("\n" + "=" * 70)
    print("TEST 4: Scan with 'url' parameter")
    print("=" * 70)
    
    response = requests.post(
        "http://127.0.0.1:8000/api/qrcodes/scan/",
        json={"url": telegram_url}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"OK Success!")
        if 'qr' in data:
            print(f"  QR URL: {data['qr'].get('qr_url')}")
    else:
        print(f"ERROR Error: {response.text}")
    
else:
    print("ERROR No QR codes found in database")
