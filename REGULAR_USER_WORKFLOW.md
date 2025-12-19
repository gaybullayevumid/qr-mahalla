# ✅ REGULAR USER WORKFLOW - TO'LIQ SOZLANDI

## 📝 Muammo va Yechim

### ❌ Avvalgi Muammo:
Regular user `/api/regions/mahalla/` ga POST so'rov yuborayotgan edi va 403 Forbidden xatosi olayotgan edi, chunki bu endpoint faqat admin va government uchun.

### ✅ Yechim:
Yangi UUID-based endpointlar yaratildi va regular user uchun to'liq workflow sozlandi.

---

## 🔧 Backend O'zgarishlar

### Yangi Endpointlar:

1. **QR Code Skanerlash (UUID bilan)**
   - URL: `GET /api/qrcodes/scan-uuid/{uuid}/`
   - File: `apps/qrcodes/views.py` → `QRScanByUUIDAPIView`
   - Funksiya: QR code UUID orqali house ma'lumotlarini olish

2. **House Claim qilish (UUID bilan)**
   - URL: `POST /api/qrcodes/claim-uuid/{uuid}/`
   - File: `apps/qrcodes/views.py` → `QRCodeClaimByUUIDAPIView`
   - Funksiya: User ma'lumotlarini saqlash va house ga biriktirish

### O'zgartirilgan Fayllar:
- ✅ `apps/qrcodes/views.py` - 2 ta yangi view qo'shildi
- ✅ `apps/qrcodes/urls.py` - 2 ta yangi URL pattern qo'shildi

---

## 🎯 Regular User Workflow

### 1. User Login qiladi
```
POST /api/users/login/
Body: { "phone": "+998901234567", "password": "..." }
Response: { "token": "...", "user": { "role": "user", ... } }
```

### 2. Home.jsx Scanner ko'rsatadi
- Agar `user.role === 'user'` bo'lsa, Scanner component render qilinadi
- Admin/Government uchun Region list ko'rsatiladi

### 3. QR Code Skanerlash
```javascript
// Scanner.jsx
const scannedUUID = "abc123def456"; // QR code dan

// Backend ga request
GET /api/qrcodes/scan-uuid/abc123def456/
Headers: { "Authorization": "Bearer TOKEN" }
```

**Response (Unclaimed House):**
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
  "house_number": "123"
}
```

**Response (Claimed House):**
```json
{
  "status": "claimed",
  "is_claimed": true,
  "can_claim": false,
  "first_name": "Alisher",
  "last_name": "Navoiy",
  "phone": "+998901234567",
  "house_address": "Toshkent ko'chasi 123",
  "mahalla": "Chilonzor"
}
```

### 4. Form Ko'rsatish (Agar Unclaimed bo'lsa)
```jsx
// ClaimForm.jsx
<form onSubmit={handleClaimSubmit}>
  <input name="first_name" placeholder="Ism" required />
  <input name="last_name" placeholder="Familiya" required />
  <input name="passport_id" placeholder="Pasport seriyasi" required />
  <input name="address" placeholder="Manzil" required />
  <button type="submit">Tasdiqlash</button>
</form>
```

### 5. Claim qilish
```javascript
// ClaimForm.jsx - onSubmit
POST /api/qrcodes/claim-uuid/abc123def456/
Headers: { "Authorization": "Bearer TOKEN" }
Body: {
  "first_name": "Alisher",
  "last_name": "Navoiy",
  "passport_id": "AA1234567",
  "address": "Toshkent, Mirobod tumani, Buyuk Ipak Yo'li 123"
}
```

**Success Response:**
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

### 6. User Role O'zgaradi
- User role avtomatik `"user"` dan `"owner"` ga o'zgaradi
- House user ga biriktiriladi
- Scan log yaratiladi

---

## 🚀 Frontend Integration

### Component Structure:
```
App
└── Home.jsx
    ├── if (user.role === 'user')
    │   └── <QRScanner />
    │       ├── onScan(uuid)
    │       │   └── GET /api/qrcodes/scan-uuid/{uuid}/
    │       ├── if (response.status === 'unclaimed')
    │       │   └── <ClaimForm uuid={uuid} />
    │       │       └── POST /api/qrcodes/claim-uuid/{uuid}/
    │       └── if (response.status === 'claimed')
    │           └── <OwnerInfo data={response} />
    └── else (admin/government)
        └── <RegionsList />
```

### Example Code:

#### Scanner.jsx
```jsx
import React, { useState } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';

function QRScanner() {
  const [scanResult, setScanResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const onScan = async (uuid) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://192.168.0.158:8000/api/qrcodes/scan-uuid/${uuid}/`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          }
        }
      );
      
      const data = await response.json();
      setScanResult(data);
      
      if (data.status === 'unclaimed') {
        // Show claim form
      } else {
        // Show owner info
      }
    } catch (error) {
      console.error('Scan error:', error);
    } finally {
      setLoading(false);
    }
  };

  // ... QR scanner setup

  return (
    <div>
      {loading && <p>Loading...</p>}
      {scanResult && scanResult.status === 'unclaimed' && (
        <ClaimForm uuid={scanResult.uuid} />
      )}
      {scanResult && scanResult.status === 'claimed' && (
        <OwnerInfo data={scanResult} />
      )}
    </div>
  );
}
```

#### ClaimForm.jsx
```jsx
import React, { useState } from 'react';

function ClaimForm({ uuid }) {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    passport_id: '',
    address: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(
        `http://192.168.0.158:8000/api/qrcodes/claim-uuid/${uuid}/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        }
      );
      
      const data = await response.json();
      
      if (response.ok) {
        alert('Muvaffaqiyatli claim qilindi!');
        // Redirect or update UI
      } else {
        alert('Xatolik: ' + data.error);
      }
    } catch (error) {
      console.error('Claim error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Ism"
        value={formData.first_name}
        onChange={(e) => setFormData({...formData, first_name: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="Familiya"
        value={formData.last_name}
        onChange={(e) => setFormData({...formData, last_name: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="Pasport seriyasi (AA1234567)"
        value={formData.passport_id}
        onChange={(e) => setFormData({...formData, passport_id: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="Manzil"
        value={formData.address}
        onChange={(e) => setFormData({...formData, address: e.target.value})}
        required
      />
      <button type="submit">Tasdiqlash</button>
    </form>
  );
}
```

---

## 📦 QR Scanner Library

React uchun QR scanner library:

### Option 1: html5-qrcode
```bash
npm install html5-qrcode
```

```jsx
import { Html5QrcodeScanner } from 'html5-qrcode';

useEffect(() => {
  const scanner = new Html5QrcodeScanner(
    "reader",
    { fps: 10, qrbox: 250 }
  );
  
  scanner.render(
    (decodedText) => {
      // decodedText is the UUID
      onScan(decodedText);
    },
    (error) => {
      console.warn(error);
    }
  );
  
  return () => scanner.clear();
}, []);

return <div id="reader"></div>;
```

### Option 2: react-qr-scanner
```bash
npm install react-qr-scanner
```

```jsx
import QrScanner from 'react-qr-scanner';

<QrScanner
  delay={300}
  onError={(error) => console.error(error)}
  onScan={(data) => {
    if (data) {
      onScan(data.text); // UUID
    }
  }}
  style={{ width: '100%' }}
/>
```

---

## 🧪 Testing

### 1. Backend Test
```bash
cd c:\Users\VICTUS\Desktop\qr-mahalla
.\env\Scripts\activate
python manage.py runserver 192.168.0.158:8000
```

### 2. Get Token
```bash
# Login as regular user
curl -X POST http://192.168.0.158:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567", "password": "password"}'
```

### 3. Run Test Script
```bash
# Edit test_qr_uuid_workflow.py and set TOKEN
python test_qr_uuid_workflow.py
```

### 4. Manual Test
```bash
# Get unclaimed QR code UUID from admin panel or database
# Then test scan
curl -X GET http://192.168.0.158:8000/api/qrcodes/scan-uuid/abc123def456/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test claim
curl -X POST http://192.168.0.158:8000/api/qrcodes/claim-uuid/abc123def456/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alisher",
    "last_name": "Navoiy",
    "passport_id": "AA1234567",
    "address": "Toshkent, Mirobod tumani"
  }'
```

---

## 🔒 Permissions

| Endpoint | Regular User | Owner | Mahalla Admin | Government | Super Admin |
|----------|-------------|-------|---------------|------------|-------------|
| `GET /api/qrcodes/scan-uuid/{uuid}/` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `POST /api/qrcodes/claim-uuid/{uuid}/` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `POST /api/regions/mahalla/` | ❌ | ❌ | ✅ | ✅ | ✅ |

---

## ⚠️ Important Notes

1. **UUID vs ID**: 
   - QR code da UUID bor (masalan: "abc123def456")
   - ID integer (masalan: 1, 2, 3)
   - UUID bilan scan qilish kerak!

2. **Permissions**:
   - Regular user `/api/regions/mahalla/` ga POST qila olmaydi
   - Regular user faqat `/api/qrcodes/claim-uuid/` ishlatadi

3. **Role Change**:
   - Claim qilingandan keyin user role "owner" ga o'zgaradi
   - Keyin user o'zining house ma'lumotlarini ko'ra oladi

4. **One House Per QR**:
   - Har bir house uchun bitta QR code
   - QR code house bilan OneToOne relationship

5. **Security**:
   - Barcha endpointlar authentication talab qiladi
   - Token bilan request yuborish kerak

---

## 📞 Help

Agar muammo bo'lsa:
1. Backend loglarini tekshiring
2. Frontend console loglarini tekshiring
3. Network tab da request/response ni ko'ring
4. Token to'g'ri yuborilayotganini tekshiring
5. UUID to'g'ri ekanligini tekshiring

---

## ✅ Summary

Backend tayyorlandi va ishlaydi! Endi frontend quyidagilarni qilishi kerak:

1. ✅ Regular user uchun Scanner ko'rsatish (Home.jsx)
2. ✅ QR code UUID ni olish
3. ✅ `GET /api/qrcodes/scan-uuid/{uuid}/` ga request
4. ✅ Agar unclaimed: ClaimForm ko'rsatish
5. ✅ Form submit: `POST /api/qrcodes/claim-uuid/{uuid}/`
6. ✅ Success: Owner info ko'rsatish

**Frontend da faqat `/api/qrcodes/claim-uuid/{uuid}/` ishlatish kerak, `/api/regions/mahalla/` emas!**
