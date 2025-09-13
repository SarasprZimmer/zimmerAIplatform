
# Caching Strategy for Zimmer AI Platform

## 1. Database Query Caching
- Cache user profile data (5 minutes)
- Cache automation listings (10 minutes)
- Cache dashboard statistics (2 minutes)
- Cache health status (1 minute)

## 2. API Response Caching
- GET /api/me - 5 minutes
- GET /api/automations/marketplace - 10 minutes
- GET /api/user/dashboard - 2 minutes
- GET /api/admin/dashboard - 2 minutes

## 3. Frontend Caching
- Static assets: 1 year
- API responses: 5 minutes
- User data: 2 minutes

## 4. Database Connection Pooling
- Pool size: 20 connections
- Max overflow: 30 connections
- Pool recycle: 1 hour
- Pool pre-ping: enabled
