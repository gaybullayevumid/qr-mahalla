import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

print("=== QR Code 65eb5437b84b4fc9 ===")
cursor.execute(
    "SELECT id, uuid, house_id FROM qrcodes_qrcode WHERE uuid = '65eb5437b84b4fc9'"
)
row = cursor.fetchone()
if row:
    print(f"ID: {row[0]}, UUID: {row[1]}, House ID: {row[2]}")
else:
    print("QR not found!")

print("\n=== All QR Codes ===")
cursor.execute("SELECT id, uuid, house_id FROM qrcodes_qrcode LIMIT 10")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, UUID: {row[1]}, House: {row[2]}")

print("\n=== All Houses ===")
cursor.execute("SELECT id, address, owner_id, mahalla_id FROM houses_house LIMIT 10")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Address: {row[1]}, Owner: {row[2]}, Mahalla: {row[3]}")

print("\n=== Check for duplicate house_id in QR codes ===")
cursor.execute(
    """
    SELECT house_id, COUNT(*) as count 
    FROM qrcodes_qrcode 
    WHERE house_id IS NOT NULL 
    GROUP BY house_id 
    HAVING count > 1
"""
)
duplicates = cursor.fetchall()
if duplicates:
    print("⚠️  Duplicates found:")
    for row in duplicates:
        print(f"  House {row[0]} has {row[1]} QR codes")
else:
    print("✅ No duplicates")

conn.close()
