#!/bin/bash

# Update script for Zimmer Platform
# This script updates the application without downtime

set -e

APP_DIR="/opt/zimmer"
BACKUP_DIR="/opt/backups/zimmer"

echo "🔄 Updating Zimmer Platform..."

# Create backup
echo "Creating backup..."
sudo mkdir -p $BACKUP_DIR
sudo cp -r $APP_DIR $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S)

# Update code
echo "Updating code..."
cd $APP_DIR
git pull origin main

# Update backend
echo "Updating backend..."
cd $APP_DIR/zimmer-backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Update frontend
echo "Updating user panel..."
cd $APP_DIR/zimmer_user_panel
npm install
npm run build

echo "Updating admin dashboard..."
cd $APP_DIR/zimmermanagement/zimmer-admin-dashboard
npm install
npm run build

# Restart services
echo "Restarting services..."
pm2 restart all

echo "✅ Update completed successfully!"
