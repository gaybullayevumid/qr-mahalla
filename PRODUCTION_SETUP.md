# ========================================
# QR MAHALLA - PRODUCTION SETUP
# ========================================

## SERVERDA BAJARILADIGAN COMMANDLAR

### 1️⃣ GUNICORN + SYSTEMD (ASOSIY)

```bash
# Proyekt papkasiga o'tish
cd /root/qr-mahalla  # yoki sizning proyekt yo'lingiz

# Virtual environment aktivlashtirish (agar bor bo'lsa)
source venv/bin/activate

# Setup scriptni ishga tushirish
chmod +x setup_production.sh
./setup_production.sh
```

**❗ TAYYOR! Server 24/7 ishlaydi**

---

### 2️⃣ NGINX SOZLASH (80-port uchun, ixtiyoriy)

```bash
chmod +x setup_nginx.sh
./setup_nginx.sh
```

Server: `http://VPS_IP_MANZIL`

---

## 📌 FOYDALI COMMANDLAR

### Service boshqarish
```bash
# Holatni ko'rish
sudo systemctl status qr-mahalla

# To'xtatish
sudo systemctl stop qr-mahalla

# Ishga tushirish
sudo systemctl start qr-mahalla

# Qayta ishga tushirish
sudo systemctl restart qr-mahalla

# Loglarni ko'rish
sudo journalctl -u qr-mahalla -f
```

### Kod yangilash (update)
```bash
cd /root/qr-mahalla
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart qr-mahalla
```

### Nginx
```bash
# Holatni ko'rish
sudo systemctl status nginx

# Qayta ishga tushirish
sudo systemctl restart nginx

# Loglar
sudo tail -f /var/log/nginx/error.log
```

---

## 🔧 MUAMMOLAR VA YECHIMLAR

### Service ishlamasa
```bash
# Loglarni ko'rish
sudo journalctl -u qr-mahalla -n 50 --no-pager

# Service qayta yoqish
sudo systemctl daemon-reload
sudo systemctl restart qr-mahalla
```

### Port band bo'lsa
```bash
# 8000-portda ishlab turgan processni topish
sudo lsof -i :8000

# Processni to'xtatish
sudo kill -9 PID_RAQAMI
```

### Static files yuklanmasa
```bash
cd /root/qr-mahalla
source venv/bin/activate
python manage.py collectstatic --clear --noinput
sudo systemctl restart qr-mahalla
```

---

## 📋 QISQA SETUP (agar script ishlamasa)

```bash
# 1. Service fayl yaratish
sudo nano /etc/systemd/system/qr-mahalla.service
```

Ichiga yozing:
```ini
[Unit]
Description=QR Mahalla Gunicorn Service
After=network.target

[Service]
Type=notify
User=root
Group=www-data
WorkingDirectory=/root/qr-mahalla
ExecStart=/root/qr-mahalla/venv/bin/gunicorn config.wsgi:application --workers 3 --bind 0.0.0.0:8000
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Service ishga tushirish
sudo systemctl daemon-reload
sudo systemctl enable qr-mahalla
sudo systemctl start qr-mahalla
sudo systemctl status qr-mahalla
```

**✅ TAYYOR!**

Server: `http://VPS_IP:8000`
