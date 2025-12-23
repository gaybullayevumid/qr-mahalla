# Region → Districts → Mahallas - To'liq Nested CRUD

## ✅ 3 Darajali Nested CRUD Ishlaydi

### 1️⃣ Region yaratish (districts va mahallas bilan birga):

```http
POST /api/regions/regions/
```

**Request Body:**
```json
{
  "name": "Farg'ona viloyati",
  "districts": [
    {
      "name": "Farg'ona tumani",
      "mahallas": [
        {
          "name": "Dehqonobod",
          "admin": null
        },
        {
          "name": "Navbahor",
          "admin": null
        }
      ]
    },
    {
      "name": "Beshariq tumani",
      "mahallas": [
        {
          "name": "Yangi mahalla",
          "admin": null
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "id": 16,
  "name": "Farg'ona viloyati",
  "districts": [...]
}
```

---

### 2️⃣ Region yangilash (districts va mahallas CRUD):

```http
PATCH /api/regions/regions/16/
```

#### A) Mavjud districtni yangilash:
```json
{
  "districts": [
    {
      "id": 1,
      "name": "Farg'ona tumani (o'zgartirilgan)",
      "mahallas": [
        {
          "id": 5,
          "name": "Dehqonobod (yangilangan)",
          "admin": 2
        }
      ]
    }
  ]
}
```

#### B) Yangi district qo'shish:
```json
{
  "districts": [
    {
      "id": 1,
      "name": "Mavjud tuman",
      "mahallas": [...]
    },
    {
      "name": "Yangi tuman",
      "mahallas": [
        {
          "name": "Yangi mahalla"
        }
      ]
    }
  ]
}
```

#### C) Mahalla qo'shish/o'zgartirish/o'chirish:
```json
{
  "districts": [
    {
      "id": 1,
      "name": "Farg'ona tumani",
      "mahallas": [
        {
          "id": 5,
          "name": "Mavjud mahalla (yangilangan)"
        },
        {
          "name": "Yangi mahalla"
        }
      ]
    }
  ]
}
```

#### D) District o'chirish (listda ko'rsatmaslik):
```json
{
  "districts": [
    {
      "id": 1,
      "name": "Qoldirilgan yagona tuman"
    }
  ]
}
```
*Listda yo'q bo'lgan barcha districts o'chiriladi*

---

### 3️⃣ Region ko'rish (barcha nested ma'lumotlar bilan):

```http
GET /api/regions/regions/16/
```

**Response:**
```json
{
  "id": 16,
  "name": "Farg'ona viloyati",
  "districts": [
    {
      "id": 1,
      "name": "Farg'ona tumani",
      "neighborhoods": [
        {
          "id": 5,
          "name": "Dehqonobod",
          "admin": 2,
          "admin_name": "Ali Valiyev",
          "users": [8, 15, 23]
        }
      ]
    }
  ]
}
```

---

### 4️⃣ District alohida yangilash (mahallas bilan):

```http
PATCH /api/regions/districts/1/
```

```json
{
  "name": "Farg'ona tumani",
  "region": 16,
  "mahallas": [
    {
      "id": 5,
      "name": "Dehqonobod",
      "admin": 2
    },
    {
      "name": "Yangi mahalla",
      "admin": null
    }
  ]
}
```

---

## 🎯 Xususiyatlar:

✅ **Region CRUD** - Create, Read, Update, Delete
✅ **Districts CRUD** - Region ichida nested
✅ **Mahallas CRUD** - Districts ichida nested
✅ **3 Daraja Nested** - Region → Districts → Mahallas
✅ **ID bilan Update** - `id` ko'rsatilsa yangilaydi
✅ **ID yo'q - Create** - `id` bo'lmasa yangi yaratadi
✅ **Listda yo'q - Delete** - Listda bo'lmasa o'chiriladi

---

## 📝 Qoidalar:

1. **Yaratish:** `id` ni ko'rsatmaslik
2. **Yangilash:** `id` ni ko'rsatish
3. **O'chirish:** Listdan olib tashlash
4. **Saqlab qolish:** Listda qoldirish

---

## Endpoint Summary:

- `POST /api/regions/regions/` - Region + Districts + Mahallas yaratish
- `PUT/PATCH /api/regions/regions/{id}/` - Region + nested CRUD
- `GET /api/regions/regions/{id}/` - To'liq ma'lumot
- `PATCH /api/regions/districts/{id}/` - District + Mahallas CRUD
- `PATCH /api/regions/mahallas/{id}/` - Mahalla yangilash

**Barcha 3 daraja to'liq CRUD qo'llab-quvvatlanadi!** ✅
