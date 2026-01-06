# QR Mahalla - Deploy qo'llanma

## GitHub orqali avtomatik deploy

### 1. GitHub Secrets sozlash

GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Quyidagi secretlarni qo'shing:

- `VPS_HOST`: VPS IP manzili (masalan: `185.196.213.45`)
- `VPS_USERNAME`: SSH username (odatda `root`)
- `VPS_PASSWORD`: SSH password

### 2. Birinchi marta server sozlash

VPS ga SSH orqali ulanib, quyidagi commandlarni bajaring:

```bash
# Server setup scriptni yuklab oling
wget https://raw.githubusercontent.com/your-username/qr-mahalla/main/server_setup.sh

# Scriptga ruxsat bering
chmod +x server_setup.sh

# Scriptni ishga tushiring
./server_setup.sh
```

Yoki qo'lda:

```bash
# 1. Sistemani yangilash
sudo apt update && sudo apt upgrade -y

# 2. Python va kerakli paketlarni o'rnatish
sudo apt install -y python3.12 python3.12-venv python3-pip git nginx postgresql postgresql-contrib build-essential libpq-dev

# 3. Loyiha katalogini yaratish
sudo mkdir -p /var/www/qr-mahalla
sudo chown -R $USER:$USER /var/www/qr-mahalla
cd /var/www/qr-mahalla

# 4. Repositoryni clone qilish
git clone https://github.com/your-username/qr-mahalla.git .

# 5. Virtual environment yaratish
python3.12 -m venv venv
source venv/bin/activate

# 6. Paketlarni o'rnatish
pip install --upgrade pip
pip install -r requirements.txt psycopg2-binary

# 7. PostgreSQL database yaratish
sudo -u postgres psql
```

PostgreSQL da:
```sql
CREATE DATABASE qr_mahalla;
CREATE USER qr_mahalla_user WITH PASSWORD 'your_strong_password';
ALTER ROLE qr_mahalla_user SET client_encoding TO 'utf8';
ALTER ROLE qr_mahalla_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE qr_mahalla_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE qr_mahalla TO qr_mahalla_user;
\q
```

```bash
# 8. .env fayl yaratish
nano .env
```

`.env` faylga quyidagilarni yozing:
```env
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,vps-ip

DB_ENGINE=django.db.backends.postgresql
DB_NAME=qr_mahalla
DB_USER=qr_mahalla_user
DB_PASSWORD=your_strong_password
DB_HOST=localhost
DB_PORT=5432

TELEGRAM_BOT_TOKEN=8443848056:AAFSUPSsd4OusBcmC10KODDzxbRi3VfSwdY
TELEGRAM_BOT_USERNAME=qrmahallabot
TELEGRAM_CHAT_IDS=8055309446,5323321097
```

```bash
# 9. Migration va static files
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# 10. Gunicorn service sozlash
sudo nano /etc/systemd/system/qr-mahalla.service
```

Service fayl:
```ini
[Unit]
Description=QR Mahalla Gunicorn daemon
After=network.target

[Service]
User=your-username
Group=www-data
WorkingDirectory=/var/www/qr-mahalla
Environment="PATH=/var/www/qr-mahalla/venv/bin"
EnvironmentFile=/var/www/qr-mahalla/.env
ExecStart=/var/www/qr-mahalla/venv/bin/gunicorn --workers 3 --bind unix:/var/www/qr-mahalla/qr-mahalla.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# 11. Nginx sozlash
sudo nano /etc/nginx/sites-available/qr-mahalla
```

Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/qr-mahalla/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/qr-mahalla/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/qr-mahalla/qr-mahalla.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

```bash
# 12. Nginx aktivlashtirish
sudo ln -s /etc/nginx/sites-available/qr-mahalla /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 13. Service ishga tushirish
sudo systemctl start qr-mahalla
sudo systemctl enable qr-mahalla
sudo systemctl status qr-mahalla

# 14. Firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### 3. SSL sertifikat (HTTPS)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 4. Keyingi deploylar

GitHub ga `main` branchga push qilganingizda avtomatik deploy bo'ladi:

```bash
git add .
git commit -m "Update"
git push origin main
```

### Foydali commandlar

```bash
# Service holatini ko'rish
sudo systemctl status qr-mahalla

# Service restart
sudo systemctl restart qr-mahalla

# Loglarni ko'rish
sudo journalctl -u qr-mahalla -f

# Nginx restart
sudo systemctl restart nginx

# Manual deploy
cd /var/www/qr-mahalla
./deploy.sh
```

## Muammolarni hal qilish

### Database migration xatolari
```bash
cd /var/www/qr-mahalla
source venv/bin/activate
python manage.py migrate --fake-initial
```

### Static files yuklanmasa
```bash
python manage.py collectstatic --clear --noinput
sudo systemctl restart qr-mahalla
```

### Permission xatolari
```bash
sudo chown -R $USER:www-data /var/www/qr-mahalla
sudo chmod -R 755 /var/www/qr-mahalla
```
