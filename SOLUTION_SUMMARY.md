# 🎯 YECHIM TAYYORLANDI - Regular User Workflow

## ❌ Muammo (Rasmdagi Error)
```
POST http://192.168.0.158:8000/api/regions/mahalla/ 403 (Forbidden)
{"detail": "You do not have permission to perform this action."}
```

Regular user `/api/regions/mahalla/` ga POST qilmoqda va 403 xatosi olmoqda, chunki bu endpoint faqat admin uchun.

---

## ✅ YECHIM

### Backend O'zgarishlar:

#### 1. Yangi View: `QRScanByUUIDAPIView`
- **File:** `apps/qrcodes/views.py`
- **URL:** `GET /api/qrcodes/scan-uuid/{uuid}/`
- **Funksiya:** QR code UUID orqali house ma'lumotlarini olish
- **Permission:** `IsAuthenticated` (har qanday user)

#### 2. Yangi View: `QRCodeClaimByUUIDAPIView`
- **File:** `apps/qrcodes/views.py`
- **URL:** `POST /api/qrcodes/claim-uuid/{uuid}/`
- **Funksiya:** House claim qilish va user role ni "owner" ga o'zgartirish
- **Permission:** `IsAuthenticated` (har qanday user)

#### 3. URLs Yangilandi
- **File:** `apps/qrcodes/urls.py`
- **Qo'shildi:** 2 ta yangi URL pattern

---

## 📋 Frontend Uchun Vazifalar

### 1. Home.jsx da Conditional Rendering
```jsx
// Home.jsx
function Home() {
  const user = getCurrentUser(); // Redux yoki Context dan
  
  if (user.role === 'user') {
    // Regular user uchun SCANNER
    return <QRScanner />;
  }
  
  // Admin/Government uchun REGIONS LIST
  return <RegionsList />;
}
```

### 2. QR Scanner Component Yaratish
```jsx
// components/QRScanner.jsx
import { Html5QrcodeScanner } from 'html5-qrcode';

function QRScanner() {
  const [scanResult, setScanResult] = useState(null);
  
  useEffect(() => {
    const scanner = new Html5QrcodeScanner("reader", { 
      fps: 10, 
      qrbox: 250 
    });
    
    scanner.render(
      async (decodedUUID) => {
        // UUID olindi (masalan: "abc123def456")
        await handleScan(decodedUUID);
      },
      (error) => console.warn(error)
    );
    
    return () => scanner.clear();
  }, []);
  
  const handleScan = async (uuid) => {
    try {
      const response = await fetch(
        `http://192.168.0.158:8000/api/qrcodes/scan-uuid/${uuid}/`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${getToken()}`,
          }
        }
      );
      
      const data = await response.json();
      setScanResult(data);
    } catch (error) {
      console.error(error);
    }
  };
  
  return (
    <div>
      <div id="reader"></div>
      
      {scanResult?.status === 'unclaimed' && (
        <ClaimForm uuid={scanResult.uuid} />
      )}
      
      {scanResult?.status === 'claimed' && (
        <OwnerInfo data={scanResult} />
      )}
    </div>
  );
}
```

### 3. Claim Form Component
```jsx
// components/ClaimForm.jsx
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
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        alert('✅ Muvaffaqiyatli claim qilindi!');
        // Update user role in state/context
        // Redirect to owner dashboard
      } else {
        const error = await response.json();
        alert('❌ Xatolik: ' + error.error);
      }
    } catch (error) {
      console.error(error);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <h2>Uy ma'lumotlari</h2>
      
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
      
      <textarea
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

### 4. QR Scanner Library O'rnatish
```bash
npm install html5-qrcode
# yoki
yarn add html5-qrcode
```

---

## 🔄 Workflow (Qadamma-qadam)

### Regular User uchun:

1. **Login** → Token olish
2. **Home.jsx** → Scanner ko'rsatiladi
3. **QR Code Scan** → UUID olinadi (masalan: "abc123def456")
4. **GET Request** → `/api/qrcodes/scan-uuid/abc123def456/`
5. **Response tekshirish:**
   - Agar `status: "unclaimed"` → **Claim Form ko'rsatish**
   - Agar `status: "claimed"` → **Owner ma'lumotlarini ko'rsatish**
6. **Form Submit** → `POST /api/qrcodes/claim-uuid/abc123def456/`
7. **Success** → User role "owner" ga o'zgaradi
8. **Redirect** → Owner dashboard yoki success page

---

## 🚫 Nima QILMASLIK Kerak

❌ **BU XATO:**
```javascript
// XATO - Regular user buni qila olmaydi!
POST /api/regions/mahalla/
```

✅ **BU TO'G'RI:**
```javascript
// TO'G'RI - Regular user buni qila oladi!
POST /api/qrcodes/claim-uuid/{uuid}/
```

---

## 📦 Kerakli Package lar

```json
{
  "dependencies": {
    "html5-qrcode": "^2.3.8",
    // yoki
    "react-qr-scanner": "^1.0.0"
  }
}
```

---

## 🧪 Test Qilish

### 1. Backend ishga tushirish:
```bash
cd c:\Users\VICTUS\Desktop\qr-mahalla
.\env\Scripts\activate
python manage.py runserver 192.168.0.158:8000
```

### 2. Token olish:
```bash
# Login as user
curl -X POST http://192.168.0.158:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567", "password": "yourpassword"}'
```

### 3. Test script ishga tushirish:
```bash
# Edit TOKEN in test_qr_uuid_workflow.py
python test_qr_uuid_workflow.py
```

### 4. Manual test (Postman yoki curl):
```bash
# Scan
curl http://192.168.0.158:8000/api/qrcodes/scan-uuid/abc123def456/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Claim
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

## 📚 Qo'shimcha Fayllar

1. **REGULAR_USER_WORKFLOW.md** - To'liq workflow documentation
2. **FRONTEND_INTEGRATION.md** - Frontend integratsiya guide
3. **test_qr_uuid_workflow.py** - Backend test script

---

## ✅ Checklist (Frontend Developer uchun)

- [ ] `html5-qrcode` package o'rnatildi
- [ ] `QRScanner.jsx` component yaratildi
- [ ] `ClaimForm.jsx` component yaratildi
- [ ] `Home.jsx` da conditional rendering qo'shildi
- [ ] Scan endpoint ga GET request qo'shildi
- [ ] Claim endpoint ga POST request qo'shildi
- [ ] Success/Error handling qo'shildi
- [ ] User role update qilish qo'shildi
- [ ] Test qilindi

---

## 🎉 Natija

✅ Backend to'liq tayyorlandi
✅ Yangi UUID-based endpointlar yaratildi
✅ Regular user uchun permissions to'g'rilandi
✅ Test scriptlar yaratildi
✅ Documentation yozildi

**Frontend endi `/api/qrcodes/claim-uuid/{uuid}/` ishlatishi kerak!**
