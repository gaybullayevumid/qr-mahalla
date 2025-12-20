# API Endpoint Changes - Mahallas to Neighborhoods

## 🔄 O'zgargan URL'lar

### Eski URL → Yangi URL

| Eski Endpoint | Yangi Endpoint | Tavsif |
|--------------|----------------|--------|
| `GET /api/regions/mahallas/` | `GET /api/regions/neighborhoods/` | Barcha mahallalar ro'yxati |
| `POST /api/regions/mahallas/` | `POST /api/regions/neighborhoods/` | Yangi mahalla yaratish |
| `GET /api/regions/mahallas/{id}/` | `GET /api/regions/neighborhoods/{id}/` | Mahalla detallari |
| `PUT /api/regions/mahallas/{id}/` | `PUT /api/regions/neighborhoods/{id}/` | Mahallani yangilash |
| `DELETE /api/regions/mahallas/{id}/` | `DELETE /api/regions/neighborhoods/{id}/` | Mahallani o'chirish |

## 📝 Response Format O'zgarishlari

### Region Response
```json
{
  "id": 1,
  "name": "Toshkent",
  "districts": [
    {
      "id": 5,
      "name": "Chilonzor",
      "neighborhoods": [    // ❌ Eski: "mahallas"
        {
          "id": 25,
          "name": "Qatortol",
          "admin": 15,
          "admin_name": "Anvar Mahmudov"
        }
      ]
    }
  ]
}
```

## 🎯 Backend O'zgarishlari

### 1. URLs (apps/regions/urls.py)
```python
# ❌ Eski
router.register("mahallas", MahallaViewSet, basename="mahalla")

# ✅ Yangi  
router.register("neighborhoods", MahallaViewSet, basename="neighborhood")
```

### 2. Serializers (apps/regions/serializers.py)
```python
# DistrictNestedSerializer
class DistrictNestedSerializer(serializers.ModelSerializer):
    # ❌ Eski
    # mahallas = MahallaNestedSerializer(many=True, read_only=True)
    # fields = ("id", "name", "mahallas")
    
    # ✅ Yangi
    neighborhoods = MahallaNestedSerializer(many=True, read_only=True, source='mahallas')
    fields = ("id", "name", "neighborhoods")
```

## 🚀 Frontend Integration

### Yangi API Chaqiruvlari

```javascript
// Barcha neighborhoods olish
const response = await fetch('/api/regions/neighborhoods/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Bitta neighborhood olish  
const neighborhood = await fetch(`/api/regions/neighborhoods/${id}/`, {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Region ichidagi districts va neighborhoods
const region = await fetch(`/api/regions/regions/${regionId}/`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
// Response: { id, name, districts: [{ id, name, neighborhoods: [...] }] }
```

## ⚠️ Migration Kerak Emas

**Eslatma:** Database modellarida hech qanday o'zgarish yo'q. Faqat API endpoint nomlari va response field nomlari o'zgardi:
- Database'dagi `related_name="mahallas"` saqlanadi
- Faqat API'da ko'rinish o'zgardi (`source='mahallas'` orqali)

## 📋 Tekshirish Ro'yxati

- [x] URL endpoints o'zgartirildi
- [x] Serializer field nomlari yangilandi
- [x] Server xatosiz ishlamoqda
- [ ] Frontend kod yangilash kerak
- [ ] Test fayllar yangilash kerak  
- [ ] Documentation yangilash kerak

## 💡 Frontend Developers Uchun

**Eski kod:**
```javascript
// ❌ O'zgartirish kerak
fetch('/api/regions/mahallas/')
region.districts[0].mahallas
```

**Yangi kod:**
```javascript
// ✅ Yangi format
fetch('/api/regions/neighborhoods/')
region.districts[0].neighborhoods
```

## 🔗 Qo'shimcha Ma'lumot

Barcha endpoint'lar [OPTIMIZED_WORKFLOW.md](OPTIMIZED_WORKFLOW.md) faylida yangilangan holda mavjud.
