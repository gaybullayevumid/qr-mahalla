import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection

print("🔍 Checking database directly with SQL\n")

with connection.cursor() as cursor:
    # Check QR codes table
    cursor.execute("SELECT id, uuid, house_id FROM qrcodes_qrcode ORDER BY id")
    qr_rows = cursor.fetchall()

    print(f"QR Codes table ({len(qr_rows)} rows):")
    print(f"{'ID':<5} {'UUID':<20} {'house_id':<10}")
    print("-" * 50)
    for row in qr_rows[:10]:
        print(f"{row[0]:<5} {row[1]:<20} {str(row[2]):<10}")

    if len(qr_rows) > 10:
        print(f"... and {len(qr_rows) - 10} more")

    # Check for duplicate house_ids
    print(f"\n📊 Checking for duplicate house_ids:")
    cursor.execute(
        """
        SELECT house_id, COUNT(*) as count
        FROM qrcodes_qrcode
        WHERE house_id IS NOT NULL
        GROUP BY house_id
        HAVING COUNT(*) > 1
    """
    )
    duplicates = cursor.fetchall()

    if duplicates:
        print(f"❌ Found {len(duplicates)} duplicate house_ids:")
        for house_id, count in duplicates:
            print(f"  house_id={house_id}: {count} QR codes")
    else:
        print(f"✅ No duplicates found")

    # Check houses table
    cursor.execute("SELECT id, address FROM houses_house ORDER BY id")
    house_rows = cursor.fetchall()

    print(f"\n📦 Houses table ({len(house_rows)} rows):")
    print(f"{'ID':<5} {'Address':<30}")
    print("-" * 50)
    for row in house_rows:
        print(f"{row[0]:<5} {row[1]:<30}")

    # Check for QR codes with invalid house_ids
    print(f"\n🔗 Checking QR codes with invalid house_ids:")
    cursor.execute(
        """
        SELECT qr.id, qr.uuid, qr.house_id
        FROM qrcodes_qrcode qr
        LEFT JOIN houses_house h ON qr.house_id = h.id
        WHERE qr.house_id IS NOT NULL AND h.id IS NULL
    """
    )
    invalid = cursor.fetchall()

    if invalid:
        print(f"❌ Found {len(invalid)} QR codes with invalid house_ids:")
        for qr_id, qr_uuid, house_id in invalid:
            print(
                f"  QR {qr_uuid} (ID: {qr_id}) -> house_id={house_id} (DOES NOT EXIST)"
            )
    else:
        print(f"✅ All house_ids are valid")
