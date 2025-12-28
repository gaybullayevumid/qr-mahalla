# YANGI WORKFLOW - QR CODE CLAIM SYSTEM

## 🔄 YANGI WORKFLOW

### **Eski workflow:**
```
1. Admin House yaratadi
2. QRCode avtomatik yaratiladi
3. User QR scan qiladi
4. User claim qiladi (faqat ism, familiya)
```

### **Yangi workflow:**
```
1. Admin bo'sh QR kodlar yaratadi (house yo'q)
2. User QR scan qiladi
3. User uy ma'lumotlarini kiritadi (forma)
4. Backend yangi House yaratadi va QR ga bog'laydi
```

---

## 📝 BO'SH QR KODLAR YARATISH

### **Script ishga tushirish:**
```bash
python create_empty_qr.py
```

**Nima qiladi:**
- Bo'sh QR kodlar yaratadi (house=None)
- Har birida UUID va Telegram URL bor
- QR image avtomatik generate qilinadi

**Namuna:**
```
UUID: a1b2c3d4e5f6g7h8
URL: https://t.me/qrmahallabot/start?startapp=QR_KEY_a1b2c3d4e5f6g7h8
House: NULL (bo'sh)
```

---

## 📱 FRONTEND WORKFLOW

### **1. QR Scan (bo'sh QR kod):**

**Request:**
```
POST /api/qrcodes/scan/
Body: {
  "url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_a1b2c3d4e5f6g7h8"
}
```

**Response (bo'sh QR):**
```json
{
  "status": "unclaimed",
  "message": "Bu QR kod hali biriktirilmagan. Siz uyingiz ma'lumotlarini kiritib claim qilishingiz mumkin.",
  "qr": {
    "id": 25,
    "uuid": "a1b2c3d4e5f6g7h8",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_a1b2c3d4e5f6g7h8"
  },
  "house": null,  ← Bo'sh!
  "owner": null,
  "can_claim": true,
  "claim_url": "/api/qrcodes/claim/a1b2c3d4e5f6g7h8/"
}
```

### **2. Claim Form (user uy ma'lumotini kiritadi):**

**Frontend form:**
```javascript
const claimForm = {
  // User ma'lumoti
  first_name: "Aziz",
  last_name: "Ahmadov",
  
  // Uy ma'lumoti (YANGI!)
  address: "Qatortol ko'chasi, 45-uy",
  house_number: "45",
  mahalla: 1  // Mahalla ID
}
```

**Request:**
```
POST /api/qrcodes/claim/a1b2c3d4e5f6g7h8/
Headers: Authorization: Bearer {token}
Body: {
  "first_name": "Aziz",
  "last_name": "Ahmadov",
  "address": "Qatortol ko'chasi, 45-uy",
  "house_number": "45",
  "mahalla": 1
}
```

**Response:**
```json
{
  "message": "House claimed successfully",
  "house": {
    "id": 35,  ← Yangi yaratilgan!
    "address": "Qatortol ko'chasi, 45-uy",
    "number": "45",
    "mahalla": "Qatortol",
    "district": "Chilonzor",
    "region": "Toshkent shahri"
  },
  "owner": {
    "phone": "+998901234567",
    "first_name": "Aziz",
    "last_name": "Ahmadov",
    "role": "client"
  },
  "qr": {
    "id": 25,
    "uuid": "a1b2c3d4e5f6g7h8",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_a1b2c3d4e5f6g7h8"
  }
}
```

---

## 🎨 FRONTEND FORM EXAMPLE

### **React/Vue/Telegram Mini App:**

```javascript
// 1. QR scan qilgandan keyin
const scanResponse = await scanQR(qrUrl);

if (scanResponse.status === "unclaimed" && !scanResponse.house) {
  // Bo'sh QR - formani ko'rsatish
  showClaimForm(scanResponse.qr.uuid);
}

// 2. Claim form
function ClaimForm({ qrUuid }) {
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    address: "",
    house_number: "",
    mahalla: null
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const response = await fetch(`/api/qrcodes/claim/${qrUuid}/`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(formData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showSuccess("Uy muvaffaqiyatli biriktirildi!");
      navigateToHouse(data.house);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Uy ma'lumotlarini kiriting</h2>
      
      <input
        type="text"
        placeholder="Ism"
        value={formData.first_name}
        onChange={(e) => setFormData({...formData, first_name: e.target.value})}
      />
      
      <input
        type="text"
        placeholder="Familiya"
        value={formData.last_name}
        onChange={(e) => setFormData({...formData, last_name: e.target.value})}
      />
      
      <input
        type="text"
        placeholder="Manzil (masalan: Qatortol ko'chasi, 45-uy)"
        value={formData.address}
        onChange={(e) => setFormData({...formData, address: e.target.value})}
      />
      
      <input
        type="text"
        placeholder="Uy raqami (masalan: 45)"
        value={formData.house_number}
        onChange={(e) => setFormData({...formData, house_number: e.target.value})}
      />
      
      {/* Cascade select: Region → District → Mahalla */}
      <RegionDistrictMahallaSelect 
        onSelect={(mahallaId) => setFormData({...formData, mahalla: mahallaId})}
      />
      
      <button type="submit">Uyni biriktirish</button>
    </form>
  );
}
```

---

## 🔐 VALIDATION

Backend quyidagilarni tekshiradi:

1. ✅ QR kod mavjudmi
2. ✅ QR kod allaqachon claimed emasligi
3. ✅ User authenticated
4. ✅ Mahalla ID to'g'riligi
5. ✅ Barcha required fieldlar mavjudligi

**Error responses:**
```json
// QR topilmadi
{
  "error": "QR code not found"
}

// Allaqachon claimed
{
  "error": "This house is already claimed"
}

// Mahalla topilmadi
{
  "error": "Mahalla not found"
}

// Validation error
{
  "first_name": ["This field is required."],
  "mahalla": ["This field is required."]
}
```

---

## 📊 ADMIN PANEL

### **Bo'sh QR kodlarni ko'rish:**
```
GET /api/qrcodes/
```

**Filter:**
```
GET /api/qrcodes/?house__isnull=true  → Bo'sh QR kodlar
GET /api/qrcodes/?house__isnull=false → House bor QR kodlar
```

---

## ✅ MIGRATION O'TKAZILDI

```python
# apps/qrcodes/models.py
house = models.OneToOneField(
    House,
    null=True,      ← Yangi!
    blank=True,     ← Yangi!
    on_delete=models.CASCADE
)
```

**Database migration:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🎯 ASOSIY FARQLAR

| Eski | Yangi |
|------|-------|
| Admin House yaratadi | Admin bo'sh QR yaratadi |
| QR avtomatik yaratiladi | QR oldindan yaratilgan |
| User faqat ism/familiya kiritadi | User uy ma'lumotini ham kiritadi |
| House allaqachon bor | House claim paytida yaratiladi |

---

## 🚀 DEPLOYMENT

1. **Bo'sh QR kodlar yaratish:**
   ```bash
   python create_empty_qr.py
   # Masalan: 1000 ta
   ```

2. **Frontend ga API document berish**

3. **User claim form sozlash**

4. **Mahalla selection cascade qo'shish:**
   - GET /api/regions/
   - GET /api/districts/?region=X
   - GET /api/neighborhoods/?district=Y

---

## 📝 FRONTEND CHECKLIST

- [ ] QR scan response da `house: null` ni handle qilish
- [ ] Claim form yaratish (ism, familiya, address, house_number, mahalla)
- [ ] Cascade select (Region → District → Mahalla)
- [ ] Form validation
- [ ] Success/Error messages
- [ ] Claimed house detail page ga o'tish
