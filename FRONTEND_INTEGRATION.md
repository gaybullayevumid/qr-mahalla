# Frontend Integration Guide

## Regular User Workflow (Oddiy foydalanuvchi uchun)

Regular user uchun workflow quyidagicha bo'lishi kerak:

### 1-Qadam: Scanner ochilishi
Home.jsx da regular user uchun **scanner** chiqishi kerak (viloyatlar ro'yxati emas!)

### 2-Qadam: QR Code Skanerlash
User QR code ni skanerlaydi va UUID ni oladi (masalan: `abc123def456`)

### 3-Qadam: Backendga GET request
```javascript
// Scanner.jsx da
const scannedUUID = "abc123def456"; // QR code dan olingan UUID

const response = await fetch(`http://192.168.0.158:8000/api/qrcodes/scan-uuid/${scannedUUID}/`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`, // yoki Token ${token}
    'Content-Type': 'application/json',
  }
});

const data = await response.json();
```

### 4-Qadam: Response bo'yicha action
**Agar house unclaimed bo'lsa:**
```json
{
  "status": "unclaimed",
  "is_claimed": false,
  "can_claim": true,
  "message": "This house has no owner yet. You can claim it.",
  "uuid": "abc123def456",
  "house_address": "Toshkent ko'chasi 123",
  "mahalla": "Chilonzor",
  "district": "Chilonzor tumani",
  "region": "Toshkent shahar",
  "house_number": "123",
  "claim_url": "/api/qrcodes/claim-uuid/abc123def456/"
}
```
→ **FORM ko'rsatiladi** (first_name, last_name, passport_id, address)

**Agar house claimed bo'lsa:**
```json
{
  "status": "claimed",
  "is_claimed": true,
  "can_claim": false,
  "first_name": "Alisher",
  "last_name": "Navoiy",
  "phone": "+998901234567",
  "house_address": "Toshkent ko'chasi 123",
  "mahalla": "Chilonzor",
  "district": "Chilonzor tumani",
  "region": "Toshkent shahar"
}
```
→ **Ma'lumotlar ko'rsatiladi** (owner ma'lumotlari)

### 5-Qadam: Form Submit (claim qilish)
Agar house unclaimed bo'lsa, user forma to'ldiradi va submit qiladi:

```javascript
// ClaimForm.jsx da
const claimData = {
  first_name: "Alisher",
  last_name: "Navoiy",
  passport_id: "AA1234567",
  address: "Toshkent, Mirobod tumani, Buyuk Ipak Yo'li 123"
};

const response = await fetch(`http://192.168.0.158:8000/api/qrcodes/claim-uuid/${scannedUUID}/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(claimData)
});

const result = await response.json();

if (response.ok) {
  // Success! House claimed
  console.log('Muvaffaqiyatli claim qilindi!', result);
  // Show success message or redirect
} else {
  // Error
  console.error('Xatolik:', result.error);
}
```

### Success Response:
```json
{
  "message": "House claimed successfully",
  "status": "success",
  "house": {
    "id": "1",
    "address": "Toshkent ko'chasi 123",
    "house_number": "123",
    "mahalla": "Chilonzor"
  },
  "owner": {
    "phone": "+998901234567",
    "first_name": "Alisher",
    "last_name": "Navoiy"
  },
  "qr_code": {
    "id": 1,
    "uuid": "abc123def456"
  }
}
```

---

## API Endpoints

### 1. QR Code Skanerlash (UUID bilan)
- **URL:** `GET /api/qrcodes/scan-uuid/{uuid}/`
- **Authentication:** Required (Bearer token yoki Token)
- **Parameters:** 
  - `uuid` (string): QR code UUID (masalan: "abc123def456")
- **Response:** House status va ma'lumotlari

### 2. House Claim qilish
- **URL:** `POST /api/qrcodes/claim-uuid/{uuid}/`
- **Authentication:** Required
- **Parameters:** 
  - `uuid` (string): QR code UUID
- **Body:**
  ```json
  {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "passport_id": "string (required)",
    "address": "string (required)"
  }
  ```
- **Response:** Success message va house ma'lumotlari

---

## Frontend Component Structure

```
Home.jsx
├── if (user.role === 'user')
│   └── <Scanner />
│       ├── QR Scanner Library (react-qr-scanner yoki html5-qrcode)
│       ├── onScan(uuid) → GET /api/qrcodes/scan-uuid/{uuid}/
│       └── if (unclaimed)
│           └── <ClaimForm />
│               └── onSubmit → POST /api/qrcodes/claim-uuid/{uuid}/
└── else (admin, government, etc.)
    └── <RegionsList />
```

---

## Xatolarni Bartaraf Qilish

### ❌ 403 Forbidden Error
**Muammo:** `/api/regions/mahalla/` ga POST qilmoqda
**Yechim:** Regular user uchun `/api/qrcodes/claim-uuid/{uuid}/` ishlatilishi kerak

### ❌ QR Code Not Found
**Muammo:** UUID noto'g'ri yoki QR code yo'q
**Yechim:** QR code UUID ni to'g'ri skanerlash

### ❌ House Already Claimed
**Muammo:** House allaqachon owner ga biriktirilgan
**Yechim:** Faqat owner ma'lumotlarini ko'rsatish (claim form yo'q)

---

## Test Qilish

1. Backend ishga tushiring:
```bash
python manage.py runserver 192.168.0.158:8000
```

2. Regular user bilan login qiling

3. QR code yarating (agar yo'q bo'lsa):
   - Admin sifatida mahalla va house yaratish
   - House uchun QR code avtomatik yaratiladi

4. QR code UUID ni oling va test qiling:
```bash
# Scan endpoint
GET http://192.168.0.158:8000/api/qrcodes/scan-uuid/{uuid}/

# Claim endpoint
POST http://192.168.0.158:8000/api/qrcodes/claim-uuid/{uuid}/
{
  "first_name": "Test",
  "last_name": "User",
  "passport_id": "AA1234567",
  "address": "Test address"
}
```

---

## Important Notes

1. ⚠️ Regular user `/api/regions/mahalla/` ga POST qila olmaydi (403 Forbidden)
2. ✅ Regular user `/api/qrcodes/claim-uuid/{uuid}/` ga POST qilishi kerak
3. ✅ Scanner UUID ni o'qiydi (ID emas, UUID!)
4. ✅ Claim form faqat unclaimed house lar uchun ko'rsatiladi
5. ✅ User role avtomatik "owner" ga o'zgaradi claim qilingandan keyin
