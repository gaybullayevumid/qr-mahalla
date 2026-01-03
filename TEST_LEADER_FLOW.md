# Leader User Flow - Super Admin Test

## ✅ O'zgarishlar

### 1. User Model
```python
mahalla = ForeignKey('regions.Mahalla', null=True, blank=True)
```
- Leader role bo'lgan userga mahalla biriktiriladi
- Boshqa role'larda mahalla NULL bo'ladi

### 2. User Serializers

**UserListSerializer** - GET uchun:
```json
{
  "id": 1,
  "phone": "+998901234567",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "role": "leader",
  "mahalla": 5,
  "mahalla_detail": {
    "id": 5,
    "name": "Qatortol",
    "district": {
      "id": 2,
      "name": "Chilonzor",
      "region": {
        "id": 1,
        "name": "Toshkent"
      }
    }
  },
  "is_verified": true,
  "houses": []
}
```

**UserCreateUpdateSerializer** - POST/PUT uchun:
```json
{
  "phone": "+998901234567",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "role": "leader",
  "mahalla": 5
}
```

### 3. Validation Rules
- ✅ Role = "leader" bo'lsa → mahalla MAJBURIY
- ✅ Role ≠ "leader" bo'lsa → mahalla avtomatik NULL qilinadi
- ✅ Mahalla ID mavjudligini tekshiradi

---

## 📋 API Endpoints

### 1. Mahallalar ro'yxati
```http
GET /api/neighborhoods/
Authorization: Bearer {token}  (yoki hech narsa - AllowAny)
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Qatortol",
    "district": 2,
    "admin": null
  },
  {
    "id": 2,
    "name": "Bodomzor",
    "district": 2,
    "admin": null
  }
]
```

### 2. User yaratish (Leader)
```http
POST /api/users/list/
Content-Type: application/json
Authorization: Bearer {token}  (yoki hech narsa - AllowAny)

{
  "phone": "+998901234567",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "role": "leader",
  "mahalla": 5
}
```

**Success Response (201):**
```json
{
  "id": 15,
  "phone": "+998901234567",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "role": "leader",
  "mahalla": 5,
  "houses": []
}
```

**Error Response (400) - mahalla yo'q:**
```json
{
  "mahalla": ["Mahalla is required for leader role"]
}
```

### 3. User yangilash
```http
PUT /api/users/list/{user_id}/
Content-Type: application/json
Authorization: Bearer {token}

{
  "role": "leader",
  "mahalla": 3
}
```

### 4. Userlarni ko'rish
```http
GET /api/users/list/
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": 15,
    "phone": "+998901234567",
    "first_name": "Ali",
    "last_name": "Valiyev",
    "role": "leader",
    "mahalla": 5,
    "mahalla_detail": {
      "id": 5,
      "name": "Qatortol",
      "district": {
        "id": 2,
        "name": "Chilonzor",
        "region": {
          "id": 1,
          "name": "Toshkent"
        }
      }
    },
    "is_verified": false,
    "houses": []
  }
]
```

### 5. Leader o'z mahalla uylarini ko'radi
```http
GET /api/houses/
Authorization: Phone +998901234567  (leader phone)
```

**Faqat leader mahallasidagi uylar qaytadi:**
```json
[
  {
    "id": 123,
    "owner": 15,
    "mahalla": 5,
    "house_number": "12",
    "address": "Qatortol MFY, 12-uy",
    "created_at": "2026-01-03T10:00:00Z"
  }
]
```

---

## 🎯 Frontend Qo'llanma (React)

### 1. Mahallalarni olish
```javascript
const [mahallas, setMahallas] = useState([]);

useEffect(() => {
  axios.get('/api/neighborhoods/')
    .then(res => setMahallas(res.data))
    .catch(err => console.error(err));
}, []);
```

### 2. User yaratish forma
```javascript
const [formData, setFormData] = useState({
  phone: '',
  firstName: '',
  lastName: '',
  role: 'client',
  mahalla: null
});

const createUser = async () => {
  try {
    const payload = {
      phone: formData.phone,
      first_name: formData.firstName,
      last_name: formData.lastName,
      role: formData.role
    };
    
    // Faqat leader bo'lsa mahalla qo'shish
    if (formData.role === 'leader') {
      payload.mahalla = parseInt(formData.mahalla);
    }
    
    const response = await axios.post('/api/users/list/', payload);
    alert('User muvaffaqiyatli yaratildi!');
    console.log('User:', response.data);
    
  } catch (error) {
    if (error.response?.data?.mahalla) {
      alert('Leader uchun mahalla tanlash majburiy!');
    } else {
      alert('Xatolik yuz berdi!');
    }
  }
};
```

### 3. To'liq Form Component
```javascript
function CreateUserForm() {
  const [formData, setFormData] = useState({
    phone: '',
    firstName: '',
    lastName: '',
    role: 'client',
    mahalla: ''
  });
  
  const [mahallas, setMahallas] = useState([]);
  
  useEffect(() => {
    // Mahallalarni olish
    axios.get('/api/neighborhoods/')
      .then(res => setMahallas(res.data))
      .catch(err => console.error(err));
  }, []);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {
      phone: formData.phone,
      first_name: formData.firstName,
      last_name: formData.lastName,
      role: formData.role
    };
    
    if (formData.role === 'leader' && formData.mahalla) {
      payload.mahalla = parseInt(formData.mahalla);
    }
    
    try {
      const response = await axios.post('/api/users/list/', payload);
      alert('User yaratildi!');
      // Reset form
      setFormData({
        phone: '',
        firstName: '',
        lastName: '',
        role: 'client',
        mahalla: ''
      });
    } catch (error) {
      console.error('Error:', error.response?.data);
      alert('Xatolik: ' + JSON.stringify(error.response?.data));
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="tel"
        placeholder="Telefon: +998901234567"
        value={formData.phone}
        onChange={(e) => setFormData({...formData, phone: e.target.value})}
        required
      />
      
      <input
        type="text"
        placeholder="Ism"
        value={formData.firstName}
        onChange={(e) => setFormData({...formData, firstName: e.target.value})}
      />
      
      <input
        type="text"
        placeholder="Familiya"
        value={formData.lastName}
        onChange={(e) => setFormData({...formData, lastName: e.target.value})}
      />
      
      <select
        value={formData.role}
        onChange={(e) => setFormData({...formData, role: e.target.value})}
        required
      >
        <option value="client">Client</option>
        <option value="leader">Leader</option>
        <option value="admin">Admin</option>
        <option value="gov">Government</option>
      </select>
      
      {/* Faqat leader tanlanganda mahalla select ko'rinadi */}
      {formData.role === 'leader' && (
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
      )}
      
      <button type="submit">User Yaratish</button>
    </form>
  );
}
```

---

## ✅ Natija

### Super Admin qilishi kerak:
1. ✅ `/api/neighborhoods/` dan mahallalarni oladi
2. ✅ Formada role = "leader" tanlanadi
3. ✅ Mahalla select paydo bo'ladi va to'ldiriladi
4. ✅ User yaratiladi → mahalla biriktiriladi
5. ✅ Leader faqat o'z mahalla uylarini ko'radi

### Leader qilishi kerak:
1. ✅ Login qiladi (phone auth)
2. ✅ `/api/houses/` ni ochadi
3. ✅ Faqat o'z mahallasidagi uylarni ko'radi
4. ✅ Boshqa mahalla uylarini ko'ra olmaydi

### Backend avtomatik:
1. ✅ Role = leader → mahalla MAJBURIY
2. ✅ Role ≠ leader → mahalla NULL
3. ✅ HouseViewSet filterlaydi: `filter(mahalla=user.mahalla)`
4. ✅ UserListSerializer mahalla detaillarini qaytaradi

---

## 🔐 Security Notes

**Hozirgi holat (Testing):**
- `/api/users/list/` - AllowAny ✅
- `/api/neighborhoods/` - AllowAny ✅
- `/api/regions/` - AllowAny ✅

**Production uchun qaytarish kerak:**
```python
# apps/users/views.py
permission_classes = [IsAuthenticated, IsAdminOrGov]

# apps/regions/views.py  
permission_classes = [IsAuthenticated]
```
