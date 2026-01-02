import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection
from apps.qrcodes.models import QRCode
from apps.houses.models import House

cursor = connection.cursor()

# Check table schema
print("=" * 50)
print("QRCode table info:")
cursor.execute("PRAGMA table_info(qrcodes_qrcode)")
for col in cursor.fetchall():
    print(
        f"  Column: {col[1]}, Type: {col[2]}, NotNull: {col[3]}, Default: {col[4]}, PK: {col[5]}"
    )

print("\n" + "=" * 50)
print("Checking indexes:")
cursor.execute(
    "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='qrcodes_qrcode'"
)
for idx in cursor.fetchall():
    if idx[0]:
        print(f"  {idx[0]}")

print("\n" + "=" * 50)
print("Current data:")
print(f"Total Houses: {House.objects.count()}")
print(f"Total QRCodes: {QRCode.objects.count()}")
print(f"QRCodes with houses: {QRCode.objects.filter(house__isnull=False).count()}")

print("\n" + "=" * 50)
print("QRCode-House mappings:")
cursor.execute("SELECT id, uuid, house_id FROM qrcodes_qrcode ORDER BY id")
for row in cursor.fetchall():
    print(f"  QR ID={row[0]}, UUID={row[1]}, house_id={row[2]}")

print("\n" + "=" * 50)
print("Houses:")
cursor.execute("SELECT id, address, mahalla_id, owner_id FROM houses_house ORDER BY id")
for row in cursor.fetchall():
    print(f"  House ID={row[0]}, Address={row[1]}, Mahalla={row[2]}, Owner={row[3]}")
