# POST Endpoints - Qaysi Endpointga Nima Yuborish Kerak

## 1. 🔐 LOGIN - Tizimga kirish

**Endpoint:** `POST /api/users/login/`

**Qachon ishlatiladi:** Telegram Mini App ochilganda birinchi marta

**Request Body:**
```json
{
  "telegram_id": 123456789,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "telegram_id": 123456789,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "role": "resident",
    "houses": [
      {
        "id": 1234567890,
        "address": "Yunusobod tumani, Bodomzor MFY, 12-uy",
        "house_number": "12",
        "mahalla": "Bodomzor",
        "district": "Yunusobod",
        "region": "Toshkent shahar",
        "scanned_qr_code": "abc123def456"
      }
    ]
  }
}
```

**JavaScript misoli:**
```javascript
const loginResponse = await axios.post('/api/users/login/', {
  telegram_id: telegramUser.id,
  username: telegramUser.username,
  first_name: telegramUser.first_name,
  last_name: telegramUser.last_name
});

const token = loginResponse.data.token;
localStorage.setItem('authToken', token);
```

---

## 2. 📱 SCAN QR - Foydalanuvchi ma'lumotlarini saqlash

**Endpoint:** `POST /api/qrcodes/<uuid>/scan/`

**Qachon ishlatiladi:** QR code scan qilingandan keyin, user ma'lumotlarini saqlash uchun

**Headers:**
```
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "success": true,
  "message": "QR code scanned successfully",
  "qr_code": {
    "uuid": "abc123def456",
    "is_claimed": false,
    "house": null,
    "region": "Toshkent shahar",
    "district": "Yunusobod",
    "mahalla": "Bodomzor"
  },
  "user": {
    "id": 1,
    "telegram_id": 123456789,
    "first_name": "John",
    "last_name": "Doe",
    "scanned_qr_code": "abc123def456"
  }
}
```

**JavaScript misoli:**
```javascript
const scanResponse = await axios.post(
  `/api/qrcodes/${uuid}/scan/`,
  {
    first_name: firstName,
    last_name: lastName
  },
  {
    headers: {
      'Authorization': `Token ${token}`
    }
  }
);

console.log('User scanned_qr_code:', scanResponse.data.user.scanned_qr_code);
```

**Eslatma:**
- `first_name` va `last_name` - **IXTIYORIY** (yuborilsa, foydalanuvchi ma'lumotlariga saqlanadi)
- `scanned_qr_code` - avtomatik ravishda user ga biriktiriladi

---

## 3. 🏠 CLAIM HOUSE - Uyni egallash

**Endpoint:** `POST /api/qrcodes/<uuid>/claim/`

**Qachon ishlatiladi:** User forma to'ldirib, uyni o'ziga bog'lash tugmasini bosganda

**Headers:**
```
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "address": "Yunusobod tumani, Bodomzor MFY, 12-uy",
  "house_number": "12",
  "mahalla": 23
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "House claimed successfully",
  "house": {
    "id": 1234567890,
    "address": "Yunusobod tumani, Bodomzor MFY, 12-uy",
    "mahalla": {
      "id": 23,
      "name": "Bodomzor",
      "district": {
        "id": 5,
        "name": "Yunusobod",
        "region": {
          "id": 1,
          "name": "Toshkent shahar"
        }
      }
    },
    "owner": {
      "id": 1,
      "telegram_id": 123456789,
      "first_name": "John",
      "last_name": "Doe"
    },
    "created_at": "2026-01-02T12:34:56Z"
  },
  "qr_code": {
    "uuid": "abc123def456",
    "is_claimed": true,
    "claimed_at": "2026-01-02T12:34:56Z"
  }
}
```

**Error Response (400) - Allaqachon claim qilingan (boshqa user):**
```json
{
  "error": "Bu uy allaqachon boshqa foydalanuvchi tomonidan claim qilingan.",
  "error_en": "This house is already claimed by another user.",
  "owner": "+998901234567"
}
```

**Error Response (400) - Siz allaqachon claim qilgansiz:**
```json
{
  "error": "Siz allaqachon bu uyni claim qilgansiz.",
  "error_en": "You have already claimed this house.",
  "house_id": 1234567890,
  "is_reclaim_attempt": true
}
```

**Error Response (400) - Validatsiya xatosi:**
```json
{
  "first_name": ["This field is required."],
  "last_name": ["This field is required."],
  "address": ["This field is required."],
  "house_number": ["This field is required."],
  "mahalla": ["This field is required."]
}
```

**Error Response (404) - Mahalla topilmadi:**
```json
{
  "error": "Mahalla not found"
}
```

**JavaScript misoli:**
```javascript
const claimResponse = await axios.post(
  `/api/qrcodes/${uuid}/claim/`,
  {
    first_name: formData.firstName,
    last_name: formData.lastName,
    address: formData.address,
    house_number: formData.houseNumber,
    mahalla: parseInt(formData.mahallaId)
  },
  {
    headers: {
      'Authorization': `Token ${token}`
    }
  }
);

if (claimResponse.status === 200) {
  alert('Uy muvaffaqiyatli egallandi!');
  console.log('House ID:', claimResponse.data.house.id);
}
```

**MAJBURIY maydonlar (Backend QRCodeClaimSerializer):**
- ✅ `first_name` - Foydalanuvchi ismi (max 100 belgi)
- ✅ `last_name` - Foydalanuvchi familiyasi (max 100 belgi)
- ✅ `address` - To'liq manzil (max 255 belgi)
- ✅ `house_number` - Uy raqami (max 50 belgi)
- ✅ `mahalla` - Mahalla ID (integer)

---

## 4. 🏘️ GET HOUSES - Foydalanuvchi uylari

**Endpoint:** `GET /api/houses/`

**Qachon ishlatiladi:** User o'z claim qilgan uylarini ko'rish uchun

**Headers:**
```
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
```json
[
  {
    "id": 1234567890,
    "owner": 1,
    "mahalla": 23,
    "house_number": "12",
    "address": "Yunusobod tumani, Bodomzor MFY, 12-uy",
    "created_at": "2026-01-02T12:34:56Z"
  }
]
```

**JavaScript misoli:**
```javascript
const housesResponse = await axios.get('/api/houses/', {
  headers: {
    'Authorization': `Token ${token}`
  }
});

console.log('My houses:', housesResponse.data);
```

**Role-based Access:**
- `client` - faqat o'z uylarini ko'radi
- `leader` - o'z mahallasidagi barcha uylarni ko'radi  
- `admin` - barcha uylarni ko'radi

---

## 5. 👥 GET USER LIST - Foydalanuvchilar ro'yxati (houses bilan)

**Endpoint:** `GET /api/users/list/`

**Qachon ishlatiladi:** Adminlar/Leaderlar foydalanuvchilarni va ularning uylarini ko'rish uchun

**Headers:**
```
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
```json
[
  {
    "id": 4,
    "phone": "+998906252919",
    "first_name": "Muxriddin",
    "last_name": "Rustamov",
    "role": "client",
    "is_verified": false,
    "houses": [
      {
        "id": 1,
        "address": "Test address",
        "house_number": "123",
        "mahalla": "Qatortol",
        "district": "Chilonzor",
        "region": "Toshkent",
        "scanned_qr_code": "10bfb53c26d34ad2"
      }
    ]
  }
]
```

**JavaScript misoli:**
```javascript
const usersResponse = await axios.get('/api/users/list/', {
  headers: {
    'Authorization': `Token ${token}`
  }
});

console.log('Users with houses:', usersResponse.data);
```

**Role-based Access:**
- `client` - faqat o'zini ko'radi (houses bilan)
- `leader` - o'z mahallasidagi userlarni ko'radi (houses bilan)
- `admin` - barcha userlarni ko'radi (houses bilan)

---

## 6. 👤 GET USER PROFILE - Profil ma'lumotlari

**Endpoint:** `GET /api/users/profile/`

**Headers:**
```
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
```json
{
  "id": 4,
  "phone": "+998906252919",
  "role": "client",
  "first_name": "Muxriddin",
  "last_name": "Rustamov",
  "is_verified": false,
  "scanned_qr_code": "abc123def456",
  "houses": [
    {
      "id": 1,
      "address": "Test address",
      "house_number": "123",
      "mahalla": "Qatortol",
      "district": "Chilonzor",
      "region": "Toshkent",
      "scanned_qr_code": "10bfb53c26d34ad2"
    }
  ]
}
```

---

## 📊 To'liq Workflow (Ketma-ketlik)

```
1️⃣ QR CODE SCAN
   └─> Telegram QR scanner ochadi
   └─> URL: t.me/bot?startapp=abc123def456
   └─> Frontend UUID ni ajratadi: "abc123def456"

2️⃣ LOGIN
   └─> POST /api/users/login/
   └─> Body: {telegram_id, username, first_name, last_name}
   └─> Response: {token, user}
   └─> Token ni localStorage ga saqlash

3️⃣ SCAN POST (User ma'lumotlarini saqlash)
   └─> POST /api/qrcodes/abc123def456/scan/
   └─> Headers: Authorization: Token xxx
   └─> Body: {first_name, last_name}
   └─> Response: {user.scanned_qr_code = "abc123def456"}

4️⃣ REGIONS, DISTRICTS, MAHALLAS (GET endpointlar)
   └─> GET /api/regions/
   └─> GET /api/regions/districts/?region=1
   └─> GET /api/regions/mahallas/?district=5

5️⃣ CLAIM HOUSE
   └─> POST /api/qrcodes/abc123def456/claim/
   └─> Body: {address, mahalla, region, district}
   └─> Response: {house, qr_code}
   └─> Success: QR code is_claimed = true
```

---

## 🚨 Xatoliklarni Tutish (Error Handling)

```javascript
async function claimHouse(uuid, formData, token) {
  try {
    const response = await axios.post(
      `/api/qrcodes/${uuid}/claim/`,
      {
        first_name: formData.firstName,
        last_name: formData.lastName,
        address: formData.address,
        house_number: formData.houseNumber,
        mahalla: parseInt(formData.mahallaId)
      },
      {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    // ✅ Muvaffaqiyatli
    alert('Uy muvaffaqiyatli egallandi!');
    console.log('House:', response.data.house);
    console.log('Owner:', response.data.owner);
    return response.data;
    
  } catch (error) {
    if (error.response) {
      // Server xatolik qaytardi
      
      if (error.response.status === 400) {
        // Validatsiya xatoligi yoki allaqachon claim qilingan
        const errorData = error.response.data;
        
        if (errorData.error) {
          // "Bu uy allaqachon boshqa foydalanuvchi tomonidan claim qilingan."
          // yoki "Siz allaqachon bu uyni claim qilgansiz."
          alert(errorData.error);
          
          if (errorData.is_reclaim_attempt) {
            console.log('House already claimed by you:', errorData.house_id);
          } else if (errorData.owner) {
            console.log('Claimed by:', errorData.owner);
          }
        } else {
          // Forma validatsiya xatoligi
          Object.keys(errorData).forEach(field => {
            console.error(`${field}: ${errorData[field]}`);
          });
          alert('Forma to\'ldirishda xatolik!');
        }
        
      } else if (error.response.status === 404) {
        if (error.response.data.error === 'Mahalla not found') {
          alert('Mahalla topilmadi!');
        } else {
          alert('QR code topilmadi!');
        }
        
      } else if (error.response.status === 401) {
        alert('Tizimga kirishingiz kerak!');
        // Login sahifasiga yo'naltirish
        window.location.href = '/login';
      }
      
    } else if (error.request) {
      // Request yuborildi, lekin response kelmadi
      alert('Internet bilan bog\'laning!');
      
    } else {
      // Boshqa xatolik
      console.error('Error:', error.message);
      alert('Xatolik yuz berdi!');
    }
  }
}
```

---

## 🔑 Muhim Eslatmalar

1. **Token avtorizatsiya:**
   - Har bir request (scan, claim) da `Authorization: Token xxx` header yuborish MAJBURIY
   - Token ni login dan olib, localStorage ga saqlash kerak

2. **UUID format:**
   - QR code UUID 16 belgidan iborat: `abc123def456`
   - Telegram URL dan ajratib olish kerak

3. **Scan POST vs GET:**
   - `GET /api/qrcodes/<uuid>/scan/` - Faqat QR ma'lumotlarini olish
   - `POST /api/qrcodes/<uuid>/scan/` - User ma'lumotlarini saqlash (first_name, last_name, scanned_qr_code)

4. **Claim majburiy maydonlar:**
   - `address` - to'liq manzil text
   - `mahalla` - mahalla ID raqami (number)

5. **scanned_qr_code:**
   - POST scan qilinganda avtomatik user ga biriktiriladi
   - Claim qilishda bu UUID ishlatilinadi

---

## 🎯 React/JavaScript To'liq Kod Namunasi

```jhouseNumber: '',
    avascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'https://qr-mahalla.up.railway.app/api';

function QRClaimFlow() {
  const [uuid, setUuid] = useState('');
  const [token, setToken] = useState('');
  const [qrData, setQrData] = useState(null);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    address: '',
    regionId: '',
    districtId: '',
    mahallaId: ''
  });

  // 1. Login
  const login = async (telegramUser) => {
    const response = await axios.post(`${API_BASE}/users/login/`, {
      telegram_id: telegramUser.id,
      username: telegramUser.username,
      first_name: telegramUser.first_name,
      last_name: telegramUser.last_name
    });
    
    setToken(response.data.token);
    localStorage.setItem('authToken', response.data.token);
  };

  // 2. Scan va user ma'lumotlarini saqlash
  const scanQR = async () => {
    const response = await axios.post(
      `${API_BASE}/qrcodes/${uuid}/scan/`,
      {
        first_name: formData.firstName,
        last_name: formData.lastName
      },
      {
        headers: { 'Authorization': `Token ${token}` }
      }
    );
    
    setQrData(response.data.qr_code);
    console.log('User scanned_qr_code:', response.data.user.scanned_qr_code);
  };

  // 3. Uyni claim qilish
  const claimHouse = async () => {
    try {
      const response = await axios.post(
        `${API_BASE}/qrcodes/${uuid}/claim/`,
        {first_name: formData.firstName,
          last_name: formData.lastName,
          address: formData.address,
          house_number: formData.houseNumber,
          mahalla: parseInt(formData.mahallaId)
        },
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      
      alert('Uy muvaffaqiyatli egallandi!');
      console.log('House:', response.data.house);
      console.log('Owner:', response.data.owner);
      
    } catch (error) {
      if (error.response?.status === 400) {
        alert(error.response.data.error || 'Forma xatosi!');
      } else if (error.response?.status === 404) {
        alert(error.response.data.error || f (error.response?.status === 404) {
        alert('QR code topilmadi!');
      }
    }
  };

  return (
    <div>
      <h1>QR Mahalla - Uyni Egallash</h1>
      
      {/* Scan qism */}
      <input 
        placeholder="Ism" 
        value={formData.firstName}
        onChange={(e) => setFormData({...formData, firstName: e.target.value})}
      />
      <input 
        placeholder="Familiya" 
        value={formData.lastName}
        onChange={(e) => setFormData({...formData, lastName: e.target.value})}
      />
      <button onClick={scanQR}>QR Scan</button>

      {/* Claim qism */}
      <input 
        placeholder="Manzil" 
        value={formData.address}
       input 
        placeholder="Uy raqami" 
        value={formData.houseNumber}
        onChange={(e) => setFormData({...formData, houseNumber: e.target.value})}
      />
      < onChange={(e) => setFormData({...formData, address: e.target.value})}
      />
      <select onChange={(e) => setFormData({...formData, mahallaId: e.target.value})}>
        <option>Mahalla tanlang</option>
        {/* Mahallalar ro'yxati */}
      </select>
      <button onClick={claimHouse}>Uyni Egallash</button>
    </div>
  );
}

export default QRClaimFlow;
```

---

## 🔧 Backend O'zgarishlar

### ✅ UNIQUE Constraint Olib Tashlandi

**Muammo:** `qrcodes_qrcode.house_id` da UNIQUE constraint bor edi. Bu orphaned house_id lar yoki random ID collisionlar tufayli xatolarga olib kelardi.

**Yechim:** `QRCode.house` ni `OneToOneField` dan `ForeignKey` ga o'zgartirildi.

**O'zgarish:**
```python
# ESKI (OneToOneField - UNIQUE constraint)
class QRCode(models.Model):
    house = models.OneToOneField(
        House,
        on_delete=models.CASCADE,
        related_name="qr_code",  # house.qr_code
        null=True,
        blank=True
    )

# YANGI (ForeignKey - UNIQUE constraint YO'Q)
class QRCode(models.Model):
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="qr_codes",  # house.qr_codes.all()
        null=True,
        blank=True
    )
```

**Natija:**
- ✅ Bir house ko'p QR code'larga bog'lanishi mumkin
- ✅ Orphaned house_id lar muammo emas
- ✅ Random ID collision xatolari yo'q
- ✅ "Bu uy allaqachon boshqa QR kod bilan bog'langan" xatosi hal qilindi

**Migration:**
- `apps/qrcodes/migrations/0007_change_house_to_foreignkey.py`
- Production (Railway) da avtomatik apply bo'ladi `python manage.py migrate` bilan

---

## ✅ Xulosa

**3 ta POST endpoint:**
?, last_name?}` (ixtiyoriy)
   - Response: `{qr_code, user}` (user.scanned_qr_code saqlanadi)

3. **`POST /api/qrcodes/<uuid>/claim/`**
   - Headers: `Authorization: Token xxx`
   - Body: `{first_name, last_name, address, house_number, mahalla}`
   - Response: `{message, house, owner}`

---

## 📋 Backend Koddan Olingan Ma'lumotlar

### QRCodeClaimSerializer (apps/qrcodes/serializers.py)
```python
class QRCodeClaimSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)      # MAJBURIY
    last_name = serializers.CharField(max_length=100)       # MAJBURIY
    address = serializers.CharField(max_length=255)         # MAJBURIY
    house_number = serializers.CharField(max_length=50)     # MAJBURIY
    mahalla = serializers.IntegerField()                    # MAJBURIY
```

### ClaimHouseView Response (apps/qrcodes/views.py)
```python
# Success Response
{
    "message": "House claimed successfully",
    "house": {
        "id": house.id,
        "address": house.address,
        "house_number": house.house_number,
        "mahalla": mahalla.name,
        "district": mahalla.district.name,
        "region": mahalla.district.region.name,
    },
    "owner": {
        "phone": user.phone,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
}
```

### User Model Update (Claim qilishda)
```python
# User ma'lumotlari avtomatik yangilanadi:
user.first_name = validated_data["first_name"]
user.last_name = validated_data["last_name"]
user.scanned_qr_code = qr.uuid  # QR UUID saqlanadi
user.save(update_fields=["first_name", "last_name", "scanned_qr_code"])
``ken xxx`
   - Body: `{first_name, last_name}` (ixtiyoriy)
   - Response: `{qr_code, user}` (user.scanned_qr_code saqlanadi)

3. **`POST /api/qrcodes/<uuid>/claim/`**
   - Headers: `Authorization: Token xxx`
   - Body: `{address, mahalla, region?, district?}`
   - Response: `{house, qr_code}`
