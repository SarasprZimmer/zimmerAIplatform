#!/bin/bash
# Script to check server logs for automation deletion errors
# Run this on your server

echo "🔍 Checking PM2 status..."
pm2 status

echo ""
echo "🔍 Checking recent backend logs..."
pm2 logs zimmer-backend --lines 30

echo ""
echo "🔍 Checking for automation-related errors..."
pm2 logs zimmer-backend --lines 100 | grep -i "automation\|delete\|error\|exception"

echo ""
echo "🔍 Checking if backend is running..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "Backend not responding"
