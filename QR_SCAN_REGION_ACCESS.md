# ✅ REGULAR USER GA REGION, TUMAN, MAHALLA RUXSATI BERILDI

## 🎯 O'zgarishlar

### QR Code Scan Response ga ID va Name Qo'shildi

Endi QR code scan qilinganda, response da region, tuman va mahalla ham **ID** ham **name** bilan qaytadi:

---

## 📝 Yangi Response Format

### 1. Unclaimed House (Owner yo'q)

**Request:**
```bash
GET /api/qrcodes/scan-uuid/{uuid}/
```

**Response:**
```json
{
  "status": "unclaimed",
  "is_claimed": false,
  "can_claim": true,
  "message": "This house has no owner yet. You can claim it.",
  "qr_id": 1,
  "uuid": "abc123def456",
  "claim_url": "/api/qrcodes/claim-uuid/abc123def456/",
  "house_address": "Toshkent ko'chasi 123",
  "house_number": "123",
  "region": {
    "id": 1,
    "name": "Toshkent shahar"
  },
  "district": {
    "id": 5,
    "name": "Chilonzor tumani"
  },
  "mahalla": {
    "id": 25,
    "name": "Chilonzor MFY"
  }
}
```

### 2. Claimed House - Regular User

**Request:**
```bash
GET /api/qrcodes/scan-uuid/{uuid}/
Authorization: Bearer {token}  # role: user
```

**Response:**
```json
{
  "status": "claimed",
  "is_claimed": true,
  "can_claim": false,
  "first_name": "Alisher",
  "last_name": "Navoiy",
  "phone": "+998901234567",
  "house_address": "Toshkent ko'chasi 123",
  "region": {
    "id": 1,
    "name": "Toshkent shahar"
  },
  "district": {
    "id": 5,
    "name": "Chilonzor tumani"
  },
  "mahalla": {
    "id": 25,
    "name": "Chilonzor MFY"
  }
}
```

### 3. Claimed House - Owner

**Response:**
```json
{
  "status": "claimed",
  "is_claimed": true,
  "can_claim": false,
  "first_name": "Alisher",
  "last_name": "Navoiy",
  "phone": "+998901234567",
  "passport_id": "AA1234567",
  "address": "Toshkent, Mirobod tumani",
  "house_address": "Toshkent ko'chasi 123",
  "region": {
    "id": 1,
    "name": "Toshkent shahar"
  },
  "district": {
    "id": 5,
    "name": "Chilonzor tumani"
  },
  "mahalla": {
    "id": 25,
    "name": "Chilonzor MFY"
  }
}
```

---

## 🔗 Region/Tuman/Mahalla Ma'lumotlarini Olish

Regular user endi region, tuman, mahalla ID laridan foydalanib, batafsil ma'lumotlarni olishi mumkin:

### 1. Region Detail
```bash
GET /api/regions/regions/{region_id}/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 1,
  "name": "Toshkent shahar",
  "districts": [
    {
      "id": 5,
      "name": "Chilonzor tumani",
      "mahallas": [
        {
          "id": 25,
          "name": "Chilonzor MFY",
          "admin": {
            "phone": "+998909999999",
            "first_name": "Mahalla",
            "last_name": "Admin"
          }
        }
      ]
    }
  ]
}
```

### 2. District Detail
```bash
GET /api/regions/districts/{district_id}/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 5,
  "name": "Chilonzor tumani",
  "region": {
    "id": 1,
    "name": "Toshkent shahar"
  },
  "mahallas": [...]
}
```

### 3. Mahalla Detail
```bash
GET /api/regions/mahallas/{mahalla_id}/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 25,
  "name": "Chilonzor MFY",
  "district": {
    "id": 5,
    "name": "Chilonzor tumani"
  },
  "admin": {
    "phone": "+998909999999",
    "first_name": "Mahalla",
    "last_name": "Admin"
  }
}
```

### 4. Barcha Regionlar
```bash
GET /api/regions/regions/
Authorization: Bearer {token}
```

### 5. Barcha Tumanlar
```bash
GET /api/regions/districts/
Authorization: Bearer {token}
```

### 6. Barcha Mahallalar
```bash
GET /api/regions/mahallas/
Authorization: Bearer {token}
```

---

## 🔒 Permissions

| Endpoint | Method | Regular User | Owner | Admin |
|----------|--------|--------------|-------|-------|
| `/api/regions/regions/` | GET | ✅ | ✅ | ✅ |
| `/api/regions/regions/{id}/` | GET | ✅ | ✅ | ✅ |
| `/api/regions/districts/` | GET | ✅ | ✅ | ✅ |
| `/api/regions/districts/{id}/` | GET | ✅ | ✅ | ✅ |
| `/api/regions/mahallas/` | GET | ✅ | ✅ | ✅ |
| `/api/regions/mahallas/{id}/` | GET | ✅ | ✅ | ✅ |
| POST/PUT/DELETE | ❌ | ❌ | ✅ |

**Regular user faqat GET (read) qila oladi, POST/PUT/DELETE qila olmaydi!**

---

## 💻 Frontend Integration

### React Example

```javascript
// QR code scan qilingandan keyin
const scanResult = await fetch(`/api/qrcodes/scan-uuid/${uuid}/`, {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Region, tuman, mahalla ma'lumotlari
console.log(scanResult.region);    // { id: 1, name: "Toshkent shahar" }
console.log(scanResult.district);  // { id: 5, name: "Chilonzor tumani" }
console.log(scanResult.mahalla);   // { id: 25, name: "Chilonzor MFY" }

// Batafsil ma'lumot olish (agar kerak bo'lsa)
const regionDetail = await fetch(
  `/api/regions/regions/${scanResult.region.id}/`,
  { headers: { 'Authorization': `Bearer ${token}` } }
).then(r => r.json());

// Mahalla admin ma'lumotlarini olish
const mahallaDetail = await fetch(
  `/api/regions/mahallas/${scanResult.mahalla.id}/`,
  { headers: { 'Authorization': `Bearer ${token}` } }
).then(r => r.json());

console.log('Mahalla admin:', mahallaDetail.admin);
```

---

## 🧪 Test Qilish

### 1. QR Scan Test
```bash
# Regular user token bilan
curl http://192.168.0.158:8000/api/qrcodes/scan-uuid/abc123def456/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "status": "claimed",
  "region": { "id": 1, "name": "..." },
  "district": { "id": 5, "name": "..." },
  "mahalla": { "id": 25, "name": "..." }
}
```

### 2. Region Detail Test
```bash
curl http://192.168.0.158:8000/api/regions/regions/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Mahalla Detail Test
```bash
curl http://192.168.0.158:8000/api/regions/mahallas/25/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Afzalliklar

1. ✅ **ID va Name** - Ikkala ma'lumot ham qaytadi
2. ✅ **Detailed Access** - Regular user batafsil ma'lumot olishi mumkin
3. ✅ **Read-Only** - Regular user faqat GET qila oladi
4. ✅ **Structured Data** - Ma'lumotlar object sifatida qaytadi
5. ✅ **Easy Frontend Integration** - ID orqali boshqa ma'lumotlar olish oson

---

## 📊 Response Structure

### Avval (Old):
```json
{
  "region": "Toshkent shahar",        // Faqat name
  "district": "Chilonzor tumani",     // Faqat name
  "mahalla": "Chilonzor MFY"          // Faqat name
}
```

### Endi (New):
```json
{
  "region": {
    "id": 1,                           // ✅ ID qo'shildi
    "name": "Toshkent shahar"
  },
  "district": {
    "id": 5,
    "name": "Chilonzor tumani"
  },
  "mahalla": {
    "id": 25,
    "name": "Chilonzor MFY"
  }
}
```

---

## ⚠️ Important Notes

1. **Read-Only Access** - Regular user POST/PUT/DELETE qila olmaydi
2. **Authenticated Only** - Token kerak
3. **All Endpoints** - Barcha scan endpointlarda yangilandi:
   - `/api/qrcodes/scan/{id}/`
   - `/api/qrcodes/scan-uuid/{uuid}/`
4. **Consistent Format** - Barcha role lar uchun bir xil format

---

## ✅ Summary

✅ QR code scan qilinganda region, tuman, mahalla ID va name qaytadi
✅ Regular user region/tuman/mahalla detail larini GET qila oladi
✅ Regular user faqat read-only access (GET)
✅ Response structured (object format)
✅ Frontend uchun oson integratsiya

**Regular userga region, tuman, mahalla ruxsati berildi!** 🎉
