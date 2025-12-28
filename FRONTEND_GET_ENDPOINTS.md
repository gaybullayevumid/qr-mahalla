# FRONTEND GET ENDPOINTS - Qaysi ma'lumotlarni olish kerak

## 🔑 ASOSIY GET ENDPOINTLAR

### 1. **User Profile (Current User)**
```
GET /api/users/profile/
Headers: Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 5,
  "phone": "+998906252919",
  "first_name": "Muxriddin",
  "last_name": "Rustamov",
  "role": "client",
  "is_verified": true,
  "mahalla": null,
  "scanned_qr_code": "df9dd4def795439b",
  "houses": [
    {
      "id": 15,
      "address": "555",
      "house_number": "AUTO-8",
      "mahalla": "Dehqonobod",
      "district": "Farg'ona",
      "region": "Farg'ona viloyati",
      "scanned_qr_code": "c628e14b75ba4403"
    }
  ]
}
```

**Qachon ishlatish:**
- ✅ App ochilganda - user ma'lumotini olish
- ✅ Profile sahifada - user data ko'rsatish
- ✅ Login/Register dan keyin - ma'lumot yangilash

---

### 2. **Regions List (Viloyatlar)**
```
GET /api/regions/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Toshkent shahri"
  },
  {
    "id": 2,
    "name": "Andijon viloyati"
  },
  {
    "id": 5,
    "name": "Farg'ona viloyati"
  }
]
```

**Qachon ishlatish:**
- ✅ Registration/Profile edit - viloyat tanlash dropdown
- ✅ Filter/Search - viloyat bo'yicha filter

---

### 3. **Districts by Region (Tumanlar)**
```
GET /api/districts/?region={region_id}
```

**Response:**
```json
[
  {
    "id": 55,
    "name": "Farg'ona",
    "region": {
      "id": 5,
      "name": "Farg'ona viloyati"
    }
  },
  {
    "id": 56,
    "name": "Qo'qon",
    "region": {
      "id": 5,
      "name": "Farg'ona viloyati"
    }
  }
]
```

**Qachon ishlatish:**
- ✅ Viloyat tanlagandan keyin - tuman dropdown
- ✅ Cascade select (viloyat → tuman → mahalla)

---

### 4. **Mahallas by District (Mahallalar)**
```
GET /api/neighborhoods/?district={district_id}
```

**Response:**
```json
[
  {
    "id": 20,
    "name": "Dehqonobod",
    "district": {
      "id": 55,
      "name": "Farg'ona",
      "region": {
        "id": 5,
        "name": "Farg'ona viloyati"
      }
    }
  },
  {
    "id": 21,
    "name": "Yangi mahalla",
    "district": {
      "id": 55,
      "name": "Farg'ona",
      "region": {...}
    }
  }
]
```

**Qachon ishlatish:**
- ✅ Tuman tanlagandan keyin - mahalla dropdown
- ✅ House create/edit - mahalla tanlash

---

### 5. **Houses List (Uylar ro'yxati)**
```
GET /api/houses/
Headers: Authorization: Bearer {access_token}
```

**Response (Client):**
```json
[
  {
    "id": 15,
    "address": "555",
    "house_number": "AUTO-8",
    "owner": {
      "id": 5,
      "first_name": "Muxriddin",
      "last_name": "Rustamov",
      "phone": "+998906252919"
    },
    "mahalla": {
      "id": 20,
      "name": "Dehqonobod",
      "district": {
        "id": 55,
        "name": "Farg'ona",
        "region": {
          "id": 5,
          "name": "Farg'ona viloyati"
        }
      }
    }
  }
]
```

**Response (Admin/Gov/Leader - ko'proq uylar):**
```json
[
  // Barcha uylar (admin uchun)
  // Faqat o'z mahalla (leader uchun)
]
```

**Qachon ishlatish:**
- ✅ Houses list sahifasi
- ✅ Admin dashboard - barcha uylar
- ✅ Client profile - faqat o'z uylari

---

### 6. **QR Codes List (QR kodlar ro'yxati)**
```
GET /api/qrcodes/
Headers: Authorization: Bearer {access_token}
```

**Response (Client - faqat unclaimed):**
```json
[
  {
    "id": 1,
    "uuid": "df9dd4def795439b",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b",
    "image": "/media/qr_codes/df9dd4def795439b.png",
    "is_claimed": false,
    "owner": null,
    "created_at": "2025-12-28T10:30:00Z"
  }
]
```

**Response (Admin - barcha QR kodlar):**
```json
[
  {
    "id": 1,
    "uuid": "df9dd4def795439b",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b",
    "image": "/media/qr_codes/df9dd4def795439b.png",
    "is_claimed": false,
    "owner": null,
    "created_at": "2025-12-28T10:30:00Z"
  },
  {
    "id": 2,
    "uuid": "c628e14b75ba4403",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_c628e14b75ba4403",
    "image": "/media/qr_codes/c628e14b75ba4403.png",
    "is_claimed": true,
    "owner": 5,
    "created_at": "2025-12-28T09:15:00Z"
  }
]
```

**Qachon ishlatish:**
- ✅ Admin panel - barcha QR kodlarni ko'rish
- ✅ Client - unclaimed uylarni topish
- ✅ Statistics - QR code usage

---

### 7. **QR Code Detail (Bitta QR kod)**
```
GET /api/qrcodes/{uuid}/
Headers: Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 2,
  "uuid": "c628e14b75ba4403",
  "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_c628e14b75ba4403",
  "image": "/media/qr_codes/c628e14b75ba4403.png",
  "is_claimed": true,
  "owner": 5,
  "created_at": "2025-12-28T09:15:00Z"
}
```

**Qachon ishlatish:**
- ✅ QR detail page
- ✅ Download QR image

---

### 8. **QR Scan GET (Authenticated scan)**
```
GET /api/qrcodes/scan/{uuid}/
Headers: Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "status": "unclaimed",
  "message": "Bu uyning egasi yo'q. Siz claim qilishingiz mumkin.",
  "can_claim": true,
  "claim_url": "/api/qrcodes/claim/df9dd4def795439b/",
  "qr": {
    "id": 1,
    "uuid": "df9dd4def795439b",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b"
  },
  "house": {
    "id": 20,
    "address": "Dehqonobod, avtomatik yaratilgan uy",
    "house_number": "AUTO-13",
    "region": {...},
    "district": {...},
    "mahalla": {...}
  }
}
```

**Qachon ishlatish:**
- ✅ QR scan (authenticated user bilan)
- ✅ Alternative to POST /api/qrcodes/scan/

---

### 9. **Users List (Foydalanuvchilar)**
```
GET /api/users/
Headers: Authorization: Bearer {access_token}
```

**Response (Client - faqat o'zini):**
```json
[
  {
    "id": 5,
    "phone": "+998906252919",
    "first_name": "Muxriddin",
    "last_name": "Rustamov",
    "role": "client",
    "is_verified": true,
    "houses": [...]
  }
]
```

**Response (Admin - barcha userlar):**
```json
[
  {
    "id": 1,
    "phone": "+998901111111",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin",
    "is_verified": true,
    "houses": []
  },
  {
    "id": 5,
    "phone": "+998906252919",
    "first_name": "Muxriddin",
    "last_name": "Rustamov",
    "role": "client",
    "is_verified": true,
    "houses": [...]
  }
]
```

**Qachon ishlatish:**
- ✅ Admin panel - users list
- ✅ Leader - o'z mahalla userlari
- ✅ Client - faqat o'zi

---

### 10. **User Detail (Bitta user)**
```
GET /api/users/{id}/
Headers: Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 5,
  "phone": "+998906252919",
  "first_name": "Muxriddin",
  "last_name": "Rustamov",
  "role": "client",
  "is_verified": true,
  "mahalla": null,
  "houses": [...]
}
```

**Qachon ishlatish:**
- ✅ User profile page
- ✅ Admin - user detail ko'rish

---

### 11. **User Sessions (Active devices)**
```
GET /api/users/sessions/
Headers: Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "device_name": "iPhone 13",
    "device_type": "mobile",
    "ip_address": "185.12.34.56",
    "user_agent": "Mozilla/5.0...",
    "is_current": true,
    "last_activity": "2025-12-28T15:30:00Z",
    "created_at": "2025-12-28T10:00:00Z"
  },
  {
    "id": 2,
    "device_name": "Chrome on Windows",
    "device_type": "desktop",
    "ip_address": "185.12.34.57",
    "is_current": false,
    "last_activity": "2025-12-27T18:20:00Z",
    "created_at": "2025-12-27T12:00:00Z"
  }
]
```

**Qachon ishlatish:**
- ✅ Security settings - active sessions ko'rish
- ✅ Logout other devices

---

## 📊 FRONTEND WORKFLOW

### **App ochilganda:**
```javascript
1. GET /api/users/profile/ → User ma'lumotini olish
2. GET /api/regions/ → Viloyatlar dropdown uchun cache
```

### **QR scan qilganda (Telegram):**
```javascript
1. POST /api/qrcodes/scan/ → QR ma'lumotini olish
2. Agar can_claim: true → Claim button ko'rsatish
```

### **Profile sahifasida:**
```javascript
1. GET /api/users/profile/ → User + houses
2. GET /api/users/sessions/ → Active devices
```

### **Admin dashboard:**
```javascript
1. GET /api/users/ → Barcha userlar
2. GET /api/houses/ → Barcha uylar
3. GET /api/qrcodes/ → Barcha QR kodlar
4. GET /api/regions/ → Statistics uchun
```

### **Location selection (Cascade):**
```javascript
1. GET /api/regions/ → Viloyatlar
2. GET /api/districts/?region=5 → Tumanlar
3. GET /api/neighborhoods/?district=55 → Mahallalar
```

---

## 🔐 ROLE-BASED ACCESS

| Endpoint | Anonymous | Client | Leader | Admin/Gov |
|----------|-----------|--------|--------|-----------|
| GET /api/users/profile/ | ❌ | ✅ O'zi | ✅ O'zi | ✅ O'zi |
| GET /api/users/ | ❌ | ✅ O'zi | ✅ Mahalla | ✅ Barchasi |
| GET /api/houses/ | ❌ | ✅ O'zi | ✅ Mahalla | ✅ Barchasi |
| GET /api/qrcodes/ | ❌ | ✅ Unclaimed | ✅ Mahalla | ✅ Barchasi |
| GET /api/regions/ | ✅ | ✅ | ✅ | ✅ |
| GET /api/districts/ | ✅ | ✅ | ✅ | ✅ |
| GET /api/neighborhoods/ | ✅ | ✅ | ✅ | ✅ |
| GET /api/users/sessions/ | ❌ | ✅ O'zi | ✅ O'zi | ✅ O'zi |

---

## ⚡ OPTIMIZATION TIPS

1. **Cache static data:**
   - Regions, Districts, Mahallas - local storage ga saqlash
   - Har safar request qilmaslik

2. **Prefetch user data:**
   - App load → GET /api/users/profile/
   - Background da yangilash

3. **Lazy load:**
   - Users list, Houses list - pagination ishlatish
   - Scroll qilganda keyingi sahifa

4. **Websocket (optional):**
   - Real-time QR scan notifications
   - House claim notifications
