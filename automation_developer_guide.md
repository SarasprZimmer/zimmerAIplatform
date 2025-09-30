# 🔧 Automation Developer Integration Guide

## Overview
This guide explains how to integrate your automation service with the Zimmer platform using service tokens for secure communication.

## 🔑 Service Token Integration

### What is a Service Token?
A service token is a secure authentication mechanism that allows the Zimmer platform to communicate with your automation service. It's like a "password" that proves requests are coming from the legitimate Zimmer platform.

### How It Works
1. **Zimmer Platform** → Sends request with service token in `X-Zimmer-Service-Token` header
2. **Your Automation Service** → Verifies the token is valid
3. **If valid** → Process the request
4. **If invalid** → Return 401 Unauthorized

## 🚀 Integration Steps

### Step 1: Receive Your Service Token
When an admin adds your automation to the Zimmer platform, they will:
1. Configure your automation URLs
2. Generate a service token
3. Provide you with the token

**Example Token:**
```
AUTOMATION_1_SERVICE_TOKEN=abc123xyz789def456ghi012jkl345mno678pqr901stu234vwx567yz890
```

### Step 2: Add Token to Your Environment
Store the service token securely in your automation's environment:

```bash
# Environment variable
export AUTOMATION_1_SERVICE_TOKEN="abc123xyz789def456ghi012jkl345mno678pqr901stu234vwx567yz890"
```

### Step 3: Implement Token Validation

#### Python (FastAPI) Example:
```python
import os
from fastapi import HTTPException, Header, Depends
from typing import Optional

# Get service token from environment
SERVICE_TOKEN = os.getenv("AUTOMATION_1_SERVICE_TOKEN")

async def verify_zimmer_token(
    x_zimmer_service_token: Optional[str] = Header(None, alias="X-Zimmer-Service-Token")
):
    """Verify the Zimmer service token"""
    if not x_zimmer_service_token:
        raise HTTPException(
            status_code=401, 
            detail="Missing service token"
        )
    
    if x_zimmer_service_token != SERVICE_TOKEN:
        raise HTTPException(
            status_code=401, 
            detail="Invalid service token"
        )
    
    return True

# Use in your endpoints
@app.post("/provision")
async def provision_endpoint(
    request_data: dict,
    token_valid: bool = Depends(verify_zimmer_token)
):
    # Your automation logic here
    return {"success": True, "message": "Automation provisioned successfully"}

@app.post("/usage/consume")
async def consume_usage(
    request_data: dict,
    token_valid: bool = Depends(verify_zimmer_token)
):
    # Your usage tracking logic here
    return {"success": True, "tokens_consumed": 10}
```

#### Node.js (Express) Example:
```javascript
const express = require('express');
const app = express();

// Get service token from environment
const SERVICE_TOKEN = process.env.AUTOMATION_1_SERVICE_TOKEN;

// Middleware to verify Zimmer service token
const verifyZimmerToken = (req, res, next) => {
    const token = req.headers['x-zimmer-service-token'];
    
    if (!token) {
        return res.status(401).json({
            error: 'Missing service token'
        });
    }
    
    if (token !== SERVICE_TOKEN) {
        return res.status(401).json({
            error: 'Invalid service token'
        });
    }
    
    next();
};

// Use middleware in your routes
app.post('/provision', verifyZimmerToken, (req, res) => {
    // Your automation logic here
    res.json({
        success: true,
        message: 'Automation provisioned successfully'
    });
});

app.post('/usage/consume', verifyZimmerToken, (req, res) => {
    // Your usage tracking logic here
    res.json({
        success: true,
        tokens_consumed: 10
    });
});
```

## 📡 Required Endpoints

Your automation service must implement these endpoints:

### 1. Provision Endpoint
**URL:** `POST /provision` (or your custom provision URL)
**Purpose:** Initialize a new user automation

**Request Headers:**
```
X-Zimmer-Service-Token: your_service_token
Content-Type: application/json
```

**Request Body:**
```json
{
    "user_automation_id": 123,
    "user_id": 456,
    "bot_token": "user_bot_token",
    "demo_tokens": 1000
}
```

**Response:**
```json
{
    "success": true,
    "message": "Automation provisioned successfully",
    "webhook_url": "https://your-automation.com/webhook/123" // Optional
}
```

### 2. Usage Consumption Endpoint
**URL:** `POST /usage/consume` (or your custom usage URL)
**Purpose:** Track token usage

**Request Headers:**
```
X-Zimmer-Service-Token: your_service_token
Content-Type: application/json
```

**Request Body:**
```json
{
    "user_automation_id": 123,
    "tokens_consumed": 10,
    "session_id": "session_123",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response:**
```json
{
    "success": true,
    "tokens_consumed": 10,
    "remaining_tokens": 990
}
```

### 3. KB Status Endpoint (Optional)
**URL:** `GET /kb/status` (or your custom KB status URL)
**Purpose:** Check knowledge base health

**Response:**
```json
{
    "status": "healthy",
    "last_updated": "2024-01-01T12:00:00Z",
    "total_documents": 100
}
```

### 4. KB Reset Endpoint (Optional)
**URL:** `POST /kb/reset` (or your custom KB reset URL)
**Purpose:** Reset knowledge base

**Response:**
```json
{
    "success": true,
    "message": "Knowledge base reset successfully"
}
```

## 🔒 Security Best Practices

### 1. Token Security
- ✅ **Store tokens securely** - Use environment variables, not hardcoded values
- ✅ **Never log tokens** - Avoid exposing tokens in logs
- ✅ **Use HTTPS** - Always use encrypted connections
- ✅ **Rotate tokens** - Change tokens if compromised

### 2. Request Validation
- ✅ **Verify all headers** - Check required headers are present
- ✅ **Validate request data** - Ensure request body is valid
- ✅ **Rate limiting** - Implement rate limiting to prevent abuse
- ✅ **Error handling** - Return appropriate error codes

### 3. Response Standards
- ✅ **Consistent format** - Use consistent JSON response format
- ✅ **Error codes** - Return appropriate HTTP status codes
- ✅ **Error messages** - Provide clear error messages
- ✅ **Timeout handling** - Handle request timeouts gracefully

## 🧪 Testing Your Integration

### 1. Test Token Validation
```bash
# Test with valid token
curl -X POST https://your-automation.com/provision \
  -H "X-Zimmer-Service-Token: your_valid_token" \
  -H "Content-Type: application/json" \
  -d '{"user_automation_id": 123, "user_id": 456, "bot_token": "test", "demo_tokens": 1000}'

# Test with invalid token
curl -X POST https://your-automation.com/provision \
  -H "X-Zimmer-Service-Token: invalid_token" \
  -H "Content-Type: application/json" \
  -d '{"user_automation_id": 123, "user_id": 456, "bot_token": "test", "demo_tokens": 1000}'
```

### 2. Test All Endpoints
Make sure all required endpoints respond correctly:
- ✅ Provision endpoint returns 200 with valid token
- ✅ Usage endpoint returns 200 with valid token
- ✅ All endpoints return 401 with invalid/missing token
- ✅ All endpoints handle malformed requests gracefully

## 🚨 Common Issues & Solutions

### Issue 1: 401 Unauthorized
**Cause:** Invalid or missing service token
**Solution:** 
- Check token is correctly set in environment
- Verify token matches what was provided by admin
- Ensure header name is exactly `X-Zimmer-Service-Token`

### Issue 2: 404 Not Found
**Cause:** Endpoint URL not found
**Solution:**
- Verify endpoint URLs are correct
- Check if endpoints are properly implemented
- Ensure server is running and accessible

### Issue 3: 500 Internal Server Error
**Cause:** Server-side error in your automation
**Solution:**
- Check server logs for errors
- Verify request data handling
- Test endpoints independently

## 📞 Support

If you need help with integration:
1. Check this guide first
2. Test your endpoints independently
3. Contact the Zimmer platform admin
4. Provide error logs and request details

## 🔄 Token Rotation

If your service token is compromised:
1. Contact the Zimmer platform admin
2. Request a new service token
3. Update your environment variables
4. Test the new token
5. Remove the old token from your system

---

**Remember:** The service token is the key to secure communication between Zimmer and your automation. Keep it safe and never expose it in logs or client-side code!
