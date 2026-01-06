#!/bin/bash

# QR Mahalla - Deploy Script
# Bu script VPS serverda deploy qilish uchun

set -e

echo "🚀 Starting deployment..."

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Restart service
echo "♻️  Restarting service..."
sudo systemctl restart qr-mahalla

echo "✅ Deployment completed successfully!"
