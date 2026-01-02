# QR Code Scan va Save Jarayoni

## 📱 Frontend dan Backend ga Request

**Endpoint:** `POST /api/qrcodes/claim/{qr_uuid}/`

**Request Body:**
```json
{
  "first_name": "Muxriddin",
  "last_name": "Rustamov",
  "address": "Toshkent ko'chasi 66",
  "house_number": "66",
  "mahalla": 1
}
```

---

## 🔄 Backend Jarayoni (Tartib bo'yicha)

### 1️⃣ **Request Validation**
```python
# Serializer data ni validatsiya qiladi
serializer = QRCodeClaimSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
validated_data = serializer.validated_data
```

**Tekshirish:**
- `first_name` - bor va to'g'ri formatda
- `last_name` - bor va to'g'ri formatda
- `address` - bor
- `house_number` - bor
- `mahalla` - ID mavjud (database da bor)

---

### 2️⃣ **User Ma'lumotlarini Olish**
```python
user = request.user  # Token dan user olinadi
```

**User obyekti:**
- `user.phone` - Telefon raqam
- `user.first_name` - Ism (yangilanadi)
- `user.last_name` - Familiya (yangilanadi)
- `user.scanned_qr_code` - Scan qilingan QR UUID (yangilanadi)

---

### 3️⃣ **Mahalla Validatsiya**
```python
try:
    mahalla = Mahalla.objects.get(id=validated_data["mahalla"])
except Mahalla.DoesNotExist:
    return Response({"error": "Mahalla not found"}, status=404)
```

---

### 4️⃣ **Retry Loop Boshlash**
```python
for attempt in range(50):  # 50 marta urinish
    # Har retry uchun yangi ID
    timestamp_ms = int(time.time() * 1000)
    random_suffix = random.randint(1, 999)
    next_house_id = timestamp_ms * 1000 + random_suffix
```

**Nima uchun retry kerak?**
- Concurrent requests (bir vaqtda ko'p user scan qilsa)
- IntegrityError (house_id allaqachon band)
- Timestamp-based ID to avoid conflicts

---

### 5️⃣ **Transaction Boshlash**
```python
with transaction.atomic():  # Atomic - yoki hamma save, yoki hech narsa
```

**Transaction nima?**
- Barcha o'zgarishlar bir butun
- Agar biror xato bo'lsa, hamma rollback (undo)
- Database consistency saqlanadi

---

### 6️⃣ **QR Code Lock va Tekshirish**
```python
qr = QRCode.objects.select_for_update().get(uuid=uuid)
```

**select_for_update():**
- QR code qatorini lock qiladi
- Boshqa request kutadi
- Race condition oldini oladi

**Tekshirish:**
```python
if qr.house and qr.house.owner:
    # Allaqachon claim qilingan
    return 400 error
```

---

### 7️⃣ **User Ma'lumotlarini Yangilash** ⭐
```python
# 1. User ismini yangilash
user.first_name = validated_data["first_name"]
user.last_name = validated_data["last_name"]
user.scanned_qr_code = qr.uuid

# 2. Database ga saqlash
user.save(update_fields=["first_name", "last_name", "scanned_qr_code"])
```

**Save tartibi:**
1. User obyektini o'zgartirish (memory da)
2. `save()` chaqirish → SQL UPDATE command
3. Database transaction ichida commit kutadi

---

### 8️⃣ **House Yaratish yoki Yangilash**

#### A) Agar QR code da house mavjud bo'lsa:
```python
if qr.house:
    # Mavjud house ni yangilash
    qr.house.address = validated_data["address"]
    qr.house.house_number = validated_data["house_number"]
    qr.house.mahalla = mahalla
    qr.house.owner = user
    qr.house.save()  # UPDATE houses_house SET ...
```

#### B) Agar yangi house yaratish kerak bo'lsa:
```python
# 1. ID ni tekshirish
existing_qr_with_id = QRCode.objects.filter(
    house_id=next_house_id
).exclude(id=qr.id).first()

if existing_qr_with_id:
    raise IntegrityError("ID band")  # Retry trigger

# 2. House obyektini yaratish
house = House(
    id=next_house_id,  # Timestamp-based ID
    address=validated_data["address"],
    house_number=validated_data["house_number"],
    mahalla=mahalla,
    owner=user
)

# 3. Database ga saqlash
house.save(force_insert=True)  # INSERT INTO houses_house ...
```

---

### 9️⃣ **QR Code ga House ni Bog'lash**
```python
# 1. QR code obyektiga house ni set qilish
qr.house = house

# 2. Database ga saqlash
qr.save(update_fields=["house"])  # UPDATE qrcodes_qrcode SET house_id=...
```

**OneToOne relationship:**
- Bir QR code faqat bitta house ga
- Bir house faqat bitta QR code ga
- Database da UNIQUE constraint

---

### 🔟 **Scan Log Saqlash**
```python
ScanLog.objects.create(
    qr=qr,
    scanned_by=user,
    ip_address=get_client_ip(request)
)
```

**ScanLog jadvalida:**
- `qr` - QRCode (ForeignKey)
- `scanned_by` - User
- `ip_address` - IP manzil
- `scanned_at` - Vaqt (auto)

---

### 1️⃣1️⃣ **Transaction Commit**
```python
# Agar hech qanday xato bo'lmasa:
# - User save bo'ladi
# - House save bo'ladi
# - QRCode house_id yangilanadi
# - ScanLog save bo'ladi
# HAMMA bir vaqtda commit!
```

---

### 1️⃣2️⃣ **Success Response**
```json
{
  "message": "House claimed successfully",
  "house": {
    "id": 1704207654321542,
    "address": "Toshkent ko'chasi 66",
    "number": "66",
    "mahalla": "Chilonzor",
    "district": "Chilonzor tumani",
    "region": "Toshkent"
  },
  "owner": {
    "phone": "+998901234567",
    "first_name": "Muxriddin",
    "last_name": "Rustamov",
    "role": "client"
  },
  "qr": {
    "id": 1,
    "uuid": "65eb5437b84b4fc9",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_65eb5437b84b4fc9",
    "is_claimed": true
  }
}
```

---

## ❌ Agar Xatolik Bo'lsa

### IntegrityError (house_id band):
```python
except IntegrityError as ie:
    # Transaction rollback
    # - User yangilanishi bekor
    # - House yaratilishi bekor
    # - QRCode yangilanishi bekor
    
    # Keyingi retry ga o'tadi (yangi ID bilan)
    continue
```

### Boshqa xatolar:
- `Mahalla.DoesNotExist` → 404
- `QRCode.DoesNotExist` → 404
- Already claimed → 400
- 50 retry exhausted → 400

---

## 📊 Database da Save Tartibi

### 1. **users_user** jadval:
```sql
UPDATE users_user 
SET first_name = 'Muxriddin',
    last_name = 'Rustamov',
    scanned_qr_code = '65eb5437b84b4fc9'
WHERE id = 1;
```

### 2. **houses_house** jadval:
```sql
INSERT INTO houses_house (id, address, house_number, mahalla_id, owner_id)
VALUES (1704207654321542, 'Toshkent ko\'chasi 66', '66', 1, 1);
```

### 3. **qrcodes_qrcode** jadval:
```sql
UPDATE qrcodes_qrcode 
SET house_id = 1704207654321542
WHERE id = 1;
```

### 4. **scans_scanlog** jadval:
```sql
INSERT INTO scans_scanlog (qr_id, scanned_by_id, ip_address, scanned_at)
VALUES (1, 1, '127.0.0.1', NOW());
```

---

## ✅ Save Muvaffaqiyatli Bo'lishi Uchun

1. ✅ User authenticated (token to'g'ri)
2. ✅ Mahalla ID mavjud
3. ✅ QR code UUID topildi
4. ✅ QR code hali claim qilinmagan
5. ✅ House ID unique (retry logic)
6. ✅ Transaction atomic (hamma yoki hech narsa)

---

## 🐛 Muammolar va Yechimlar

### Muammo 1: "UNIQUE constraint failed"
**Sabab:** House ID allaqachon QRCode da ishlatilgan
**Yechim:** Timestamp + random ID (har retry yangi)

### Muammo 2: User ma'lumotlari saqlanmaydi
**Sabab:** Transaction rollback bo'lsa, user ham rollback
**Yechim:** ✅ Hozir to'g'ri - user transaction ichida save

### Muammo 3: Race condition
**Sabab:** Ikkita user bir vaqtda scan qilsa
**Yechim:** select_for_update() + atomic transaction

### Muammo 4: 50 retry ham fail
**Sabab:** Barcha ID lar band (impossible hozir)
**Yechim:** Timestamp milliseconds + random = unique

---

## 📝 Summary

**Save tartibi:**
1. 🔐 User authenticate
2. ✅ Validate data
3. 🔒 Lock QR code
4. 👤 Update user (first_name, last_name, scanned_qr_code)
5. 🏠 Create/Update house
6. 🔗 Link QR → House
7. 📊 Log scan
8. ✅ Commit all

**Hamma bir transaction da!**
