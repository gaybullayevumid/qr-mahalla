#!/bin/bash

# ========================================
# QR MAHALLA - SODDA PRODUCTION SETUP
# ========================================

echo "🚀 QR Mahalla Production Setup boshlandi..."
echo ""

# 1. Proyekt yo'lini aniqlash
PROJECT_DIR=$(pwd)
PROJECT_NAME="qr-mahalla"
USER_NAME=$(whoami)

echo "📁 Proyekt: $PROJECT_DIR"
echo "👤 User: $USER_NAME"
echo ""

# 2. Gunicorn o'rnatilganligini tekshirish
echo "📦 Gunicorn tekshirilmoqda..."
if ! pip show gunicorn > /dev/null 2>&1; then
    echo "⚠️  Gunicorn topilmadi. O'rnatilmoqda..."
    pip install gunicorn
else
    echo "✅ Gunicorn o'rnatilgan"
fi

# 3. Systemd service yaratish
echo ""
echo "⚙️  Systemd service yaratilmoqda..."

sudo tee /etc/systemd/system/$PROJECT_NAME.service > /dev/null << EOF
[Unit]
Description=QR Mahalla Gunicorn Service
After=network.target

[Service]
Type=notify
User=$USER_NAME
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn config.wsgi:application --workers 3 --bind 0.0.0.0:8000
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service fayl yaratildi: /etc/systemd/system/$PROJECT_NAME.service"

# 4. Systemd reload
echo ""
echo "🔄 Systemd reload qilinmoqda..."
sudo systemctl daemon-reload

# 5. Service yoqish va ishga tushirish
echo ""
echo "▶️  Service ishga tushirilmoqda..."
sudo systemctl enable $PROJECT_NAME
sudo systemctl start $PROJECT_NAME

# 6. Status tekshirish
echo ""
echo "📊 Service holati:"
sudo systemctl status $PROJECT_NAME --no-pager

echo ""
echo "✅ ======================="
echo "✅ TAYYOR!"
echo "✅ ======================="
echo ""
echo "📌 Foydali commandlar:"
echo "   Status:  sudo systemctl status $PROJECT_NAME"
echo "   Stop:    sudo systemctl stop $PROJECT_NAME"
echo "   Start:   sudo systemctl start $PROJECT_NAME"
echo "   Restart: sudo systemctl restart $PROJECT_NAME"
echo "   Logs:    sudo journalctl -u $PROJECT_NAME -f"
echo ""
echo "🌐 Server manzil: http://$(curl -s ifconfig.me):8000"
echo ""
