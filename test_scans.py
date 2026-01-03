#!/usr/bin/env python
"""Test scans endpoint."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from apps.scans.views import ScanLogViewSet
from apps.scans.models import ScanLog
import json

print("=" * 80)
print("=== TEST: GET /api/scans/ ===")
print("=" * 80)

factory = RequestFactory()
viewset = ScanLogViewSet.as_view({"get": "list"})

# GET all scans
request = factory.get("/api/scans/")
response = viewset(request)

print(f"\n✅ Status: {response.status_code}")
print(f"\n✅ Total Scans: {len(response.data)}")
print("\nFirst 5 Scans:")
print(json.dumps(response.data[:5], indent=2, ensure_ascii=False))

# Count by QR
print("\n" + "=" * 80)
print("=== Scan Statistics ===")
print("=" * 80)

total_scans = ScanLog.objects.count()
unique_qrs = ScanLog.objects.values('qr').distinct().count()
scanned_qrs = ScanLog.objects.filter(qr__is_scanned=True).count()

print(f"\nTotal scans: {total_scans}")
print(f"Unique QR codes scanned: {unique_qrs}")
print(f"QR codes marked as scanned: {scanned_qrs}")
