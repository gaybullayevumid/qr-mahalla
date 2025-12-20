# QR Code System - Optimized Workflow

## 🎯 Tizim Ma'lumotlari

**Optimallashtirilgan sana:** 2025-12-20  
**Versiya:** 2.0

## 📋 Asosiy Workflow

### 1. Super Admin - QR Code Yaratish
```
POST /api/qrcodes/create/
Headers: Authorization: Bearer <admin_token>
Body: {
    "house": 123
}

Response: {
    "id": 1,
    "uuid": "a1b2c3d4e5f67890",
    "image": "/media/qr_codes/a1b2c3d4e5f67890.png",
    "is_claimed": false,
    "created_at": "2025-12-20T10:00:00Z"
}
```

### 2. User - Telefon Orqali Auth
```
POST /api/users/auth/
Body: {
    "phone": "+998901234567"
}

Response: {
    "message": "SMS code sent",
    "step": "verify"
}

POST /api/users/auth/
Body: {
    "phone": "+998901234567",
    "code": "123456"
}

Response: {
    "access": "eyJ0eXAi...",
    "refresh": "eyJ0eXAi...",
    "user": {
        "id": 1,
        "phone": "+998901234567",
        "role": "user"
    }
}
```

### 3. User - QR Code Skanerlash
```
GET /api/qrcodes/scan/<uuid>/
Headers: Authorization: Bearer <user_token>

# Agar uy claim qilinmagan bo'lsa:
Response: {
    "status": "unclaimed",
    "message": "This house has no owner yet. You can claim it.",
    "qr": {
        "id": 1,
        "uuid": "a1b2c3d4e5f67890"
    },
    "house": {
        "address": "Chilonzor 12-mavze",
        "number": "25",
        "region": {
            "id": 1,
            "name": "Toshkent"
        },
        "district": {
            "id": 5,
            "name": "Chilonzor"
        },
        "mahalla": {
            "id": 12,
            "name": "Qatortol"
        }
    }
}

# Agar uy claim qilingan bo'lsa:
Response: {
    "status": "claimed",
    "owner": {
        "first_name": "Anvar",
        "last_name": "Mahmudov",
        "phone": "+998901234567"
        # Admin uchun yana passport_id va address ham keladi
    },
    "house": {
        "address": "Chilonzor 12-mavze",
        "number": "25",
        "region": {...},
        "district": {...},
        "mahalla": {...}
    }
}
```

### 4. User - Uyni Claim Qilish
```
POST /api/qrcodes/claim/<uuid>/
Headers: Authorization: Bearer <user_token>
Body: {
    "first_name": "Anvar",
    "last_name": "Mahmudov",
    "passport_id": "AA1234567",
    "address": "Toshkent, Chilonzor 12"
}

Response: {
    "message": "House claimed successfully",
    "house": {
        "id": 123,
        "address": "Chilonzor 12-mavze",
        "number": "25",
        "mahalla": "Qatortol"
    },
    "owner": {
        "phone": "+998901234567",
        "first_name": "Anvar",
        "last_name": "Mahmudov"
    },
    "qr": {
        "id": 1,
        "uuid": "a1b2c3d4e5f67890"
    }
}
```

### 5. Keyingi Skanerlashlar
Claim qilingan uyni qayta skanerlasangiz, role asosida ma'lumotlar ko'rsatiladi:
- **Regular user**: Faqat ism, familiya, telefon
- **Owner/Admin**: Barcha ma'lumotlar (passport, address)

## 🔗 API Endpoints

### QR Code Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/qrcodes/` | QR kodlar ro'yxati | All authenticated |
| POST | `/api/qrcodes/create/` | Yangi QR yaratish | Admin only |
| GET | `/api/qrcodes/<uuid>/` | QR details | Role-based |
| GET | `/api/qrcodes/scan/<uuid>/` | QR skanerlash | All authenticated |
| POST | `/api/qrcodes/claim/<uuid>/` | Uyni claim qilish | Regular users |

### House Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/houses/houses/` | Uylar ro'yxati | Role-based |
| POST | `/api/houses/houses/` | Yangi uy yaratish | Admin only |
| GET | `/api/houses/houses/<id>/` | Uy details | Role-based |
| PUT/PATCH | `/api/houses/houses/<id>/` | Uyni tahrirlash | Admin/Owner |
| DELETE | `/api/houses/houses/<id>/` | Uyni o'chirish | Admin only |

## 👥 Role-based Access

### Regular User (user)
- QR kod skanerlashi mumkin
- Claim qilinmagan uylarni ko'rishi va claim qilishi mumkin
- Claim qilingan uylarda faqat public ma'lumotlarni ko'rishi mumkin

### House Owner (owner) 
- O'z uyining barcha ma'lumotlarini ko'rishi mumkin
- Boshqa uylarni skanlashda private ma'lumotlarni ko'rishi mumkin
- O'z uyini tahrirlashi mumkin

### Mahalla Admin (mahalla_admin)
- O'z mahallasidagi barcha uylarni ko'rishi mumkin
- Barcha private ma'lumotlarni ko'rishi mumkin
- Tahrirlash imkoniyati

### Government/Super Admin
- Barcha uylarni ko'rishi va boshqarishi mumkin
- To'liq access

## 🎨 Optimallashtirilgan Qismlar

### ✅ O'chirilgan Funksiyalar:
1. **Delivery tracking** - is_delivered, delivered_at, delivered_by
2. **Duplicate endpoints** - Barcha duplicate scan/claim endpointlar
3. **Takroriy kod** - Response formatlash uchun helper funksiyalar yaratildi

### ✅ Yaxshilangan Qismlar:
1. **Clean URLs** - UUID-based, RESTful endpoints
2. **Helper Functions** - `_get_location_data()`, `_get_owner_data()`
3. **Optimized Queries** - `select_related()` to'g'ri ishlatilgan
4. **Consistent Responses** - Barcha responselar bir xil struktura
5. **Better Naming** - Professional view nomlari

### ✅ Yangi Struktura:

**Views:**
- `ScanQRCodeView` - Scan endpoint
- `ClaimHouseView` - Claim endpoint  
- `QRCodeListAPIView` - List view
- `QRCodeCreateAPIView` - Create view
- `QRCodeDetailAPIView` - Detail view

**Serializers:**
- `QRCodeSerializer` - Basic info
- `QRCodeCreateSerializer` - Creation
- `QRCodeClaimSerializer` - Claiming

## 📊 Database Changes

Migration yaratildi va apply qilindi:
```
apps/qrcodes/migrations/0004_remove_qrcode_delivered_at_and_more.py
- Remove field delivered_at from qrcode
- Remove field delivered_by from qrcode
- Remove field is_delivered from qrcode
```

## 🚀 Frontend Integration

### QR Scanner Integratsiya:
1. User login qiladi (SMS auth)
2. QR scanner ochiladi  
3. QR scan qilinadi, UUID olinadi
4. `GET /api/qrcodes/scan/<uuid>/` ga so'rov yuboriladi
5. Agar unclaimed -> claim formasi ko'rsatiladi
6. User ma'lumotlarini kiritadi
7. `POST /api/qrcodes/claim/<uuid>/` ga yuboriladi
8. Success - user role "owner" ga o'zgaradi

## 💡 Best Practices

1. **Har doim UUID ishlating** - ID emas, UUID
2. **Role-based access** - Har bir foydalanuvchi o'z rolida ko'rishidan ko'p ma'lumot ko'rmaydi
3. **Scan logging** - Har bir scan ScanLog'ga yoziladi
4. **Atomic operations** - Claim qilishda user va house bir vaqtda yangilanadi
5. **Error handling** - To'g'ri error messagelar qaytaradi

## 🎯 Next Steps

Frontend uchun tavsiyalar:
1. QR scanner library integratsiya qiling (react-qr-reader)
2. Scan natijasi bo'yicha conditional rendering
3. Claim form validation
4. Success/error toast notifications
5. User session management (refresh tokens)
