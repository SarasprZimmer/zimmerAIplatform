# 🔍 Knowledge Base Monitoring System

## Overview

The Knowledge Base (KB) Monitoring system allows the Zimmer backend to monitor the health and status of knowledge bases across all user automations. This system provides real-time insights into KB health, backup status, and error logs.

## 🏗️ Architecture

```
Zimmer Backend ←→ External Automation APIs
     ↓
1. Admin requests KB status
2. Backend calls automation APIs
3. Normalized response returned
4. Admin can reset KB if needed
```

## 📋 Features

### ✅ Implemented Features

1. **KB Status Monitoring**
   - Real-time health status for each user's KB
   - Backup status tracking
   - Error log collection
   - Last updated timestamps

2. **KB Reset Functionality**
   - Admin-initiated KB resets
   - Secure API communication
   - Reset status tracking

3. **Secure API Communication**
   - Service token authentication
   - Timeout handling
   - Error handling and fallbacks

## 🔧 Database Schema

### Automation Model Extensions

```python
class Automation(Base):
    # ... existing fields ...
    api_kb_status_url = Column(String, nullable=True)  # KB status endpoint
    api_kb_reset_url = Column(String, nullable=True)   # KB reset endpoint
```

## 🌐 API Endpoints

### 1. GET `/api/admin/kb-status`

**Purpose**: Get KB status for all users of a specific automation

**Parameters**:
- `automation_id` (query): ID of the automation to check

**Response**:
```json
{
  "automation_id": 1,
  "automation_name": "Agency AI",
  "total_users": 3,
  "kb_statuses": [
    {
      "user_id": 123,
      "name": "Ali Rezayi",
      "kb_health": "healthy",
      "last_updated": "2025-01-28T15:30:00Z",
      "backup_status": true,
      "error_logs": [],
      "supports_reset": true
    }
  ]
}
```

### 2. POST `/api/admin/kb-reset/{user_automation_id}`

**Purpose**: Reset KB for a specific user automation

**Parameters**:
- `user_automation_id` (path): ID of the user automation to reset

**Response**:
```json
{
  "message": "KB reset initiated successfully",
  "user_automation_id": 1,
  "automation_name": "Agency AI",
  "reset_status": "success"
}
```

## 🔐 Security

### Service Token Authentication

All external automation API calls use a service token for authentication:

```python
ZIMMER_SERVICE_TOKEN = os.getenv("ZIMMER_SERVICE_TOKEN", "default_service_token")
```

**Headers sent to automation APIs**:
```
Authorization: Bearer <ZIMMER_SERVICE_TOKEN>
Content-Type: application/json
```

## 🚀 External Automation Requirements

Your external automations must implement these endpoints:

### 1. KB Status Endpoint

**URL**: `POST /api/kb-status`

**Request Body**:
```json
{
  "user_id": 123,
  "user_automation_id": 1
}
```

**Response**:
```json
{
  "status": "healthy|warning|error",
  "last_updated": "2025-01-28T15:30:00Z",
  "backup_status": true,
  "error_logs": [],
  "supports_reset": true,
  "kb_size": 1250
}
```

### 2. KB Reset Endpoint

**URL**: `POST /api/kb-reset`

**Request Body**:
```json
{
  "user_automation_id": 1
}
```

**Response**:
```json
{
  "status": "success",
  "message": "KB reset initiated",
  "timestamp": "2025-01-28T15:30:00Z"
}
```

## 🛠️ Setup Instructions

### 1. Environment Configuration

Add to your `.env` file:
```ini
ZIMMER_SERVICE_TOKEN=your_secret_service_token_for_automation_apis
```

### 2. Database Migration

Run the migration script to add KB monitoring columns:
```bash
python migrate_kb_monitoring.py
```

### 3. Update Automation URLs

In the admin dashboard, update your automations with KB monitoring URLs:
- **KB Status URL**: `https://your-automation.com/api/kb-status`
- **KB Reset URL**: `https://your-automation.com/api/kb-reset`

## 🧪 Testing

### 1. Mock API Server

Start the mock automation API for testing:
```bash
python mock_automation_api.py
```

This will start a server on `http://localhost:8001` with mock KB endpoints.

### 2. Test Scripts

Run the comprehensive test:
```bash
python test_complete_kb_monitoring.py
```

Or run individual tests:
```bash
python test_kb_monitoring.py
```

### 3. Manual Testing

1. **Start the mock API**: `python mock_automation_api.py`
2. **Start the main backend**: `uvicorn main:app --reload`
3. **Login to admin dashboard**: `http://localhost:3001`
4. **Navigate to KB Monitoring**: Check the monitoring page
5. **Test endpoints**: Use the test scripts or admin dashboard

## 📊 Health Status Values

- **`healthy`**: KB is working normally
- **`warning`**: KB has minor issues (e.g., old backup)
- **`error`**: KB has critical issues (e.g., connection failed)

## 🔄 Error Handling

The system includes comprehensive error handling:

1. **API Timeouts**: 10-second timeout with 504 Gateway Timeout
2. **Connection Errors**: 502 Bad Gateway for API errors
3. **Authentication Errors**: 401 Unauthorized for invalid tokens
4. **Fallback Responses**: Default error status when APIs fail

## 📝 Usage Examples

### Admin Dashboard Integration

The KB monitoring is integrated into the admin dashboard:

1. **Navigate to KB Monitoring page**
2. **Select automation** from dropdown
3. **View real-time status** for all users
4. **Reset KB** for specific users if needed

### API Integration

```python
import requests

# Get KB status
response = requests.get(
    "${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api/admin/kb-status",
    headers={"Authorization": f"Bearer {admin_token}"},
    params={"automation_id": 1}
)

# Reset KB
response = requests.post(
    "${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api/admin/kb-reset/1",
    headers={"Authorization": f"Bearer {admin_token}"}
)
```

## 🚨 Troubleshooting

### Common Issues

1. **"Automation does not have KB status URL configured"**
   - Solution: Update automation with KB monitoring URLs in admin dashboard

2. **"Automation API timeout"**
   - Solution: Check if external automation API is running and accessible

3. **"Invalid service token"**
   - Solution: Verify `ZIMMER_SERVICE_TOKEN` in `.env` file matches automation API

4. **"No user automations found"**
   - Solution: Users need to purchase automations first

### Debug Steps

1. **Check automation URLs**: Verify KB status/reset URLs are correct
2. **Test external APIs**: Ensure automation APIs are responding
3. **Verify tokens**: Check service token configuration
4. **Check logs**: Review backend logs for detailed error messages

## 🔮 Future Enhancements

1. **Real-time Notifications**: WebSocket updates for KB status changes
2. **Automated Alerts**: Email/SMS alerts for KB issues
3. **KB Analytics**: Usage statistics and trends
4. **Bulk Operations**: Reset multiple KBs at once
5. **KB Backup Management**: Automated backup scheduling

## 📞 Support

For issues or questions about the KB monitoring system:

1. Check the troubleshooting section above
2. Review the test scripts for examples
3. Verify external automation API compliance
4. Check backend logs for detailed error information 