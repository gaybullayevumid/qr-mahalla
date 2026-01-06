# QR Code Bulk Generation - Backend Implementation

## ✅ Tayyor Implementatsiya

Backend quyidagi funksiyalar bilan tayyor:

### 📍 **Endpointlar:**

1. **Bulk QR Kod Yaratish**
   - URL: `POST /api/qrcodes/bulk/generate/`
   - Faqat admin, gov, leader rollari uchun
   
2. **Yaratilgan QR Kodlarni Ko'rish**
   - URL: `GET /api/qrcodes/bulk/list/`
   - Faqat admin, gov, leader rollari uchun

---

## 🔧 **Backend O'zgarishlar**

### 1. **Views** ([apps/qrcodes/views.py](apps/qrcodes/views.py))

**Qo'shilgan classlar:**

#### `BulkQRCodeGenerateView`
```python
- Input: {"count": 10}
- Permission: Admin, Gov, Leader
- Output: 
  {
    "download_url": "/media/qr_downloads/qrcodes_1_123.zip",
    "count": 10,
    "message": "QR kodlar muvaffaqiyatli yaratildi"
  }
```

#### `QRCodeBulkListView`
```python
- Query params: ?limit=50&is_claimed=false
- Permission: Admin, Gov, Leader
- Output: Array of QR code objects
```

### 2. **Serializers** ([apps/qrcodes/serializers.py](apps/qrcodes/serializers.py))

**Qo'shilgan:**
```python
class BulkQRCodeGenerateSerializer:
    - count: IntegerField (1-1000)
    - Validation: min=1, max=1000
```

### 3. **URLs** ([apps/qrcodes/urls.py](apps/qrcodes/urls.py))

**Qo'shilgan routelar:**
```python
path("bulk/generate/", BulkQRCodeGenerateView.as_view())
path("bulk/list/", QRCodeBulkListView.as_view())
```

---

## 📝 **Frontend Integratsiyasi**

### React Component Misoli:

```jsx
import React, { useState } from 'react';
import axios from 'axios';

const QRGeneratorComponent = () => {
  const [count, setCount] = useState(10);
  const [loading, setLoading] = useState(false);
  const [qrCodes, setQrCodes] = useState([]);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      // Step 1: Generate QR codes
      const response = await axios.post(
        '/api/qrcodes/bulk/generate/',
        { count },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
          }
        }
      );

      const { download_url, count: generated } = response.data;
      
      // Step 2: Auto-download ZIP file
      const link = document.createElement('a');
      link.href = download_url;
      link.download = `qrcodes_${generated}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Step 3: Fetch generated QR codes list
      const listResponse = await axios.get(
        `/api/qrcodes/bulk/list/?limit=${generated}&is_claimed=false`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
          }
        }
      );

      setQrCodes(listResponse.data);
      alert(`${generated} ta QR kod yaratildi va yuklab olindi!`);
      
    } catch (error) {
      console.error('Error:', error);
      alert('Xatolik yuz berdi: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="qr-generator">
      <div className="input-group">
        <label>QR kod soni:</label>
        <input
          type="number"
          min="1"
          max="1000"
          value={count}
          onChange={(e) => setCount(parseInt(e.target.value))}
          disabled={loading}
        />
        <button onClick={handleGenerate} disabled={loading}>
          {loading ? 'Yaratilmoqda...' : `${count} ta QR kod yaratish`}
        </button>
      </div>

      {qrCodes.length > 0 && (
        <div className="qr-list">
          <h3>Yaratilgan QR kodlar ({qrCodes.length})</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>UUID</th>
                <th>Status</th>
                <th>Yaratilgan</th>
              </tr>
            </thead>
            <tbody>
              {qrCodes.map(qr => (
                <tr key={qr.id}>
                  <td>{qr.id}</td>
                  <td>{qr.uuid}</td>
                  <td>{qr.is_claimed ? 'Claimed' : 'Unclaimed'}</td>
                  <td>{new Date(qr.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default QRGeneratorComponent;
```

---

## 🧪 **Test Qilish**

### cURL orqali test:

```bash
# 1. Login qiling
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567", "password": "admin123"}'

# 2. QR kodlar yaratish
curl -X POST http://localhost:8000/api/qrcodes/bulk/generate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"count": 20}'

# 3. Yaratilgan QR kodlarni ko'rish
curl -X GET "http://localhost:8000/api/qrcodes/bulk/list/?limit=20&is_claimed=false" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. ZIP faylni yuklab olish
curl -O http://localhost:8000/media/qr_downloads/qrcodes_1_123.zip
```

### Python test script:

```bash
python test_bulk_qr_generate.py
```

---

## 📦 **ZIP Fayl Tuzilishi**

Yaratilgan ZIP fayl ichida:
```
qrcodes_1_123.zip
├── qr_abc123def456.png
├── qr_def456ghi789.png
├── qr_ghi789jkl012.png
└── ...
```

Har bir fayl nomi: `qr_{uuid}.png`

---

## ⚙️ **Backend Logikasi**

1. **Input Validation**
   - Count: 1-1000 orasida
   - Permission check: Admin/Gov/Leader
   
2. **QR Code Generation**
   - Transaction atomic blokida yaratiladi
   - Har bir QR kod o'zining UUID va image'ini oladi
   
3. **ZIP File Creation**
   - In-memory BytesIO orqali
   - Barcha QR kod rasmlarini qo'shadi
   - `media/qr_downloads/` papkasiga saqlaydi
   
4. **Response**
   - Download URL qaytaradi
   - Frontend avtomatik yuklab oladi
   
5. **List Endpoint**
   - Filter by claimed status
   - Limit parameter
   - Ordering by created_at DESC

---

## 🔐 **Xavfsizlik**

✅ Authentication required
✅ Role-based access control (Admin/Gov/Leader)
✅ Input validation (count: 1-1000)
✅ Transaction atomic operations
✅ Error handling

---

## 📊 **API Response Examples**

### Success (201 Created):
```json
{
  "download_url": "/media/qr_downloads/qrcodes_1_123.zip",
  "count": 20,
  "message": "QR kodlar muvaffaqiyatli yaratildi",
  "message_en": "QR codes generated successfully"
}
```

### Error - Invalid Count (400):
```json
{
  "count": [
    "Bir vaqtning o'zida maksimal 1000 ta QR kod yaratish mumkin. / Maximum 1000 QR codes can be generated at once."
  ]
}
```

### Error - Permission Denied (403):
```json
{
  "error": "Ruxsat yo'q. Faqat admin foydalanuvchilar QR kod yaratishi mumkin.",
  "error_en": "Permission denied. Only admin users can generate QR codes.",
  "error_type": "permission_denied"
}
```

---

## ✨ **Features**

✅ Bulk QR code generation (1-1000)
✅ Automatic ZIP file creation
✅ Direct download link
✅ List recently created QR codes
✅ Filter by claimed/unclaimed status
✅ Role-based permissions
✅ Uzbek & English error messages
✅ Transaction safety
✅ Automatic cleanup support (media files)

---

## 📁 **File Locations**

- Views: [apps/qrcodes/views.py](apps/qrcodes/views.py#L788-L929)
- Serializers: [apps/qrcodes/serializers.py](apps/qrcodes/serializers.py#L1-L31)
- URLs: [apps/qrcodes/urls.py](apps/qrcodes/urls.py#L14-L15)
- Documentation: [BULK_QR_GENERATE_API.md](BULK_QR_GENERATE_API.md)
- Test Script: [test_bulk_qr_generate.py](test_bulk_qr_generate.py)

---

## 🚀 **Deploy Notes**

1. **Media Files:** Ensure `MEDIA_ROOT` and `MEDIA_URL` configured properly
2. **Permissions:** Create `media/qr_downloads/` directory
3. **Cleanup:** Consider adding cron job to delete old ZIP files
4. **Storage:** For production, consider using cloud storage (AWS S3, etc.)

---

## 💡 **Next Steps**

- [ ] Add periodic cleanup task for old ZIP files
- [ ] Add download history tracking
- [ ] Add email notification option
- [ ] Add QR code customization options (logo, colors)
- [ ] Add CSV export of QR codes list
