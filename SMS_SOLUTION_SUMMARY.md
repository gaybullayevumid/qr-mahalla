# ✅ SMS KODNI KIRITGANDAN KEYIN USERNI BAZAGA SAQLASH

## 🎯 YECHIM TAYYORLANDI!

---

## 📋 Muammo va Yechim

### ❌ Avvalgi Holat:
SMS kod yuborilganda darhol user bazada yaratilayotgan edi (`User.objects.get_or_create(phone=phone)`). 

**Muammolar:**
- User SMS kod kiritmasdan chiqib ketsa ham bazada qolib ketadi
- Ko'p keraksiz userlar database da to'planadi
- Verified bo'lmagan userlar mavjud

### ✅ Yangi Yechim:
**SMS kod tasdiqlangandan keyingina** user bazaga saqlanadi!

---

## 🔧 O'zgarishlar

### File: `apps/users/views.py`

#### 1. SMS yuborish (Line 45-70)
```python
# Don't create user yet - only create after SMS verification
# Just generate and send OTP

# Invalidate old codes
PhoneOTP.objects.filter(phone=phone, is_used=False).update(is_used=True)

# Generate new code
new_code = PhoneOTP.generate_code()
PhoneOTP.objects.create(phone=phone, code=new_code)

# Send SMS
send_sms(phone, new_code)
```
**⚠️ User hali bazada yaratilmagan!**

#### 2. SMS kod tasdiqlash (Line 111-125)
```python
# Mark OTP as used
otp.is_used = True
otp.save()

# Create user if doesn't exist (SMS kod tasdiqlangandan keyin)
user, created = User.objects.get_or_create(
    phone=phone,
    defaults={
        'is_verified': True,
        'role': 'user',
    }
)

# If user already exists, just verify them
if not created:
    user.is_verified = True
    user.save()
```
**✅ User bazada yaratildi!**

---

## 🔄 Workflow

```
1. User telefon raqam kiritadi
   ↓
2. POST /api/users/auth/ {"phone": "+998901234567"}
   ↓
3. SMS kod yuboriladi
   ⚠️ User hali bazada YO'Q
   ↓
4. User SMS kodni kiritadi
   ↓
5. POST /api/users/auth/ {"phone": "+998...", "code": "123456"}
   ↓
6. Kod tekshiriladi
   ↓
7. ✅ User bazada yaratiladi (is_verified=True)
   ↓
8. Token generatsiya qilinadi
   ↓
9. Response: {access, refresh, user}
```

---

## 📝 API Endpoints

### 1. SMS Yuborish
```
POST /api/users/auth/
Body: {"phone": "+998901234567"}

Response (200):
{
  "message": "SMS code sent",
  "phone": "+998901234567",
  "detail": "Please verify your phone number with the code sent via SMS"
}
```

### 2. SMS Kod Tasdiqlash
```
POST /api/users/auth/
Body: {
  "phone": "+998901234567",
  "code": "123456",
  "device_id": "device_001",
  "device_name": "iPhone 13"
}

Response (200):
{
  "access": "eyJ0eXAiOiJKV1QiLC...",
  "refresh": "eyJ0eXAiOiJKV1QiLC...",
  "user": {
    "phone": "+998901234567",
    "role": "user",
    "first_name": "",
    "last_name": ""
  }
}
```

---

## 🧪 Test Qilish

### Automated Test
```bash
python test_sms_auth.py
```

Test options:
1. To'liq workflow test
2. Faqat SMS yuborish
3. Faqat kod tasdiqlash
4. User mavjudligini tekshirish

### Manual Test

#### Step 1: SMS yuborish
```bash
curl -X POST http://192.168.0.158:8000/api/users/auth/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567"}'
```

#### Step 2: Admin panel dan kodni olish
- URL: `http://192.168.0.158:8000/admin/users/phoneotp/`
- Oxirgi yaratilgan kodni ko'ring

#### Step 3: Kod tasdiqlash
```bash
curl -X POST http://192.168.0.158:8000/api/users/auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+998901234567",
    "code": "123456",
    "device_id": "test_device",
    "device_name": "Test Device"
  }'
```

#### Step 4: User yaratilganini tekshirish
- Admin panel: `http://192.168.0.158:8000/admin/users/user/`
- Telefon raqam bo'yicha qidiring

---

## 📦 Frontend Integration

### JavaScript/React Example
```javascript
// Step 1: Send SMS
async function sendSMS(phone) {
  const response = await fetch('/api/users/auth/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ phone })
  });
  
  const data = await response.json();
  // Show code input form
}

// Step 2: Verify code
async function verifyCode(phone, code) {
  const response = await fetch('/api/users/auth/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      phone,
      code,
      device_id: getDeviceId(),
      device_name: getDeviceName()
    })
  });
  
  const data = await response.json();
  if (response.ok) {
    // User yaratildi va token olindi!
    localStorage.setItem('accessToken', data.access);
    localStorage.setItem('refreshToken', data.refresh);
    // Redirect to home
  }
}
```

---

## ✅ Afzalliklar

1. ✅ **Clean Database** - Faqat SMS tasdiqlagan userlar saqlanadi
2. ✅ **Security** - Hamma userlar verified
3. ✅ **No Orphan Users** - Kod kiritmasdan ketganlar bazada yo'q
4. ✅ **Better Performance** - Kam userlar, tezroq query lar
5. ✅ **Verified by Default** - Barcha userlar `is_verified=True`

---

## 📚 Qo'shimcha Fayllar

1. **SMS_AUTH_WORKFLOW.md** - Batafsil dokumentatsiya
2. **test_sms_auth.py** - Test script
3. **apps/users/views.py** - O'zgartirilgan backend kod

---

## ⚠️ Important Notes

- User **faqat SMS kod tasdiqlangandan keyin** bazaga saqlanadi
- Barcha yangi userlar `is_verified=True` holatda yaratiladi
- Default role: `"user"`
- Token faqat user yaratilgandan keyin generatsiya qilinadi
- OTP kod 2 minut davomida amal qiladi

---

## ✅ SUMMARY

**SMS kodni kiritgandan keyin user bazaga saqlanadi!**

- ❌ SMS yuborilganda → User yaratilmaydi
- ✅ SMS kod tasdiqlanganda → User bazaga saqlanadi

Backend to'liq tayyorlandi va test qilingan! 🎉
