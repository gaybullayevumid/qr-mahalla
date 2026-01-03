# House Admin Create API

## ✅ Yangi Endpoint

### POST /api/houses/admin-create/

Admin/Super Admin uchun house yaratish endpointi. Owner ma'lumotlari bilan.

---

## 📋 Request Body

```json
{
  "region": "Toshkent",       // optional - validation uchun
  "district": "Chilonzor",    // optional - validation uchun
  "mahalla": 1,               // REQUIRED - mahalla ID
  "ownerFirstName": "hhh",    // optional - owner ismi
  "ownerLastName": "ggg",     // optional - owner familiyasi
  "phone": "111111111",       // REQUIRED - owner telefoni
  "address": "999999",        // REQUIRED - uy manzili
  "houseNumber": "88888"      // optional - uy raqami
}
```

### Field Details

**MAJBURIY (Required):**
- `phone` - Owner telefon raqami (avtomatik +998 qo'shiladi)
- `mahalla` - Mahalla ID (integer)
- `address` - Uy manzili (string)

**IXTIYORIY (Optional):**
- `region` - Region nomi (validation uchun)
- `district` - District nomi (validation uchun)
- `ownerFirstName` - Owner ismi
- `ownerLastName` - Owner familiyasi
- `houseNumber` - Uy raqami

---

## ✅ Success Response (201 Created)

```json
{
  "id": 13,
  "owner": {
    "id": 8,
    "phone": "+998111111111",
    "firstName": "hhh",
    "lastName": "ggg"
  },
  "mahalla": {
    "id": 1,
    "name": "Qatortol",
    "district": {
      "id": 1,
      "name": "Chilonzor",
      "region": {
        "id": 1,
        "name": "Toshkent"
      }
    }
  },
  "address": "999999",
  "houseNumber": "88888",
  "createdAt": "2026-01-03T11:07:51.188323+00:00"
}
```

---

## ❌ Error Responses

### Invalid Mahalla ID (400)
```json
{
  "mahalla": ["Mahalla with ID 999 does not exist"]
}
```

### Region/District Mismatch (400)
```json
{
  "region": ["Mahalla ID 1 does not belong to region 'WrongRegion'"]
}
```

---

## 🔧 Features

### 1. Phone Number Normalization
Telefon raqami avtomatik normalizatsiya qilinadi:

| Input         | Output          |
|---------------|-----------------|
| 901234567     | +998901234567   |
| 998901234567  | +998901234567   |
| +998901234567 | +998901234567   |

### 2. User Creation/Update
- **Yangi user:** Phone raqam bo'yicha user topilmasa, yangi user yaratiladi
- **Mavjud user:** Phone raqam bo'yicha user topilsa, ismi yangilanadi (agar berilgan bo'lsa)

### 3. Validation
- Mahalla ID mavjudligini tekshiradi
- Region va district nomi to'g'ri ekanligini tekshiradi (agar berilgan bo'lsa)

---

## 🎯 Frontend Integration

### React/JavaScript Example

```javascript
const createHouse = async (formData) => {
  try {
    const response = await axios.post('/api/houses/admin-create/', {
      region: formData.region,          // optional
      district: formData.district,      // optional
      mahalla: parseInt(formData.mahalla),  // required
      ownerFirstName: formData.firstName,
      ownerLastName: formData.lastName,
      phone: formData.phone,            // required
      address: formData.address,        // required
      houseNumber: formData.houseNumber
    });
    
    console.log('House created:', response.data);
    alert('Uy muvaffaqiyatli yaratildi!');
    
  } catch (error) {
    console.error('Error:', error.response?.data);
    if (error.response?.data?.mahalla) {
      alert('Mahalla topilmadi!');
    } else if (error.response?.data?.region) {
      alert('Region yoki district noto\'g\'ri!');
    } else {
      alert('Xatolik yuz berdi!');
    }
  }
};
```

### Full Form Component

```javascript
function CreateHouseForm() {
  const [formData, setFormData] = useState({
    region: '',
    district: '',
    mahalla: '',
    firstName: '',
    lastName: '',
    phone: '',
    address: '',
    houseNumber: ''
  });
  
  const [mahallas, setMahallas] = useState([]);
  
  useEffect(() => {
    // Load mahallas
    axios.get('/api/neighborhoods/')
      .then(res => setMahallas(res.data))
      .catch(err => console.error(err));
  }, []);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.post('/api/houses/admin-create/', {
        region: formData.region,
        district: formData.district,
        mahalla: parseInt(formData.mahalla),
        ownerFirstName: formData.firstName,
        ownerLastName: formData.lastName,
        phone: formData.phone,
        address: formData.address,
        houseNumber: formData.houseNumber
      });
      
      alert('Uy yaratildi!');
      console.log('Created house:', response.data);
      
      // Reset form
      setFormData({
        region: '',
        district: '',
        mahalla: '',
        firstName: '',
        lastName: '',
        phone: '',
        address: '',
        houseNumber: ''
      });
      
    } catch (error) {
      console.error('Error:', error.response?.data);
      const errorMsg = JSON.stringify(error.response?.data);
      alert('Xatolik: ' + errorMsg);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Region (optional) */}
      <input
        type="text"
        placeholder="Region (ixtiyoriy)"
        value={formData.region}
        onChange={(e) => setFormData({...formData, region: e.target.value})}
      />
      
      {/* District (optional) */}
      <input
        type="text"
        placeholder="District (ixtiyoriy)"
        value={formData.district}
        onChange={(e) => setFormData({...formData, district: e.target.value})}
      />
      
      {/* Mahalla (required) */}
      <select
        value={formData.mahalla}
        onChange={(e) => setFormData({...formData, mahalla: e.target.value})}
        required
      >
        <option value="">Mahalla tanlang...</option>
        {mahallas.map(m => (
          <option key={m.id} value={m.id}>
            {m.name}
          </option>
        ))}
      </select>
      
      {/* Owner First Name */}
      <input
        type="text"
        placeholder="Owner Ismi"
        value={formData.firstName}
        onChange={(e) => setFormData({...formData, firstName: e.target.value})}
      />
      
      {/* Owner Last Name */}
      <input
        type="text"
        placeholder="Owner Familiyasi"
        value={formData.lastName}
        onChange={(e) => setFormData({...formData, lastName: e.target.value})}
      />
      
      {/* Phone (required) */}
      <input
        type="tel"
        placeholder="Telefon: 901234567"
        value={formData.phone}
        onChange={(e) => setFormData({...formData, phone: e.target.value})}
        required
      />
      
      {/* Address (required) */}
      <input
        type="text"
        placeholder="Manzil"
        value={formData.address}
        onChange={(e) => setFormData({...formData, address: e.target.value})}
        required
      />
      
      {/* House Number */}
      <input
        type="text"
        placeholder="Uy raqami"
        value={formData.houseNumber}
        onChange={(e) => setFormData({...formData, houseNumber: e.target.value})}
      />
      
      <button type="submit">Uy Yaratish</button>
    </form>
  );
}
```

---

## 📝 Notes

1. **Authentication:** Hozirda `AllowAny` (testing). Production da `IsAdminOrGov` ga o'zgartirish kerak.

2. **Phone Format:** Har qanday formatda yuborish mumkin (avtomatik +998 qo'shiladi):
   - `901234567` ✅
   - `998901234567` ✅
   - `+998901234567` ✅

3. **Region/District:** Optional, faqat validation uchun. Mahalla ID yetarli.

4. **User Creation:** Telefon raqam bo'yicha user topilmasa, avtomatik yangi user yaratiladi (`role=client`).

---

## 🔐 Production Settings

Production uchun permission o'zgartirish:

```python
# apps/houses/views.py
def get_permissions(self):
    if self.action in ["list", "retrieve"]:
        return [IsAuthenticated()]
    if self.action == "admin_create":
        return [IsAuthenticated(), IsAdminOrGov()]  # Faqat admin
    return [IsAuthenticated(), HouseAccessPermission()]
```
