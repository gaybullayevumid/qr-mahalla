import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    print("🔍 Checking house_id=1 in QR codes table\n")

    cursor.execute(
        """
        SELECT id, uuid, house_id
        FROM qrcodes_qrcode
        WHERE house_id = 1
    """
    )
    rows = cursor.fetchall()

    print(f"QR codes with house_id=1: {len(rows)}")
    for row in rows:
        print(f"  QR ID {row[0]}: UUID={row[1]}, house_id={row[2]}")

    print(f"\n📊 All QR codes with non-null house_id:")
    cursor.execute(
        """
        SELECT id, uuid, house_id
        FROM qrcodes_qrcode
        WHERE house_id IS NOT NULL
    """
    )
    all_with_house = cursor.fetchall()
    print(f"Total: {len(all_with_house)}")
    for row in all_with_house:
        print(f"  QR ID {row[0]}: UUID={row[1]}, house_id={row[2]}")
