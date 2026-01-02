# Railway Production Database Cleanup

## ✅ Muammo HAL QILINDI!

**Backend o'zgarish:** `QRCode.house` field `OneToOneField` dan `ForeignKey` ga o'zgartirildi.

**Natija:**
- ✅ `house_id` UNIQUE constraint olib tashlandi
- ✅ Bir house ko'p QR code'larga bog'lanishi mumkin
- ✅ Orphaned house_id lar muammo emas
- ✅ "Bu uy allaqachon boshqa QR kod bilan bog'langan" xatosi yo'q

## Railway Deployment

### 1. Migration Avtomatik Apply Bo'ladi

```bash
# Railway avtomatik ishga tushiradi:
python manage.py migrate

# Migration:
# apps/qrcodes/migrations/0007_change_house_to_foreignkey.py
```

### 2. Tekshirish (Optional)

Railway console ga kirib tekshiring:

```bash
# Railway dashboard -> qr-mahalla project -> Shell
```

### 2. Tekshirish (Optional)

Railway console ga kirib tekshiring:

```bash
# Railway dashboard -> qr-mahalla project -> Shell
```

```python
python manage.py shell

from django.db import connection
cursor = connection.cursor()

# Check if UNIQUE constraint removed
cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='qrcodes_qrcode' AND name LIKE '%house_id%'")
indexes = cursor.fetchall()

if not indexes:
    print("✅ UNIQUE constraint removed!")
else:
    print("❌ UNIQUE constraint still exists:")
    for idx in indexes:
        print(f"  {idx[0]}")
```

## Eski Orphaned house_ids (Agar kerak bo'lsa)

Agar hali ham orphaned house_ids bor bo'lsa, ularni tozalash shart emas. Lekin xohlasangiz:

```python
python manage.py shell

from apps.qrcodes.models import QRCode
from apps.houses.models import House

# Check orphaned house_ids
existing_house_ids = set(House.objects.values_list("id", flat=True))
used_house_ids_in_qr = set(
    QRCode.objects.filter(house_id__isnull=False).values_list("house_id", flat=True)
)
orphaned_ids = used_house_ids_in_qr - existing_house_ids

print(f"Existing Houses: {len(existing_house_ids)}")
print(f"QRCodes with house_id: {len(used_house_ids_in_qr)}")
print(f"Orphaned house_ids: {len(orphaned_ids)}")

if orphaned_ids:
    print(f"Orphaned IDs: {sorted(list(orphaned_ids))[:20]}")
```

### 3. Cleanup Orphaned house_ids

```python
# Agar orphaned_ids bor bo'lsa:
if orphaned_ids:
    cleaned = QRCode.objects.filter(house_id__in=orphaned_ids).update(house_id=None)
    print(f"✅ Cleaned {cleaned} QRCode records")
    
    # Verify
    remaining = QRCode.objects.filter(house_id__isnull=False).count()
    print(f"Remaining QRCodes with house_id: {remaining}")
```

### 4. Duplicate house_id ni tekshiring

```python
from django.db.models import Count

duplicates = (
    QRCode.objects.filter(house_id__isnull=False)
    .values("house_id")
    .annotate(count=Count("house_id"))
    .filter(count__gt=1)
)

print(f"Duplicate house_id: {duplicates.count()}")

if duplicates.count() > 0:
    for dup in duplicates:
        house_id = dup["house_id"]
        count = dup["count"]
        print(f"  house_id {house_id}: used {count} times")
        
        # Keep only first QRCode, clear others
        qrs = QRCode.objects.filter(house_id=house_id).order_by("id")
        first_qr = qrs.first()
        other_qrs = qrs.exclude(id=first_qr.id)
        other_qrs.update(house_id=None)
        print(f"  Kept QR {first_qr.uuid}, cleared {other_qrs.count()} others")
```

### 5. Migration ni tekshiring

```bash
# Check if migration 0006 exists
python manage.py showmigrations qrcodes

# If not applied:
python manage.py migrate qrcodes
```

### 6. Test Qiling

Frontend dan qayta claim qiling. Endi ishlashi kerak!

## Debugging

Agar xato davom etsa, Railway logs ni ko'ring:

```bash
# Railway dashboard -> Logs
# Search for:
"Pre-claim cleanup"
"Found N orphaned house_ids"
"Successfully cleaned up"
```

## Expected Result

```
✅ Orphaned house_ids: 0
✅ Duplicate house_id: 0
✅ Claim works successfully
✅ House saved to database
```

## Frontendda tekshirish

```javascript
// Response should be:
{
  "message": "House claimed successfully",
  "house": {
    "id": 1234567890,
    "address": "...",
    "number": "123",
    "mahalla": "Qatortol",
    "district": "Chilonzor",
    "region": "Toshkent"
  },
  "owner": {
    "phone": "+998...",
    "first_name": "...",
    "last_name": "..."
  }
}
```

## House Database ga Saqlanishini Tekshirish

```python
# Railway console
from apps.houses.models import House

# Check all houses
houses = House.objects.all()
print(f"Total Houses: {houses.count()}")

for h in houses:
    print(f"House {h.id}: {h.address}, owner={h.owner.phone if h.owner else None}")
```
