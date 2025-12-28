# QR CODE URL INTEGRATSIYASI - Telegram Bot bilan

## 🎯 QR KOD QANDAY ISHLAYDI

### 1. **QR Kod yaratilganda:**

```python
# apps/qrcodes/models.py - generate_qr_image()

# UUID yaratiladi
uuid = "df9dd4def795439b"

# Telegram bot URL tuziladi
qr_url = f"https://t.me/qrmahallabot/start?startapp=QR_KEY_{uuid}"
# Natija: https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b

# Bu URL QR code rasmiga encode qilinadi
qr_code_image.add_data(qr_url)  # QR rasmga URL yoziladi
qr_code_image.save("df9dd4def795439b.png")
```

**Demak QR kod rasmi ichida Telegram URL yozilgan!**

---

## 📱 TELEFON KAMERASIDAN SCAN QILISH

### **1. User telefon kamerasini ochadi**
```
📸 Kamera → QR rasm scan → URL o'qiladi
```

### **2. Telefon avtomatik ochadi:**
```
https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b
                                        └─────── Bu UUID
```

### **3. Telegram bot ochiladi:**
```
Telegram app → @qrmahallabot botni ochadi
              → startapp parametrini uzatadi: "QR_KEY_df9dd4def795439b"
```

---

## 🔄 FRONTEND (Telegram Mini App) QABUL QILADI

### **JavaScript kod (Telegram WebApp):**

```javascript
// Telegram WebApp API dan start parametrini olish
const initData = window.Telegram.WebApp.initDataUnsafe;
const startParam = initData.start_param;

console.log(startParam);
// Output: "QR_KEY_df9dd4def795439b"

// To'liq URL ni tuzish
const fullUrl = `https://t.me/qrmahallabot/start?startapp=${startParam}`;

// Backend ga yuborish
const response = await fetch('https://your-api.com/api/qrcodes/scan/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${userToken}` // agar login bo'lsa
  },
  body: JSON.stringify({
    url: fullUrl
    // yoki faqat: uuid: startParam.replace('QR_KEY_', '')
  })
});

const data = await response.json();

// Response qayta ishlash
if (data.status === 'unclaimed') {
  showClaimButton(data);
} else if (data.status === 'claimed') {
  showOwnerInfo(data.owner, data.house);
}
```

---

## 🔐 BACKEND URL NI QAYTA ISHLAYDI

### **apps/qrcodes/views.py - extract_uuid():**

```python
def extract_uuid(self, data):
    """URL dan UUID ni ajratib olish"""
    
    # Input: "https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b"
    
    if "t.me/" in data or "telegram.me/" in data:
        if "QR_KEY_" in data:
            parts = data.split("QR_KEY_")
            # parts[1] = "df9dd4def795439b"
            return parts[1].strip()
    
    # Input: "df9dd4def795439b" (to'g'ridan UUID)
    if len(data) == 16:
        return data
    
    return data
```

**Natija:** `uuid = "df9dd4def795439b"`

---

## 📊 TO'LIQ WORKFLOW

```
┌─────────────────┐
│  QR Kod yaratish │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ 1. UUID generate: df9dd4def795439b   │
│ 2. URL tuzish:                       │
│    https://t.me/qrmahallabot/       │
│    start?startapp=QR_KEY_{uuid}     │
│ 3. QR rasmga encode qilish          │
│    → /media/qr_codes/{uuid}.png     │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  📸 User telefon kamerasi bilan      │
│     QR kodni scan qiladi             │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  📱 Telefon URL ni o'qiydi va        │
│     Telegram botni ochadi            │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  🤖 Telegram bot ochiladi            │
│     startapp = "QR_KEY_df9dd4..."   │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  💻 Frontend (Mini App)              │
│     startParam ni oladi              │
│     Backend ga POST qiladi           │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  ⚙️  Backend                         │
│     URL dan UUID ajratadi            │
│     QRCode ni topadi                 │
│     House ma'lumotini qaytaradi      │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  📱 Frontend response ko'rsatadi     │
│     - Unclaimed: Claim button        │
│     - Claimed: Owner info            │
│     - qr_url: Share button           │
└──────────────────────────────────────┘
```

---

## 🌐 FRONTEND GET ENDPOINTS

### **1. QR URL ni olish (har doim response da bor):**

```javascript
// QR scan qilgandan keyin
const response = await fetch('/api/qrcodes/scan/', {
  method: 'POST',
  body: JSON.stringify({ url: telegramUrl })
});

const data = await response.json();

console.log(data.qr.qr_url);
// Output: "https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b"

// Bu URL ni ishlatish mumkin:
// 1. Share button - boshqa odamlarga yuborish
// 2. QR kod qayta generate qilish
// 3. Deep link yaratish
```

### **2. Barcha QR kodlar ro'yxati:**

```javascript
// Admin/Leader uchun
const response = await fetch('/api/qrcodes/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const qrCodes = await response.json();

qrCodes.forEach(qr => {
  console.log(qr.qr_url);
  // Har bir QR ning Telegram URL i mavjud
  // QR image: qr.image
  // Share: qr.qr_url
});
```

### **3. User profili (qaysi QR scan qilgan):**

```javascript
const response = await fetch('/api/users/profile/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const profile = await response.json();

console.log(profile.scanned_qr_code); // "df9dd4def795439b"

// To'liq URL ni tuzish
const scannedUrl = `https://t.me/qrmahallabot/start?startapp=QR_KEY_${profile.scanned_qr_code}`;

// Yoki backend dan olish
profile.houses.forEach(house => {
  console.log(house.scanned_qr_code); // QR UUID
});
```

---

## ✅ ASOSIY NUQTALAR

1. **QR kod yaratilganda:**
   - UUID generate qilinadi
   - Telegram URL tuziladi: `https://t.me/bot/start?startapp=QR_KEY_{uuid}`
   - Bu URL QR rasmga encode qilinadi

2. **Telefon scan qilganda:**
   - Telefon URL ni o'qiydi
   - Telegram botni ochadi
   - StartApp parametrini uzatadi

3. **Frontend qabul qiladi:**
   - `window.Telegram.WebApp.initDataUnsafe.start_param`
   - Backend ga POST qiladi

4. **Backend qayta ishlaydi:**
   - URL dan UUID ni extract qiladi
   - QRCode ni topadi
   - House ma'lumotini qaytaradi
   - Response da `qr_url` majburiy

5. **Frontend response ishlatadi:**
   - `data.qr.qr_url` - Share qilish uchun
   - `data.house` - Uy ma'lumoti
   - `data.owner` - Ega ma'lumoti (rol asosida)

---

## 🔗 QR URL HAMMA JOYDA BOR

Har qanday QR response da `qr_url` mavjud:

```json
{
  "qr": {
    "id": 1,
    "uuid": "df9dd4def795439b",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b"
  }
}
```

Bu URL ni ishlatish:
- ✅ Share button
- ✅ QR kod qayta generate
- ✅ Deep linking
- ✅ Social media share
- ✅ Copy to clipboard
