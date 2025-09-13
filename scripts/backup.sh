#!/bin/bash

# Backup script for Zimmer Platform
# This script creates a complete backup of the application

set -e

APP_DIR="/opt/zimmer"
BACKUP_DIR="/opt/backups/zimmer"
DATE=$(date +%Y%m%d_%H%M%S)

echo "💾 Creating backup..."

# Create backup directory
sudo mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
pg_dump -h localhost -U zimmer_user zimmer_production > $BACKUP_DIR/database_$DATE.sql

# Backup application files
echo "Backing up application files..."
sudo tar -czf $BACKUP_DIR/application_$DATE.tar.gz -C /opt zimmer

# Backup nginx configuration
echo "Backing up nginx configuration..."
sudo cp /etc/nginx/sites-available/zimmer $BACKUP_DIR/nginx_zimmer_$DATE.conf

# Backup systemd services
echo "Backing up systemd services..."
sudo tar -czf $BACKUP_DIR/systemd_$DATE.tar.gz -C /etc/systemd/system zimmer-*.service

# Clean old backups (keep last 7 days)
echo "Cleaning old backups..."
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed successfully!"
echo "Backup location: $BACKUP_DIR"
