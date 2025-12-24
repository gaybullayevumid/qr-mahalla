# Frontend POST Request Issues - Muammolar va Yechimlar

## ✅ To'g'irlangan muammolar

### 1. User yaratishda Houses bilan muammo
**Muammo**: Frontend `houses` arrayda `region` va `district` yuborardi, lekin House modelida bu fieldlar yo'q.

**Yechim**: Serializer to'g'irlandi - `region` va `district` fieldlari avtomatik o'chiriladi (`pop()` qilinadi).

**To'g'ri format**:
```json
{
  "phone": "+998901234567",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "role": "user",
  "houses": [
    {
      "mahalla": 1,
      "house_number": "123",
      "address": "Toshkent ko'chasi 123",
      "region": 1,      // ← Bu optional, serializer ignore qiladi
      "district": 1     // ← Bu optional, serializer ignore qiladi  
    }
  ]
}
```

**Minimal format (tavsiya etiladi)**:
```json
{
  "phone": "+998901234567",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "houses": [
    {
      "mahalla": 1,
      "address": "Toshkent ko'chasi 123",
      "house_number": "123"  // optional
    }
  ]
}
```

### 2. District yaratishda region muammosi
**Muammo**: Standalone district yaratishda `region` field optional edi, lekin aslida required.

**Yechim**: Serializer validation qo'shildi - agar `region` yo'q bo'lsa, xato qaytaradi.

**To'g'ri format**:
```json
{
  "name": "Toshkent tumani",
  "region": 1  // ← Bu majburiy!
}
```

### 3. house_number default value
**Muammo**: `house_number` bo'sh bo'lganda validation xato berishi mumkin edi.

**Yechim**: Default value `""` qo'shildi.

## 📋 Frontend uchun to'g'ri POST formatlar

### 1. Auth - SMS yuborish
```javascript
POST /api/auth/
Content-Type: application/json

{
  "phone": "+998901234567"
}
```

### 2. Auth - SMS tasdiqlash
```javascript
POST /api/auth/
Content-Type: application/json

{
  "phone": "+998901234567",
  "code": "123456",
  "device_id": "unique-device-id",  // optional
  "device_name": "iPhone 13"        // optional
}
```

### 3. Region yaratish (super_admin, government)
```javascript
POST /api/regions/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Toshkent shahar"
}
```

**Nested yaratish**:
```json
{
  "name": "Toshkent shahar",
  "districts": [
    {
      "name": "Chilonzor tumani",
      "mahallas": [
        {
          "name": "Katta Chilonzor",
          "admin": 1  // optional - User ID
        }
      ]
    }
  ]
}
```

### 4. District yaratish
```javascript
POST /api/districts/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Chilonzor tumani",
  "region": 1  // ← Majburiy!
}
```

### 5. Mahalla yaratish
```javascript
POST /api/mahallas/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Katta Chilonzor",
  "district": 1,  // ← Majburiy!
  "admin": 2      // optional - User ID
}
```

### 6. House yaratish (barcha authenticated users)
```javascript
POST /api/houses/
Authorization: Bearer {token}
Content-Type: application/json

{
  "mahalla": 1,  // ← Majburiy!
  "address": "Toshkent ko'chasi 123",
  "house_number": "123"  // optional
}
```

**Muhim**: `owner` avtomatik current user ga o'rnatiladi!

### 7. User yaratish (admin)
```javascript
POST /api/users/
Authorization: Bearer {token}
Content-Type: application/json

// Minimal:
{
  "phone": "+998901234567"
  // role default "user" bo'ladi
}

// To'liq:
{
  "phone": "+998901234567",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "passport_id": "AA1234567",
  "address": "Toshkent, Mirobod",
  "role": "user"
}

// Houses bilan:
{
  "phone": "+998901234567",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "houses": [
    {
      "mahalla": 1,
      "address": "Toshkent ko'chasi 123"
    }
  ]
}
```

### 8. QR code bilan house claim qilish
```javascript
// 1. Avval scan qiling (GET):
GET /api/qrcodes/scan-uuid/{uuid}/
Authorization: Bearer {token}

// 2. Agar unclaimed bo'lsa, claim qiling (POST):
POST /api/qrcodes/claim-uuid/{uuid}/
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "Ali",
  "last_name": "Valiyev",
  "passport_id": "AA1234567",
  "address": "Toshkent, Mirobod tumani, Amir Temur ko'chasi 123"
}
```

## 🔍 Xatoliklarni debug qilish

### ValidationError olsangiz:
1. **400 Bad Request** - ma'lumotlar noto'g'ri formatda
2. Response body'da xato tafsilotlari bo'ladi:
   ```json
   {
     "field_name": ["error message"],
     "another_field": ["another error"]
   }
   ```

### Tez-tez uchraydigan xatolar:

#### "This field is required"
```json
{
  "phone": ["This field is required"]
}
```
**Yechim**: Majburiy fieldni qo'shing (user uchun `phone`, house uchun `mahalla`, va h.k.)

#### "Invalid phone number format"
```json
{
  "phone": ["Invalid phone number format. Format: +998901234567"]
}
```
**Yechim**: Telefon raqamni `+998XXXXXXXXX` formatida yuboring

#### "QR code already exists for this house"
```json
{
  "house": ["QR code already exists for this house"]
}
```
**Yechim**: Bu house uchun allaqachon QR kod yaratilgan

#### "Region is required when creating a district"
```json
{
  "region": ["Region is required when creating a district"]
}
```
**Yechim**: District yaratishda `region` field majburiy

## ⚠️ Muhim eslatmalar

1. **Authorization Header** - Barcha authenticated endpointlar uchun:
   ```javascript
   headers: {
     'Authorization': 'Bearer ' + accessToken,
     'Content-Type': 'application/json'
   }
   ```

2. **Phone format** - Doim `+998` bilan boshlash kerak:
   - ✅ `+998901234567`
   - ❌ `998901234567`
   - ❌ `901234567`

3. **Role-based permissions**:
   - `user` - faqat o'z ma'lumotlarini ko'radi, house yaratishi mumkin
   - `mahalla_admin` - faqat o'z mahallasini boshqaradi
   - `government` - barcha CRUD
   - `super_admin` - barcha CRUD

4. **House owner** - House yaratilganda `owner` avtomatik current user ga o'rnatiladi. Uni POST request da yuborish shart emas!

5. **Nested objects** - Region yaratishda nested districts va mahallas qo'shish mumkin, lekin bu optional.

## 🎯 Frontend Development Tips

### React/Next.js uchun:
```javascript
const createHouse = async (mahallaId, address, houseNumber = "") => {
  try {
    const response = await fetch('/api/houses/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mahalla: mahallaId,
        address: address,
        house_number: houseNumber
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Validation errors:', errorData);
      throw new Error('House creation failed');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};
```

### Error handling:
```javascript
const handleError = (error) => {
  if (error.response && error.response.data) {
    // Django ValidationError format
    const errors = error.response.data;
    Object.keys(errors).forEach(field => {
      console.log(`${field}: ${errors[field].join(', ')}`);
      // Show error in UI
    });
  }
};
```

## 🚀 Test qilish

Server ishga tushiring:
```bash
python manage.py runserver
```

Manual test (curl):
```bash
# SMS yuborish
curl -X POST http://127.0.0.1:8000/api/auth/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567"}'

# House yaratish
curl -X POST http://127.0.0.1:8000/api/houses/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mahalla": 1, "address": "Test address"}'
```

Yoki Postman/Thunder Client/Insomnia ishlatishingiz mumkin.
