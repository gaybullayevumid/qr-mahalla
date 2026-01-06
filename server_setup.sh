#!/bin/bash

# QR Mahalla - Server Setup Script
# Bu script VPS serverda birinchi marta o'rnatish uchun

set -e

echo "🔧 QR Mahalla - Server Setup"
echo "================================"

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and required packages
echo "🐍 Installing Python 3.12 and dependencies..."
sudo apt install -y python3.12 python3.12-venv python3-pip python3.12-dev

# Install PostgreSQL
echo "🗄️  Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install -y nginx

# Install Git
echo "📥 Installing Git..."
sudo apt install -y git

# Install other dependencies
echo "📦 Installing other dependencies..."
sudo apt install -y build-essential libpq-dev

# Create project directory
echo "📁 Creating project directory..."
sudo mkdir -p /var/www/qr-mahalla
sudo chown -R $USER:$USER /var/www/qr-mahalla
cd /var/www/qr-mahalla

# Clone repository
echo "📥 Cloning repository..."
read -p "Enter your GitHub repository URL: " REPO_URL
git clone $REPO_URL .

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3.12 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup PostgreSQL database
echo "🗄️  Setting up PostgreSQL database..."
sudo -u postgres psql << EOF
CREATE DATABASE qr_mahalla;
CREATE USER qr_mahalla_user WITH PASSWORD 'change-this-password';
ALTER ROLE qr_mahalla_user SET client_encoding TO 'utf8';
ALTER ROLE qr_mahalla_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE qr_mahalla_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE qr_mahalla TO qr_mahalla_user;
\q
EOF

# Create .env file
echo "📝 Creating environment file..."
cp .env.example .env
echo "⚠️  Please edit /var/www/qr-mahalla/.env and set your environment variables"

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
python manage.py createsuperuser

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Setup Gunicorn service
echo "⚙️  Setting up Gunicorn service..."
sudo tee /etc/systemd/system/qr-mahalla.service > /dev/null << EOF
[Unit]
Description=QR Mahalla Gunicorn daemon
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/qr-mahalla
Environment="PATH=/var/www/qr-mahalla/venv/bin"
EnvironmentFile=/var/www/qr-mahalla/.env
ExecStart=/var/www/qr-mahalla/venv/bin/gunicorn --workers 3 --bind unix:/var/www/qr-mahalla/qr-mahalla.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx
echo "🌐 Setting up Nginx..."
sudo tee /etc/nginx/sites-available/qr-mahalla > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # O'zgartiring

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
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/qr-mahalla /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Start and enable services
echo "▶️  Starting services..."
sudo systemctl start qr-mahalla
sudo systemctl enable qr-mahalla
sudo systemctl restart nginx
sudo systemctl enable nginx

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Edit /var/www/qr-mahalla/.env file with your settings"
echo "2. Update Nginx config: sudo nano /etc/nginx/sites-available/qr-mahalla"
echo "3. Restart services: sudo systemctl restart qr-mahalla nginx"
echo ""
echo "🔒 For SSL certificate (recommended):"
echo "   sudo apt install certbot python3-certbot-nginx"
echo "   sudo certbot --nginx -d your-domain.com -d www.your-domain.com"
echo ""
