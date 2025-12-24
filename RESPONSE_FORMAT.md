# Backend Response Formatlari

## 1. AUTH ENDPOINT - `/api/users/auth/`

### Request (SMS yuborish):
```json
POST /api/users/auth/
{
  "phone": "+998901234567"
}
```

### Response (SMS yuborildi):
```json
{
  "message": "SMS code sent",
  "phone": "+998901234567",
  "detail": "Please verify your phone number with the code sent via SMS"
}
```

---

### Request (Kod bilan login):
```json
POST /api/users/auth/
{
  "phone": "+998901234567",
  "code": "123456",
  "device_id": "unique-device-id",
  "device_name": "iPhone 12"
}
```

### ✅ Response (Login muvaffaqiyatli):
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "id": 11,                    ⬅️ BU YERDA ID BOR!
    "phone": "+998991234567",
    "role": "user",
    "first_name": "",
    "last_name": "",
    "passport_id": "",
    "address": "",
    "is_verified": true,
    "houses": []
  },
  "available_roles": [
    {
      "value": "super_admin",
      "label": "Super Admin",
      "level": 4
    },
    {
      "value": "government",
      "label": "Government Officer",
      "level": 3
    },
    {
      "value": "mahalla_admin",
      "label": "Neighborhood Admin",
      "level": 2
    },
    {
      "value": "user",
      "label": "User",
      "level": 1
    }
  ]
}
```

**Frontend uchun:**
```javascript
// Auth qilgandan keyin
const response = await axios.post('/api/users/auth/', data);

// ID olish:
const userId = response.data.user.id;  // ⬅️ SHUNDAY
// ❌ NOTO'G'RI: response.data.id
// ❌ NOTO'G'RI: response.user.id

console.log('User ID:', userId);  // 11
console.log('Token:', response.data.access);
```

---

## 2. PROFILE ENDPOINT - `/api/users/profile/`

### Request:
```json
GET /api/users/profile/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}
```

### ✅ Response:
```json
{
  "id": 8,                       ⬅️ TO'G'RIDAN-TO'G'RI ID BOR!
  "phone": "+998991234567",
  "role": "user",
  "first_name": "John",
  "last_name": "Doe",
  "passport_id": "AB1234567",
  "address": "Tashkent",
  "is_verified": true,
  "houses": [
    {
      "id": 5,
      "address": "Street 123",
      "house_number": "45",
      "mahalla": "Chilonzor",
      "district": "Chilonzor",
      "region": "Tashkent",
      "scanned_qr_code": "uuid-here"
    }
  ]
}
```

**Frontend uchun:**
```javascript
// Profile olish
const response = await axios.get('/api/users/profile/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// ID olish:
const userId = response.data.id;  // ⬅️ SHUNDAY (to'g'ridan-to'g'ri)
// ❌ NOTO'G'RI: response.data.user.id

console.log('User ID:', userId);  // 8
```

---

## Farqlarga e'tibor bering:

### AUTH endpoint:
```javascript
userId = response.data.user.id  // user object ichida
```

### PROFILE endpoint:
```javascript
userId = response.data.id  // to'g'ridan-to'g'ri
```

---

## Frontend localStorage'da saqlash:

```javascript
// Login qilgandan keyin
const loginResponse = await axios.post('/api/users/auth/', loginData);

// Ma'lumotlarni saqlash
localStorage.setItem('access_token', loginResponse.data.access);
localStorage.setItem('refresh_token', loginResponse.data.refresh);
localStorage.setItem('user', JSON.stringify(loginResponse.data.user));

// ID olish
const user = JSON.parse(localStorage.getItem('user'));
console.log('Saved User ID:', user.id);  // 11
```

---

## Axios Interceptor misol:

```javascript
// axios instance yarating
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor - har bir requestga token qo'shish
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - xatolarni handle qilish
api.interceptors.response.use(
  (response) => {
    console.log('Response data:', response.data);
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## Frontend komponent misol (React):

```javascript
import { useState } from 'react';
import api from './api';

function LoginComponent() {
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState(1); // 1=phone, 2=code
  const [userData, setUserData] = useState(null);

  // SMS yuborish
  const sendSMS = async () => {
    try {
      const response = await api.post('/users/auth/', { phone });
      console.log('SMS sent:', response.data.message);
      setStep(2);
    } catch (error) {
      console.error('Error:', error.response?.data);
    }
  };

  // Login
  const login = async () => {
    try {
      const response = await api.post('/users/auth/', { 
        phone, 
        code,
        device_id: 'web-browser',
        device_name: navigator.userAgent
      });
      
      // ✅ ID BU YERDA
      console.log('User ID:', response.data.user.id);
      console.log('User data:', response.data.user);
      
      // Saqlash
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      setUserData(response.data.user);
      
      // Profile olamiz
      fetchProfile();
      
    } catch (error) {
      console.error('Login error:', error.response?.data);
    }
  };

  // Profile olish
  const fetchProfile = async () => {
    try {
      const response = await api.get('/users/profile/');
      
      // ✅ ID BU YERDA (to'g'ridan-to'g'ri)
      console.log('Profile ID:', response.data.id);
      console.log('Profile data:', response.data);
      
      setUserData(response.data);
      
    } catch (error) {
      console.error('Profile error:', error.response?.data);
    }
  };

  return (
    <div>
      {step === 1 && (
        <div>
          <input 
            value={phone} 
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+998901234567"
          />
          <button onClick={sendSMS}>Send SMS</button>
        </div>
      )}
      
      {step === 2 && (
        <div>
          <input 
            value={code} 
            onChange={(e) => setCode(e.target.value)}
            placeholder="123456"
          />
          <button onClick={login}>Login</button>
        </div>
      )}
      
      {userData && (
        <div>
          <h3>Welcome!</h3>
          <p>User ID: {userData.id}</p>  {/* ⬅️ BU YERDA */}
          <p>Phone: {userData.phone}</p>
          <p>Role: {userData.role}</p>
        </div>
      )}
    </div>
  );
}
```

---

## Debug qilish uchun:

```javascript
// Browser console'da
const response = await fetch('http://127.0.0.1:8000/api/users/auth/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+998901234567', code: '123456' })
});

const data = await response.json();
console.log('Full response:', data);
console.log('User ID:', data.user.id);  // ⬅️ BU ISHLAYDI
```

---

## CORS Headers (Backend allaqachon to'g'ri):

```python
# config/settings.py
CORS_ALLOW_ALL_ORIGINS = True  # ✅ Ishlamoqda

# Yoki muayyan origin'lar uchun:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
```

---

## Agar ID undefined bo'lsa:

1. **Browser console tekshiring:**
```javascript
console.log('Response:', response);
console.log('Response.data:', response.data);
console.log('Response.data.user:', response.data.user);
console.log('Response.data.user.id:', response.data.user.id);
```

2. **Network tab tekshiring:**
- Chrome DevTools > Network
- Auth requestni toping
- Response tab'ni oching
- JSON formatda `user.id` bormi tekshiring

3. **LocalStorage tekshiring:**
```javascript
// Console'da
const user = JSON.parse(localStorage.getItem('user'));
console.log('Saved user:', user);
console.log('Saved user ID:', user?.id);

// Agar eski ma'lumot bo'lsa, tozalang:
localStorage.clear();
```

4. **Cache tozalang:**
- Ctrl + Shift + Delete
- Yoki Hard Reload: Ctrl + Shift + R
