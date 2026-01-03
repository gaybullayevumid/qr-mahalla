#!/usr/bin/env python
"""Test QR code scanning and is_scanned field."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from apps.qrcodes.views import ScanQRCodeView
from apps.qrcodes.models import QRCode
from apps.scans.models import ScanLog
from apps.users.models import User
import json

print("=" * 80)
print("=== TEST: QR Code Scanning ===")
print("=" * 80)

# Get a QR code
qr = QRCode.objects.first()
if not qr:
    print("❌ No QR codes found!")
    exit(1)

print(f"\n✅ QR Code: {qr.uuid}")
print(f"   Is Scanned: {qr.is_scanned}")
print(f"   House: {qr.house}")

# Get or create a test user
user, created = User.objects.get_or_create(
    phone="+998909999999",
    defaults={
        "first_name": "Test",
        "last_name": "Scanner",
        "role": "client",
        "is_verified": True,
    },
)

print(f"\n✅ User: {user.phone} - {user.first_name} {user.last_name}")

# Scan QR code
factory = RequestFactory()
viewset = ScanQRCodeView.as_view()

request = factory.get(f"/api/qrcodes/scan/{qr.uuid}/")
request.user = user
response = viewset(request, uuid=qr.uuid)

print(f"\n✅ Scan Status: {response.status_code}")
print("\nResponse:")
print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Check if QR is marked as scanned
qr.refresh_from_db()
print(f"\n✅ After Scan - Is Scanned: {qr.is_scanned}")

# Check scan logs
scan_count = ScanLog.objects.filter(qr=qr).count()
print(f"✅ Scan Logs Count: {scan_count}")

if scan_count > 0:
    last_scan = ScanLog.objects.filter(qr=qr).last()
    print(
        f"   Last scan by: {last_scan.scanned_by.phone if last_scan.scanned_by else 'Anonymous'}"
    )
    print(f"   Scanned at: {last_scan.scanned_at}")
