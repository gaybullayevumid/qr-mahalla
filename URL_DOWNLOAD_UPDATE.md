# URL bilan ZIP Fayl Yuklash - Yangilangan

## ✅ O'zgarishlar

### 1. **Absolute URL Qaytarish**

Generate endpoint endi **to'liq absolute URL** qaytaradi (domain bilan):

**Oldingi:**
```json
{
  "download_url": "/media/qr_downloads/qrcodes_1_123.zip"
}
```

**Hozir:**
```json
{
  "download_url": "http://localhost:8000/media/qr_downloads/qrcodes_1_123.zip",
  "count": 50,
  "filename": "qrcodes_1_123.zip"
}
```

Frontend endi bu URLni to'g'ridan-to'g'ri ishlatishi mumkin:
```javascript
const { download_url } = await response.json();
window.location.href = download_url; // Works!
```

---

### 2. **Direct Download Endpoint (Qo'shimcha)**

Yangi endpoint qo'shildi - to'g'ridan-to'g'ri fayl yuklab olish uchun:

**Endpoint:**
```
GET /api/qrcodes/bulk/download/{filename}/
```

**Example:**
```bash
curl http://localhost:8000/api/qrcodes/bulk/download/qrcodes_1_123.zip \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -O
```

**Frontend:**
```javascript
// Option 1: Media URL (public access)
window.location.href = data.download_url;

// Option 2: API endpoint (with auth)
window.location.href = `/api/qrcodes/bulk/download/${data.filename}/`;
```

---

## 🔧 **API Response (Yangilangan)**

### POST /api/qrcodes/bulk/generate/

**Request:**
```json
{
  "count": 50
}
```

**Response (201):**
```json
{
  "download_url": "http://localhost:8000/media/qr_downloads/qrcodes_1_123.zip",
  "count": 50,
  "filename": "qrcodes_1_123.zip",
  "message": "QR kodlar muvaffaqiyatli yaratildi",
  "message_en": "QR codes generated successfully"
}
```

---

## 📱 **Frontend Integration**

### React/Next.js:

```jsx
const handleGenerate = async (count) => {
  try {
    // Generate QR codes
    const response = await fetch('/api/qrcodes/bulk/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({ count })
    });
    
    const data = await response.json();
    
    // Method 1: Direct download via absolute URL (Recommended)
    const link = document.createElement('a');
    link.href = data.download_url; // Full URL with domain
    link.download = data.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Method 2: Via API endpoint (with authentication)
    // window.location.href = `/api/qrcodes/bulk/download/${data.filename}/`;
    
  } catch (error) {
    console.error('Error:', error);
  }
};
```

---

## 🔐 **Security Features**

### BulkQRCodeDownloadView:
- ✅ Authentication required
- ✅ Admin/Gov/Leader role check
- ✅ Filename validation (prevents directory traversal)
- ✅ File existence check
- ✅ Proper Content-Disposition header

**Xavfsizlik:**
```python
# Prevents: ../../../etc/passwd
if '..' in filename or '/' in filename or '\\' in filename:
    return 400 Bad Request
```

---

## 🧪 **Test Examples**

### cURL:

```bash
# 1. Generate with absolute URL
curl -X POST http://localhost:8000/api/qrcodes/bulk/generate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"count": 20}'

# Response:
# {
#   "download_url": "http://localhost:8000/media/qr_downloads/qrcodes_1_456.zip",
#   "filename": "qrcodes_1_456.zip"
# }

# 2. Download via media URL (direct)
curl -O http://localhost:8000/media/qr_downloads/qrcodes_1_456.zip

# 3. Download via API endpoint (with auth)
curl http://localhost:8000/api/qrcodes/bulk/download/qrcodes_1_456.zip \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -O
```

---

## 📊 **Comparison**

| Variant | URL Type | Authentication | Use Case |
|---------|----------|----------------|----------|
| **Media URL** | `/media/qr_downloads/file.zip` | Optional (public) | Quick download, sharable |
| **API Endpoint** | `/api/qrcodes/bulk/download/file.zip` | Required | Secure, role-based access |

---

## ✨ **Summary**

- ✅ `download_url` endi **absolute URL** (domain bilan)
- ✅ `filename` qo'shildi responsega
- ✅ Yangi endpoint: `/api/qrcodes/bulk/download/{filename}/`
- ✅ Directory traversal attack himoyasi
- ✅ Frontend oson download qilishi mumkin

Frontend endi `download_url` ni to'g'ridan-to'g'ri ishlatishi mumkin - hech qanday qo'shimcha manipulyatsiya kerak emas!
