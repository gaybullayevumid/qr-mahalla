# QR Mahalla - Django REST API

## Loyiha haqida
QR kod orqali mahalla uylarini boshqarish tizimi. Bu loyiha Django REST Framework asosida qurilgan.

## Loyiha strukturasi
```
qr-mahalla/
├── apps/                 # Asosiy ilovalar
│   ├── houses/          # Uylar moduli
│   ├── qrcodes/         # QR kodlar moduli
│   ├── regions/         # Mintaqalar moduli
│   ├── scans/           # Skanerlash moduli
│   ├── users/           # Foydalanuvchilar moduli
│   └── utils.py         # Yordamchi funksiyalar
├── config/              # Django sozlamalari
├── docs/                # Hujjatlar
├── media/               # Media fayllar
├── manage.py           # Django boshqaruv fayli
├── requirements.txt    # Python kutubxonalar
└── README.md           # Bu fayl
```

## O'rnatish

1. Virtual muhitni yaratish:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

3. Ma'lumotlar bazasini yaratish:
```bash
python manage.py migrate
```

4. Serverni ishga tushirish:
```bash
python manage.py runserver
```

## API Hujjatlari
Batafsil API hujjatlarini `docs/` papkasida topishingiz mumkin:
- [API_ENDPOINTS.md](docs/API_ENDPOINTS.md) - API endpoint'lar
- [FRONTEND_INTEGRATION.md](docs/FRONTEND_INTEGRATION.md) - Frontend integratsiya
- [SMS_AUTH_WORKFLOW.md](docs/SMS_AUTH_WORKFLOW.md) - SMS autentifikatsiya

## Lisenziya
© 2025 QR Mahalla