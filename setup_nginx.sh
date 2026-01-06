#!/bin/bash

# ========================================
# NGINX SOZLASH (80-port uchun)
# ========================================

echo "🌐 Nginx sozlanmoqda..."
echo ""

PROJECT_NAME="qr-mahalla"
PROJECT_DIR=$(pwd)
SERVER_IP=$(curl -s ifconfig.me)

# 1. Nginx o'rnatish (agar yo'q bo'lsa)
if ! command -v nginx &> /dev/null; then
    echo "📦 Nginx o'rnatilmoqda..."
    sudo apt update
    sudo apt install -y nginx
else
    echo "✅ Nginx o'rnatilgan"
fi

# 2. Nginx config yaratish
echo ""
echo "📝 Nginx config yaratilmoqda..."

sudo tee /etc/nginx/sites-available/$PROJECT_NAME > /dev/null << EOF
server {
    listen 80;
    server_name $SERVER_IP;
    client_max_body_size 20M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 3. Symlink yaratish
echo ""
echo "🔗 Symlink yaratilmoqda..."
sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/

# 4. Default config o'chirish (agar kerak bo'lsa)
if [ -f /etc/nginx/sites-enabled/default ]; then
    echo "🗑️  Default config o'chirilmoqda..."
    sudo rm /etc/nginx/sites-enabled/default
fi

# 5. Nginx test
echo ""
echo "🧪 Nginx config tekshirilmoqda..."
sudo nginx -t

# 6. Nginx restart
echo ""
echo "♻️  Nginx qayta ishga tushirilmoqda..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# 7. Firewall (agar kerak bo'lsa)
if command -v ufw &> /dev/null; then
    echo ""
    echo "🔥 Firewall sozlanmoqda..."
    sudo ufw allow 'Nginx Full'
    sudo ufw allow 8000
fi

echo ""
echo "✅ ======================="
echo "✅ NGINX TAYYOR!"
echo "✅ ======================="
echo ""
echo "🌐 Saytingiz: http://$SERVER_IP"
echo ""
echo "📌 Foydali commandlar:"
echo "   Status:  sudo systemctl status nginx"
echo "   Restart: sudo systemctl restart nginx"
echo "   Logs:    sudo tail -f /var/log/nginx/error.log"
echo ""
