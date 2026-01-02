# QR Mahalla API Endpoints

## Authentication
- `POST /api/users/telegram-auth/` - Telegram orqali kirish
- `POST /api/users/phone-auth/` - Telefon orqali kirish
- `GET /api/users/profile/` - Foydalanuvchi profili

## QR Code Operations
- `POST /api/qrcodes/scan/` - QR kodni scan qilish (POST body)
- `GET /api/qrcodes/scan/{uuid}/` - QR kodni scan qilish (GET)
- `GET /api/qrcodes/claim/{uuid}/` - ✅ QR kod holatini tekshirish
- `POST /api/qrcodes/claim/{uuid}/` - ✅ Uyni claim qilish
- `GET /api/qrcodes/` - QR kodlar ro'yxati
- `POST /api/qrcodes/create/` - Yangi QR kod yaratish
- `GET /api/qrcodes/{uuid}/` - QR kod detallari

## Regions & Mahallas
- `GET /api/regions/` - Viloyatlar ro'yxati
- `GET /api/districts/` - Tumanlar ro'yxati
- `GET /api/mahallas/` - Mahallalar ro'yxati

## Claim House Endpoint Details

### GET /api/qrcodes/claim/{uuid}/
**Maqsad:** QR kod holatini tekshirish

**Response:**
```json
{
  "qr_uuid": "65eb5437b84b4fc9",
  "qr_id": 123,
  "has_house": true,
  "can_claim": false,
  "message": "Bu uy allaqachon claim qilingan.",
  "house": {
    "id": 1,
    "address": "Toshkent ko'chasi 10",
    "house_number": "10",
    "mahalla_id": 1,
    "mahalla_name": "Qatortol",
    "has_owner": true,
    "owner": {
      "id": 5,
      "phone": "+998901234567",
      "first_name": "Ali",
      "last_name": "Valiyev"
    }
  }
}
```

### POST /api/qrcodes/claim/{uuid}/
**Maqsad:** Uyni claim qilish

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

**Success Response (200):**
```json
{
  "message": "House claimed successfully",
  "house": {
    "id": 2,
    "address": "Toshkent ko'chasi 66",
    "number": "66",
    "mahalla": "Qatortol",
    "district": "Chilonzor",
    "region": "Toshkent"
  },
  "owner": {
    "phone": "+998906252919",
    "first_name": "Muxriddin",
    "last_name": "Rustamov",
    "role": "client"
  },
  "qr": {
    "id": 123,
    "uuid": "65eb5437b84b4fc9",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_65eb5437b84b4fc9"
  }
}
```

**Error Responses:**

**400 - Already Claimed:**
```json
{
  "error": "Bu uy allaqachon boshqa foydalanuvchi tomonidan claim qilingan.",
  "error_en": "This house is already claimed by another user.",
  "owner": "+998901234567"
}
```

**400 - Already Claimed by You:**
```json
{
  "error": "Siz allaqachon bu uyni claim qilgansiz.",
  "error_en": "You have already claimed this house.",
  "house_id": 1,
  "is_reclaim_attempt": true
}
```

**404 - QR Not Found:**
```json
{
  "error": "QR code not found"
}
```

## Frontend Developer uchun:

**Endpoint mavjud!** ✅
- URL: `https://qr-mahalla.up.railway.app/api/qrcodes/claim/{uuid}/`
- Method: `POST` (claim qilish uchun)
- Method: `GET` (holat tekshirish uchun)
- Authorization: `Bearer {token}` kerak

**To'g'ri ishlatish:**
```javascript
// 1. QR kod holatini tekshirish
const response = await axios.get(`/api/qrcodes/claim/${uuid}/`, {
  headers: { Authorization: `Bearer ${token}` }
});

// 2. Uyni claim qilish
const claimResponse = await axios.post(`/api/qrcodes/claim/${uuid}/`, {
  first_name: "Muxriddin",
  last_name: "Rustamov",
  address: "Toshkent ko'chasi 66",
  house_number: "66",
  mahalla: 1
}, {
  headers: { Authorization: `Bearer ${token}` }
});
```
