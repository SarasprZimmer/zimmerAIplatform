#!/bin/bash

# Health check script for Zimmer Platform
# This script checks if all services are running properly

set -e

echo "🏥 Health Check for Zimmer Platform..."

# Check if PM2 is running
if command -v pm2 &> /dev/null; then
    echo "Checking PM2 services..."
    pm2 status
else
    echo "PM2 not found, checking systemd services..."
    sudo systemctl status zimmer-backend zimmer-user-panel zimmer-admin-dashboard
fi

# Check if nginx is running
echo "Checking nginx..."
sudo systemctl status nginx

# Check if PostgreSQL is running
echo "Checking PostgreSQL..."
sudo systemctl status postgresql

# Check if backend API is responding
echo "Checking backend API..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is healthy"
else
    echo "❌ Backend API is not responding"
fi

# Check if user panel is responding
echo "Checking user panel..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ User panel is healthy"
else
    echo "❌ User panel is not responding"
fi

# Check if admin dashboard is responding
echo "Checking admin dashboard..."
if curl -f http://localhost:4000 > /dev/null 2>&1; then
    echo "✅ Admin dashboard is healthy"
else
    echo "❌ Admin dashboard is not responding"
fi

# Check disk space
echo "Checking disk space..."
df -h

# Check memory usage
echo "Checking memory usage..."
free -h

echo "🏥 Health check completed!"
