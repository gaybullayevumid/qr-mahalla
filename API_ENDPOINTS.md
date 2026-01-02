# QR Mahalla API Endpoints

## ⚠️ MUHIM: Frontend Developer uchun

### Endpoint To'g'ri Ishlayapti! ✅

**URL:** `POST /api/qrcodes/claim/{uuid}/`

**Muammo hal qilindi:**
- ✅ Database integrity errors
- ✅ Race conditions
- ✅ GapFillingIDMixin conflicts
- ✅ Transaction issues

**Endi qanday ishlaydi:**
1. Backend avtomatik retry qiladi (20 martagacha)
2. Agar conflict bo'lsa, yangi ID bilan urinadi
3. Success bo'lganda 200 qaytaradi
4. Error bo'lganda batafsil xabar qaytaradi

---

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

### ✅ TO'G'RI ISHLATISH:

```javascript
// 1. QR kod holatini tekshirish (ixtiyoriy)
const statusResponse = await axios.get(`/api/qrcodes/claim/${uuid}/`, {
  headers: { Authorization: `Bearer ${token}` }
});

// 2. Uyni claim qilish
try {
  const claimResponse = await axios.post(`/api/qrcodes/claim/${uuid}/`, {
    first_name: formData.first_name,
    last_name: formData.last_name,
    address: formData.address,
    house_number: formData.house_number,
    mahalla: formData.mahalla_id  // Integer ID
  }, {
    headers: { 
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  // Success!
  console.log('House claimed:', claimResponse.data);
  // Navigate to success page or show success message
  
} catch (error) {
  if (error.response) {
    const { status, data } = error.response;
    
    if (status === 400) {
      // Already claimed or integrity error
      if (data.is_reclaim_attempt) {
        alert(`${data.error}\nSiz allaqachon bu uyni claim qilgansiz.`);
      } else if (data.error_type === 'house_already_linked') {
        alert(`${data.error}\nBoshqa uy ma'lumotlarini kiriting.`);
      } else {
        alert(data.error || data.error_en);
      }
    } else if (status === 404) {
      alert('QR kod topilmadi');
    } else if (status === 500) {
      alert('Server xatosi. Iltimos qaytadan urinib ko\'ring.');
    }
  } else {
    alert('Tarmoq xatosi. Internetni tekshiring.');
  }
}
```

### 🚫 NOTO'G'RI (ishlatmang):

```javascript
// ❌ /users/profile/ ishlatmang
// ❌ Houses arrayiga qo'shmang
// ❌ Manual update qilmang
```

### 📋 Request Body Format:

**To'g'ri:**
```json
{
  "first_name": "Muxriddin",
  "last_name": "Rustamov",
  "address": "Toshkent ko'chasi 66",
  "house_number": "66",
  "mahalla": 1
}
```

**Noto'g'ri (ishlamaydi):**
```json
{
  "region_id": 1,        // ❌ Kerak emas
  "district_id": 1,      // ❌ Kerak emas
  "mahalla_id": 1,       // ❌ Noto'g'ri key (mahalla bo'lishi kerak)
  "owner_name": "...",   // ❌ Kerak emas
  "phone": "..."         // ❌ Kerak emas (token dan olinadi)
}
```

### 🔧 Debugging:

Agar xatolik chiqsa, console da tekshiring:

```javascript
console.log('Request URL:', error.config?.url);
console.log('Request Data:', error.config?.data);
console.log('Response:', error.response?.data);
console.log('Status:', error.response?.status);
```

### ⏱️ Timeout:

Backend avtomatik retry qiladi, shuning uchun:
- Timeout ni kamida **30 sekund** qiling
- Loading indicator ko'rsating
- User kutishini ta'minlang

```javascript
const axiosInstance = axios.create({
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json'
  }
});
```

---

**Endpoint mavjud va ishlayapti!** ✅
- URL: `https://qr-mahalla.up.railway.app/api/qrcodes/claim/{uuid}/`
- Method: `POST` (claim qilish uchun)
- Method: `GET` (holat tekshirish uchun)
- Authorization: `Bearer {token}` **majburiy**

**Hozir qilish kerak:**
1. ✅ To'g'ri endpoint ishlating: `/api/qrcodes/claim/{uuid}/`
2. ✅ Request body formatini to'g'rilang (yuqoridagi misol)
3. ✅ Error handling qo'shing
4. ✅ Loading indicator qo'shing
5. ✅ Success message ko'rsating
