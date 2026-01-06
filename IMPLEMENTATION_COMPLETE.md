# ✅ BACKEND TO'LIQ TAYYOR - BULK QR CODE GENERATION

## 📋 **Qo'shilgan O'zgarishlar**

### 1. ✅ **Views** - [apps/qrcodes/views.py](apps/qrcodes/views.py)

**Import qo'shildi:**
```python
import os
import zipfile
from io import BytesIO
from django.http import HttpResponse, FileResponse
from django.conf import settings
```

**Yangi Classlar:**

#### `BulkQRCodeGenerateView` (787-qator)
- **Endpoint:** `POST /api/qrcodes/bulk/generate/`
- **Permission:** Admin/Gov/Leader
- **Input:** `{"count": 1-1000}`
- **Output:** `{"download_url": "/media/qr_downloads/...", "count": N, "message": "..."}`

**Funksiyasi:**
1. Count validatsiya (1-1000)
2. Transaction atomic bilan QR kodlar yaratish
3. ZIP fayl yaratish (in-memory)
4. `media/qr_downloads/` ga saqlash
5. Download URL qaytarish

#### `QRCodeBulkListView` (899-qator)
- **Endpoint:** `GET /api/qrcodes/bulk/list/`
- **Permission:** Admin/Gov/Leader
- **Query params:** `?limit=50&is_claimed=false`
- **Output:** QR kodlar ro'yxati (claimed/unclaimed filter bilan)

---

### 2. ✅ **Serializers** - [apps/qrcodes/serializers.py](apps/qrcodes/serializers.py)

**Yangi Serializer:**

```python
class BulkQRCodeGenerateSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        min_value=1,
        max_value=1000,
        required=True
    )
    
    def validate_count(self, value):
        # Validation: 1-1000 orasida bo'lishi kerak
        ...
```

**Validatsiya:**
- `count < 1`: "Kamida 1 ta QR kod yaratish kerak"
- `count > 1000`: "Maksimal 1000 ta QR kod yaratish mumkin"

---

### 3. ✅ **URLs** - [apps/qrcodes/urls.py](apps/qrcodes/urls.py)

**Yangi Routelar:**

```python
urlpatterns = [
    # ... existing routes ...
    path("bulk/generate/", BulkQRCodeGenerateView.as_view(), name="qr-bulk-generate"),
    path("bulk/list/", QRCodeBulkListView.as_view(), name="qr-bulk-list"),
    # ... existing routes ...
]
```

---

## 🔧 **API Endpointlar**

### 1. Generate Bulk QR Codes

**Request:**
```http
POST /api/qrcodes/bulk/generate/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "count": 50
}
```

**Success Response (201):**
```json
{
  "download_url": "/media/qr_downloads/qrcodes_1_123.zip",
  "count": 50,
  "message": "QR kodlar muvaffaqiyatli yaratildi",
  "message_en": "QR codes generated successfully"
}
```

**Error Responses:**

```json
// 403 Forbidden
{
  "error": "Ruxsat yo'q. Faqat admin foydalanuvchilar QR kod yaratishi mumkin.",
  "error_en": "Permission denied. Only admin users can generate QR codes.",
  "error_type": "permission_denied"
}

// 400 Bad Request
{
  "count": [
    "Bir vaqtning o'zida maksimal 1000 ta QR kod yaratish mumkin."
  ]
}
```

---

### 2. List Generated QR Codes

**Request:**
```http
GET /api/qrcodes/bulk/list/?limit=20&is_claimed=false
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
[
  {
    "id": 123,
    "uuid": "abc123def4567890",
    "qr_url": "https://t.me/bot?start=abc123def4567890",
    "image": "/media/qr_codes/qr_abc123def4567890.png",
    "is_claimed": false,
    "owner": null,
    "created_at": "2026-01-06T10:30:00Z"
  },
  ...
]
```

---

## 🎯 **Frontend Integration**

### React/Next.js Example:

```jsx
const handleGenerateQRCodes = async (count) => {
  try {
    // Step 1: Generate QR codes
    const response = await fetch('/api/qrcodes/bulk/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({ count })
    });
    
    const data = await response.json();
    
    // Step 2: Auto-download ZIP
    const link = document.createElement('a');
    link.href = data.download_url;
    link.download = `qrcodes_${count}.zip`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Step 3: Fetch generated QR codes
    const listResponse = await fetch(
      `/api/qrcodes/bulk/list/?limit=${count}&is_claimed=false`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      }
    );
    
    const qrCodes = await listResponse.json();
    setQrCodes(qrCodes);
    
  } catch (error) {
    console.error('Error:', error);
  }
};
```

---

## 🧪 **Test Cases**

### 1. Manual cURL Test:

```bash
# 1. Login (get token)
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567", "password": "admin123"}'

# 2. Generate 20 QR codes
curl -X POST http://localhost:8000/api/qrcodes/bulk/generate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"count": 20}'

# 3. List generated QR codes
curl http://localhost:8000/api/qrcodes/bulk/list/?limit=20 \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Download ZIP file
curl -O http://localhost:8000/media/qr_downloads/qrcodes_1_123.zip
```

### 2. Python Test Script:

```bash
python test_bulk_qr_generate.py
```

---

## 📦 **File Structure**

```
qr-mahalla/
├── apps/
│   └── qrcodes/
│       ├── views.py              ✅ Updated (BulkQRCodeGenerateView + QRCodeBulkListView)
│       ├── serializers.py        ✅ Updated (BulkQRCodeGenerateSerializer)
│       └── urls.py               ✅ Updated (2 new routes)
├── media/
│   └── qr_downloads/             ✅ Auto-created (ZIP files stored here)
│       └── qrcodes_*.zip
├── BULK_QR_IMPLEMENTATION.md     ✅ Created (Full documentation)
├── BULK_QR_GENERATE_API.md       ✅ Created (API reference)
└── test_bulk_qr_generate.py      ✅ Created (Test script)
```

---

## ✨ **Features Implemented**

- ✅ Bulk QR code generation (1-1000 at once)
- ✅ ZIP file creation and auto-download
- ✅ Direct media download link
- ✅ Permission control (Admin/Gov/Leader only)
- ✅ List generated QR codes with filters
- ✅ Filter by claimed/unclaimed status
- ✅ Limit parameter support
- ✅ Transaction atomic safety
- ✅ Uzbek & English error messages
- ✅ Proper validation (count: 1-1000)

---

## 🔐 **Security & Permissions**

1. **Authentication Required:** Bearer token
2. **Role Check:** Admin, Gov, Leader only
3. **Input Validation:** Count must be 1-1000
4. **Transaction Safety:** Atomic operations
5. **Error Handling:** Comprehensive try-catch blocks

---

## 📊 **Backend Logic Flow**

```
1. Frontend sends POST request with count
   ↓
2. Backend validates authentication & role
   ↓
3. Backend validates count (1-1000)
   ↓
4. Transaction starts
   ↓
5. Generate N QR codes (with UUID & images)
   ↓
6. Transaction commits
   ↓
7. Create ZIP file in memory
   ↓
8. Add all QR images to ZIP
   ↓
9. Save ZIP to media/qr_downloads/
   ↓
10. Return download URL to frontend
    ↓
11. Frontend auto-downloads ZIP
    ↓
12. Frontend fetches list of generated QR codes
    ↓
13. Display QR codes in UI
```

---

## 🚀 **Deployment Notes**

1. **Media Directory:** Ensure `media/qr_downloads/` has write permissions
2. **MEDIA_ROOT:** Already configured in settings.py
3. **MEDIA_URL:** Already configured as `/media/`
4. **Static Files:** URL pattern already set in config/urls.py
5. **Cleanup:** Consider cron job to delete old ZIP files

---

## ✅ **Verification Checklist**

- [x] Views updated with 2 new classes
- [x] Serializers updated with BulkQRCodeGenerateSerializer
- [x] URLs updated with 2 new routes
- [x] Imports added (os, zipfile, BytesIO, etc.)
- [x] Permissions implemented (Admin/Gov/Leader)
- [x] Validation implemented (1-1000 count)
- [x] Transaction safety implemented
- [x] ZIP file creation implemented
- [x] Media file handling implemented
- [x] Error handling implemented
- [x] Documentation created
- [x] Test script created
- [x] No syntax errors (verified with py_compile)
- [x] Classes exist in views.py (verified with AST)

---

## 🎉 **SUMMARY**

Backend **TO'LIQ TAYYOR**! 

Barcha kerakli funksiyalar qo'shildi:
1. ✅ Bulk QR generation endpoint
2. ✅ ZIP file creation
3. ✅ Download URL return
4. ✅ List generated QR codes endpoint
5. ✅ Filters (claimed/unclaimed, limit)
6. ✅ Permission control
7. ✅ Full error handling
8. ✅ Documentation

Frontend endi bu API'larni ishlatib, quyidagi flow'ni amalga oshirishi mumkin:
1. Input field (count)
2. Button click
3. Generate QR codes (POST)
4. Auto-download ZIP
5. Fetch & display generated QR codes (GET)

Server ishga tushirilgan va tayyor! 🚀
