# API ENDPOINTS DOCUMENTATION

## BASE URL
```
http://127.0.0.1:8000/api
```

---

## 🔐 USER AUTHENTICATION & PROFILE

### 1. Auth (SMS + Login)
**Endpoint:** `POST /api/users/auth/`

**Step 1 - Send SMS:**
```json
POST /api/users/auth/
{
  "phone": "+998901234567"
}

Response:
{
  "message": "SMS code sent",
  "phone": "+998901234567",
  "detail": "Please verify your phone number with the code sent via SMS"
}
```

**Step 2 - Login with code:**
```json
POST /api/users/auth/
{
  "phone": "+998901234567",
  "code": "123456",
  "device_id": "web-browser",
  "device_name": "Chrome"
}

Response:
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "id": 11,                    ⬅️ ID bu yerda
    "phone": "+998901234567",
    "role": "user",
    "first_name": "",
    "last_name": "",
    "passport_id": "",
    "address": "",
    "is_verified": true,
    "houses": []
  },
  "available_roles": [...]
}
```

---

### 2. Profile (GET/PUT/PATCH/POST)
**Endpoint:** `/api/users/profile/`

**GET - Profile olish:**
```json
GET /api/users/profile/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}

Response:
{
  "id": 8,                       ⬅️ ID to'g'ridan-to'g'ri
  "phone": "+998901234567",
  "role": "user",
  "first_name": "John",
  "last_name": "Doe",
  "passport_id": "AB1234567",
  "address": "Tashkent",
  "is_verified": true,
  "houses": [...]
}
```

**PUT/PATCH - Profile yangilash:**
```json
PUT /api/users/profile/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}
{
  "first_name": "John",
  "last_name": "Doe",
  "passport_id": "AB1234567",
  "address": "Tashkent, Chilonzor"
}

Response: (Same as GET)
```

**POST - Profile yaratish:**
```json
POST /api/users/profile/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}
{
  "first_name": "John",
  "last_name": "Doe"
}

Response: (Same as GET)
```

---

### 3. Token Refresh
**Endpoint:** `POST /api/users/token/refresh/`

```json
POST /api/users/token/refresh/
{
  "refresh": "eyJhbGci..."
}

Response:
{
  "access": "new_token_here..."
}
```

---

### 4. User Sessions
**Endpoint:** `GET /api/users/sessions/`

```json
GET /api/users/sessions/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}

Response:
[
  {
    "id": 1,
    "device_name": "Chrome",
    "device_id": "web-browser",
    "ip_address": "127.0.0.1",
    "last_activity": "2024-12-24T10:30:00Z",
    "is_active": true
  }
]
```

---

### 5. Logout Device
**Endpoint:** `POST /api/users/logout-device/`

```json
POST /api/users/logout-device/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}
{
  "device_id": "web-browser"
}
```

---

### 6. Logout All Devices
**Endpoint:** `POST /api/users/logout-all/`

```json
POST /api/users/logout-all/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}
```

---

### 7. Available Roles
**Endpoint:** `GET /api/users/roles/`

```json
GET /api/users/roles/

Response:
[
  {"value": "super_admin", "label": "Super Admin", "level": 4},
  {"value": "government", "label": "Government Officer", "level": 3},
  {"value": "mahalla_admin", "label": "Neighborhood Admin", "level": 2},
  {"value": "user", "label": "User", "level": 1}
]
```

---

### 8. User List (Admin)
**Endpoint:** `/api/users/list/`

```json
GET /api/users/list/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}

Response:
[
  {
    "id": 1,
    "phone": "+998901234567",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_verified": true,
    "houses": [...]
  }
]
```

**GET specific user:**
```json
GET /api/users/list/1/
```

**POST - Create user:**
```json
POST /api/users/list/
{
  "phone": "+998901234567",
  "first_name": "John",
  "role": "user"
}
```

**PUT/PATCH - Update user:**
```json
PUT /api/users/list/1/
{
  "first_name": "Updated Name"
}
```

**DELETE - Delete user:**
```json
DELETE /api/users/list/1/
```

---

## 🏘️ REGIONS, DISTRICTS, NEIGHBORHOODS

### 9. Regions (Viloyatlar)
**Base:** `/api/regions/`

**List all regions:**
```json
GET /api/regions/

Response:
[
  {
    "id": 1,
    "name": "Tashkent",
    "districts": [...]
  }
]
```

**Get specific region:**
```json
GET /api/regions/1/
```

**Create region:**
```json
POST /api/regions/
{
  "name": "Tashkent",
  "districts": [
    {
      "name": "Chilonzor",
      "neighborhoods": [
        {"name": "Chilonzor-1"},
        {"name": "Chilonzor-2"}
      ]
    }
  ]
}
```

**Update region:**
```json
PUT /api/regions/1/
{
  "name": "Tashkent City"
}
```

**Delete region:**
```json
DELETE /api/regions/1/
```

---

### 10. Nested Districts in Region
**Endpoint:** `/api/regions/{id}/districts/`

**List districts of region:**
```json
GET /api/regions/1/districts/

Response:
[
  {
    "id": 1,
    "name": "Chilonzor",
    "region": 1,
    "neighborhoods": [...]
  }
]
```

**Create district in region:**
```json
POST /api/regions/1/districts/
{
  "name": "New District",
  "neighborhoods": [
    {"name": "Neighborhood-1"}
  ]
}
```

---

### 11. Districts (Tumanlar)
**Base:** `/api/districts/`

**List all districts:**
```json
GET /api/districts/

Response:
[
  {
    "id": 1,
    "name": "Chilonzor",
    "region": 1,
    "neighborhoods": [...]
  }
]
```

**Get specific district:**
```json
GET /api/districts/1/
```

**Create district:**
```json
POST /api/districts/
{
  "name": "Chilonzor",
  "region": 1,
  "neighborhoods": [
    {"name": "Chilonzor-1"}
  ]
}
```

**Update district:**
```json
PUT /api/districts/1/
{
  "name": "Updated District"
}
```

**Delete district:**
```json
DELETE /api/districts/1/
```

---

### 12. Nested Neighborhoods in District
**Endpoint:** `/api/districts/{id}/neighborhoods/`

**List neighborhoods of district:**
```json
GET /api/districts/1/neighborhoods/

Response:
[
  {
    "id": 1,
    "name": "Chilonzor-1",
    "district": 1
  }
]
```

**Create neighborhood in district:**
```json
POST /api/districts/1/neighborhoods/
{
  "name": "New Neighborhood"
}
```

---

### 13. Neighborhoods (Mahallalar)
**Base:** `/api/neighborhoods/`

**List all neighborhoods:**
```json
GET /api/neighborhoods/

Response:
[
  {
    "id": 1,
    "name": "Chilonzor-1",
    "district": 1
  }
]
```

**Get specific neighborhood:**
```json
GET /api/neighborhoods/1/
```

**Create neighborhood:**
```json
POST /api/neighborhoods/
{
  "name": "Chilonzor-1",
  "district": 1
}
```

**Update neighborhood:**
```json
PUT /api/neighborhoods/1/
{
  "name": "Updated Neighborhood"
}
```

**Delete neighborhood:**
```json
DELETE /api/neighborhoods/1/
```

---

## 📱 QR CODES

### 14. QR Code List
**Endpoint:** `GET /api/qrcodes/`

```json
GET /api/qrcodes/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}

Response:
[
  {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "house": {
      "id": 5,
      "address": "Street 123",
      "mahalla": "Chilonzor-1"
    },
    "created_at": "2024-12-24T10:00:00Z"
  }
]
```

---

### 15. QR Code Create
**Endpoint:** `POST /api/qrcodes/create/`

```json
POST /api/qrcodes/create/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}
{
  "house_id": 5
}

Response:
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "house": {...},
  "qr_code_image": "/media/qr_codes/xxx.png"
}
```

---

### 16. QR Code Detail
**Endpoint:** `GET /api/qrcodes/{uuid}/`

```json
GET /api/qrcodes/123e4567-e89b-12d3-a456-426614174000/
```

---

### 17. Scan QR Code (User Workflow)
**Endpoint:** `POST /api/qrcodes/scan/{uuid}/`

```json
POST /api/qrcodes/scan/123e4567-e89b-12d3-a456-426614174000/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}

Response:
{
  "message": "QR code scanned successfully",
  "house": {
    "id": 5,
    "address": "Street 123",
    "mahalla": "Chilonzor-1",
    "district": "Chilonzor",
    "region": "Tashkent",
    "owner": null
  },
  "is_claimed": false
}
```

---

### 18. Claim House (User Workflow)
**Endpoint:** `POST /api/qrcodes/claim/{uuid}/`

```json
POST /api/qrcodes/claim/123e4567-e89b-12d3-a456-426614174000/
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}

Response:
{
  "message": "House claimed successfully",
  "house": {
    "id": 5,
    "address": "Street 123",
    "owner": {
      "id": 8,
      "phone": "+998901234567"
    }
  }
}
```

---

## 🔑 AUTHENTICATION HEADERS

Barcha protected endpoint'lar uchun:

```javascript
headers: {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer eyJhbGci...'  // access token
}
```

---

## ⚠️ ERROR RESPONSES

```json
// 400 Bad Request
{
  "error": "Invalid phone number format",
  "field": "phone"
}

// 401 Unauthorized
{
  "error": "Authentication required"
}

// 404 Not Found
{
  "error": "Resource not found"
}

// 500 Internal Server Error
{
  "error": "Server error"
}
```

---

## 📋 FULL ENDPOINT LIST

### Users:
- `POST /api/users/auth/` - SMS yuborish / Login
- `GET /api/users/profile/` - Profile olish
- `PUT/PATCH/POST /api/users/profile/` - Profile yangilash
- `POST /api/users/token/refresh/` - Token yangilash
- `GET /api/users/sessions/` - User sessions
- `POST /api/users/logout-device/` - Device'dan logout
- `POST /api/users/logout-all/` - Barcha device'lardan logout
- `GET /api/users/roles/` - Available roles
- `GET /api/users/list/` - User list (admin)
- `POST /api/users/list/` - Create user
- `GET /api/users/list/{id}/` - Get user
- `PUT/PATCH /api/users/list/{id}/` - Update user
- `DELETE /api/users/list/{id}/` - Delete user

### Regions:
- `GET /api/regions/` - List regions
- `POST /api/regions/` - Create region
- `GET /api/regions/{id}/` - Get region
- `PUT/PATCH /api/regions/{id}/` - Update region
- `DELETE /api/regions/{id}/` - Delete region
- `GET /api/regions/{id}/districts/` - Get districts of region
- `POST /api/regions/{id}/districts/` - Create district in region

### Districts:
- `GET /api/districts/` - List districts
- `POST /api/districts/` - Create district
- `GET /api/districts/{id}/` - Get district
- `PUT/PATCH /api/districts/{id}/` - Update district
- `DELETE /api/districts/{id}/` - Delete district
- `GET /api/districts/{id}/neighborhoods/` - Get neighborhoods of district
- `POST /api/districts/{id}/neighborhoods/` - Create neighborhood in district

### Neighborhoods:
- `GET /api/neighborhoods/` - List neighborhoods
- `POST /api/neighborhoods/` - Create neighborhood
- `GET /api/neighborhoods/{id}/` - Get neighborhood
- `PUT/PATCH /api/neighborhoods/{id}/` - Update neighborhood
- `DELETE /api/neighborhoods/{id}/` - Delete neighborhood

### QR Codes:
- `GET /api/qrcodes/` - List QR codes
- `POST /api/qrcodes/create/` - Create QR code
- `GET /api/qrcodes/{uuid}/` - Get QR code
- `POST /api/qrcodes/scan/{uuid}/` - Scan QR code
- `POST /api/qrcodes/claim/{uuid}/` - Claim house

### Documentation:
- `GET /swagger/` - Swagger UI documentation
