# ✅ SMS Authentication Workflow - User Yaratish

## 📋 O'zgarishlar

### ❌ Avvalgi Muammo:
SMS kod yuborilganda darhol user bazada yaratilayotgan edi:
```python
# Old code (line 49)
user, created = User.objects.get_or_create(phone=phone)
```

Bu muammo edi, chunki:
- User SMS kod kiritmasdan chiqib ketsa ham bazada qolib ketadi
- Ko'p foydalanuvchilar kod kiritmasdan ro'yxatdan o'tgan bo'lib qoladi
- Database keraksiz userlar bilan to'ladi

### ✅ Yangi Yechim:
SMS kod **tasdiqlangandan keyingina** user bazada yaratiladi:
```python
# New code (line 111-120)
# Create user if doesn't exist (SMS kod tasdiqlangandan keyin)
user, created = User.objects.get_or_create(
    phone=phone,
    defaults={
        'is_verified': True,
        'role': 'user',
    }
)
```

---

## 🔄 Yangi Workflow

### 1. SMS Kod Yuborish (POST /api/users/auth/)
```json
Request:
{
  "phone": "+998901234567"
}

Response (200 OK):
{
  "message": "SMS code sent",
  "phone": "+998901234567",
  "detail": "Please verify your phone number with the code sent via SMS"
}
```
**⚠️ User hali bazada yaratilmagan!**

### 2. SMS Kod Tasdiqlash (POST /api/users/auth/)
```json
Request:
{
  "phone": "+998901234567",
  "code": "123456",
  "device_id": "device_001",
  "device_name": "iPhone 13"
}

Response (200 OK):
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
**✅ User bazada yaratildi va verified!**

---

## 📝 O'zgartirilgan Kodlar

### File: `apps/users/views.py`

#### 1. SMS Yuborishda User Yaratmaslik (Lines 45-70)
```python
# If no code provided → send SMS
if not code:
    # Don't create user yet - only create after SMS verification
    # Just generate and send OTP
    
    # Invalidate old codes
    PhoneOTP.objects.filter(phone=phone, is_used=False).update(is_used=True)

    # Generate new code
    new_code = PhoneOTP.generate_code()
    PhoneOTP.objects.create(phone=phone, code=new_code)

    # Send SMS
    try:
        send_sms(phone, new_code)
        return Response(
            {
                "message": "SMS code sent", 
                "phone": phone,
                "detail": "Please verify your phone number with the code sent via SMS"
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"error": "Error sending SMS"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
```

#### 2. SMS Kod Tasdiqlashda User Yaratish (Lines 72-125)
```python
# If code provided → verify and return token
else:
    # Normalize phone number for comparison
    phone = phone.strip()
    code = code.strip()

    # Check OTP code first (before checking user)
    otp = (
        PhoneOTP.objects.filter(phone=phone, code=code, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if not otp:
        # Debug: show what codes exist for this phone
        all_codes = PhoneOTP.objects.filter(phone=phone).order_by(
            "-created_at"
        )[:3]
        debug_info = [
            f"Code: {c.code}, Used: {c.is_used}, Created: {c.created_at}"
            for c in all_codes
        ]
        return Response(
            {
                "error": "Code is incorrect or already used",
                "debug": f"Looking for code '{code}' for phone '{phone}'",
                "recent_codes": debug_info if settings.DEBUG else None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if otp.is_expired():
        return Response(
            {"error": "Code has expired. Please request a new code"},
            status=status.HTTP_400_BAD_REQUEST,
        )

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

    # Get device info from request
    device_id = request.data.get("device_id", "unknown")
    device_name = request.data.get("device_name", "")

    # Create JWT token
    refresh = RefreshToken.for_user(user)

    # Create or update session
    session, created = UserSession.objects.update_or_create(
        user=user,
        device_id=device_id,
        defaults={
            "device_name": device_name,
            "refresh_token": str(refresh),
            "ip_address": get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "is_active": True,
        },
    )

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "phone": user.phone,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        },
        status=status.HTTP_200_OK,
    )
```

---

## 🧪 Test Qilish

### 1. Backend ishga tushirish
```bash
cd c:\Users\VICTUS\Desktop\qr-mahalla
.\env\Scripts\activate
python manage.py runserver 192.168.0.158:8000
```

### 2. Test script ishga tushirish
```bash
python test_sms_auth.py
```

Test script quyidagilarni tekshiradi:
1. ✅ SMS kod yuborish (user yaratilmaydi)
2. ✅ Noto'g'ri kod bilan test (user yaratilmaydi)
3. ✅ To'g'ri kod bilan test (user yaratiladi)

### 3. Manual test (curl yoki Postman)

#### Step 1: SMS yuborish
```bash
curl -X POST http://192.168.0.158:8000/api/users/auth/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567"}'
```

#### Step 2: Kod tasdiqlash
```bash
# Admin panel dan yoki console dan kodni oling
# http://192.168.0.158:8000/admin/users/phoneotp/

curl -X POST http://192.168.0.158:8000/api/users/auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+998901234567",
    "code": "123456",
    "device_id": "test_device",
    "device_name": "Test Device"
  }'
```

#### Step 3: User yaratilganini tekshirish
```bash
# Admin panel:
# http://192.168.0.158:8000/admin/users/user/
```

---

## 📊 Database Tables

### User Model (apps/users/models.py)
```python
class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    passport_id = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=20, default="user")
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # ✅ SMS kod tasdiqlangandan keyin True
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
```

### PhoneOTP Model (apps/users/models.py)
```python
class PhoneOTP(models.Model):
    phone = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)  # ✅ Kod tasdiqlangandan keyin True
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 🎯 Frontend Integration

### React Example

```javascript
// Step 1: Send SMS
const sendSMS = async (phone) => {
  const response = await fetch('http://192.168.0.158:8000/api/users/auth/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone })
  });
  
  const data = await response.json();
  if (response.ok) {
    console.log('SMS sent!');
    // Show code input form
  }
};

// Step 2: Verify SMS code
const verifyCode = async (phone, code) => {
  const response = await fetch('http://192.168.0.158:8000/api/users/auth/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone,
      code,
      device_id: getDeviceId(), // Generate unique device ID
      device_name: getDeviceName() // e.g., "iPhone 13"
    })
  });
  
  const data = await response.json();
  if (response.ok) {
    // Save tokens
    localStorage.setItem('accessToken', data.access);
    localStorage.setItem('refreshToken', data.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    // User yaratildi va bazaga saqlandi!
    console.log('User created and logged in:', data.user);
    // Redirect to home
  }
};
```

---

## ✅ Afzalliklar

1. **Clean Database** - Faqat tasdiqlangan userlar bazada saqlanadi
2. **Security** - SMS kod to'g'ri kiritilgan userlar ro'yxatdan o'tadi
3. **No Orphan Users** - Kod kiritmasdan ketgan userlar bazada qolmaydi
4. **Verified Users** - Barcha userlar `is_verified=True` bilan yaratiladi
5. **Better UX** - User faqat SMS kod tasdiqlangandan keyin tizimga kiradi

---

## ⚠️ Important Notes

1. **User yaratilish vaqti**: SMS kod tasdiqlangandan keyin
2. **is_verified field**: Avtomatik `True` qo'yiladi
3. **Default role**: `"user"` qilib yaratiladi
4. **Token generation**: User yaratilgandan keyingina
5. **Session tracking**: Device ID bilan tracking qilinadi

---

## 🔍 Debugging

Agar user yaratilmasa:
1. SMS kod to'g'ri kiritilganini tekshiring
2. Kod expire bo'lmaganini tekshiring (2 minutdan kam)
3. Kod allaqachon ishlatilmaganini tekshiring
4. Admin panel da PhoneOTP ni tekshiring

```bash
# Django shell
python manage.py shell

from apps.users.models import User, PhoneOTP

# Check if user exists
User.objects.filter(phone="+998901234567").exists()

# Check OTP codes
PhoneOTP.objects.filter(phone="+998901234567").order_by('-created_at')[:5]
```

---

## ✅ Summary

✅ SMS kod yuborilganda user yaratilmaydi
✅ SMS kod tasdiqlanganda user bazaga saqlanadi
✅ User avtomatik verified holatda yaratiladi
✅ Token faqat user yaratilgandan keyin generatsiya qilinadi
✅ Database clean va optimized

**SMS kod kiritgandan keyin user bazaga saqlanadi!** ✅
