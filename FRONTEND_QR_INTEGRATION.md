# FRONTEND INTEGRATION - QR CODE SYSTEM

## 1. QR CODE SCAN (Telefon kamerasidan)

**Endpoint:** `POST /api/qrcodes/scan/`

**Request (3 xil usul):**
```json
// Usul 1: To'g'ridan UUID
{
  "uuid": "df9dd4def795439b"
}

// Usul 2: Telegram URL (telefon kamerasi scan qilganda)
{
  "url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b"
}

// Usul 3: qr_code parametri
{
  "qr_code": "https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b"
}
```

**Response (Unclaimed house, anonymous):**
```json
{
  "status": "unclaimed",
  "message": "Bu uyning egasi yo'q. Claim qilish uchun login qiling.",
  "qr": {
    "id": 1,
    "uuid": "df9dd4def795439b",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b"
  },
  "house": {
    "id": 20,
    "address": "Dehqonobod, avtomatik yaratilgan uy",
    "house_number": "AUTO-13",
    "region": {
      "id": 5,
      "name": "Farg'ona viloyati"
    },
    "district": {
      "id": 55,
      "name": "Farg'ona"
    },
    "mahalla": {
      "id": 20,
      "name": "Dehqonobod"
    }
  },
  "owner": null,
  "can_claim": false
}
```

**Response (Unclaimed house, authenticated client):**
```json
{
  "status": "unclaimed",
  "message": "Bu uyning egasi yo'q. Siz claim qilishingiz mumkin.",
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
  },
  "owner": null,
  "can_claim": true,
  "claim_url": "/api/qrcodes/claim/df9dd4def795439b/"
}
```

**Response (Claimed house, anonymous):**
```json
{
  "status": "claimed",
  "qr": {
    "id": 2,
    "uuid": "c628e14b75ba4403",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_c628e14b75ba4403"
  },
  "house": {
    "id": 15,
    "address": "555",
    "house_number": "AUTO-8",
    "region": {...},
    "district": {...},
    "mahalla": {...}
  },
  "owner": {
    "id": 5,
    "first_name": "Muxriddin",
    "last_name": "Rustamov",
    "phone": "+998906252919"
    // role va is_verified YO'Q (anonymous user)
  },
  "is_owner": false
}
```

**Response (Claimed house, admin/gov/leader):**
```json
{
  "status": "claimed",
  "qr": {
    "id": 2,
    "uuid": "c628e14b75ba4403",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_c628e14b75ba4403"
  },
  "house": {
    "id": 15,
    "address": "555",
    "house_number": "AUTO-8",
    "region": {...},
    "district": {...},
    "mahalla": {...}
  },
  "owner": {
    "id": 5,
    "first_name": "Muxriddin",
    "last_name": "Rustamov",
    "phone": "+998906252919",
    "role": "client",              // ← ADMIN uchun
    "is_verified": true            // ← ADMIN uchun
  },
  "is_owner": false
}
```

---

## 2. HOUSE CLAIM (Uyni o'ziga biriktirish)

**Endpoint:** `POST /api/qrcodes/claim/{uuid}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "first_name": "Aziz",
  "last_name": "Ahmadov"
}
```

**Response (Success):**
```json
{
  "message": "House claimed successfully",
  "house": {
    "id": 20,
    "address": "Dehqonobod, avtomatik yaratilgan uy",
    "number": "AUTO-13",
    "mahalla": "Dehqonobod"
  },
  "owner": {
    "phone": "+998901234567",
    "first_name": "Aziz",
    "last_name": "Ahmadov",
    "role": "client"
  },
  "qr": {
    "id": 1,
    "uuid": "df9dd4def795439b",
    "qr_url": "https://t.me/qrmahallabot/start?startapp=QR_KEY_df9dd4def795439b"
  }
}
```

**Response (Error - Already claimed):**
```json
{
  "error": "This house is already claimed"
}
```

---

## 3. USER PROFILE

**Endpoint:** `GET /api/users/me/`

**Headers:**
```
Authorization: Bearer {access_token}
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

---

## FRONTEND INTEGRATION FLOW

### Telegram Mini App Integration:

1. **User telefondan QR scan qiladi:**
   ```javascript
   // Telegram WebApp dan startapp parametrini olish
   const initData = window.Telegram.WebApp.initDataUnsafe;
   const startParam = initData.start_param; // "QR_KEY_df9dd4def795439b"
   
   // Backend ga yuborish
   const response = await fetch('/api/qrcodes/scan/', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       url: `https://t.me/qrmahallabot/start?startapp=${startParam}`
     })
   });
   ```

2. **Response qayta ishlash:**
   ```javascript
   const data = await response.json();
   
   if (data.status === 'unclaimed') {
     if (data.can_claim) {
       // Claim button ko'rsatish
       showClaimButton(data.claim_url);
     } else {
       // Login taklif qilish
       showLoginPrompt();
     }
   } else if (data.status === 'claimed') {
     // Owner ma'lumotini ko'rsatish
     displayOwnerInfo(data.owner);
     displayHouseInfo(data.house);
   }
   ```

3. **Claim qilish:**
   ```javascript
   const claimResponse = await fetch(`/api/qrcodes/claim/${uuid}/`, {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${accessToken}`
     },
     body: JSON.stringify({
       first_name: 'Aziz',
       last_name: 'Ahmadov'
     })
   });
   ```

---

## ROLE-BASED MA'LUMOT

| Field | Anonymous | Client | Admin/Gov/Leader |
|-------|-----------|--------|------------------|
| owner.id | ✅ | ✅ | ✅ |
| owner.first_name | ✅ | ✅ | ✅ |
| owner.last_name | ✅ | ✅ | ✅ |
| owner.phone | ✅ | ✅ | ✅ |
| owner.role | ❌ | ❌ | ✅ |
| owner.is_verified | ❌ | ❌ | ✅ |
| can_claim | ❌ | ✅ | ✅ |
| claim_url | ❌ | ✅ | ✅ |
| house.id | ✅ | ✅ | ✅ |
| qr.id | ✅ | ✅ | ✅ |
| qr.qr_url | ✅ | ✅ | ✅ |

---

## ERROR RESPONSES

**QR not found:**
```json
{
  "error": "QR code not found"
}
```

**Invalid format:**
```json
{
  "error": "Invalid QR code format"
}
```

**Missing data:**
```json
{
  "error": "QR code data is required. Send 'uuid', 'qr_code', or 'url' parameter."
}
```
