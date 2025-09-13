# 🔐 Authentication Sessions System

This document describes the robust access/refresh token session system implemented in the Zimmer backend.

## 🎯 Overview

The new authentication system provides:
- **Short-lived access tokens** (15 minutes by default)
- **Long-lived refresh tokens** (7 days by default)
- **Automatic session management** with idle timeout (2 hours)
- **Secure token rotation** on each refresh
- **Comprehensive audit logging** for security

## ⚙️ Configuration

Add these environment variables to your `.env` file:

```bash
# Session Configuration
ACCESS_TOKEN_TTL_MIN=15
REFRESH_TOKEN_TTL_DAYS=7
SESSION_IDLE_TIMEOUT_MIN=120  # auto logout after 2h inactivity
JWT_ALG=HS256
```

## 🏗️ Architecture

### Components

1. **Session Model** (`models/session.py`)
   - Stores refresh token hashes
   - Tracks user agent and IP address
   - Manages expiration and revocation

2. **JWT Utilities** (`utils/jwt.py`)
   - Access token creation/validation
   - Refresh token generation and verification
   - Secure token handling with bcrypt

3. **Authentication Router** (`routers/auth_sessions.py`)
   - Login, refresh, logout endpoints
   - Session management and cleanup
   - Security features (idle timeout, token rotation)

4. **Updated Dependencies** (`utils/auth.py`)
   - Enhanced user authentication
   - Admin privilege verification
   - Token validation middleware

## 🔄 API Endpoints

### POST `/api/auth/login`
**Request:**
```json
{
  "email": "user@example.com",
  "password": "userpassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "کاربر نمونه",
    "email": "user@example.com",
    "is_admin": false
  }
}
```

**Cookies:** Sets `refresh_token` as HTTP-only cookie

### POST `/api/auth/refresh`
**Request:** No body required, uses refresh token cookie

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Features:**
- Rotates refresh token for security
- Updates session last_used timestamp
- Enforces idle timeout

### POST `/api/auth/logout`
**Request:** No body required, uses refresh token cookie

**Response:**
```json
{
  "ok": true,
  "message": "خروج موفقیت‌آمیز بود"
}
```

**Features:**
- Revokes current session
- Clears refresh token cookie

### POST `/api/auth/logout-all`
**Request:** Requires valid access token in Authorization header

**Response:**
```json
{
  "ok": true,
  "message": "از تمام جلسه‌ها خارج شدید (3 جلسه)"
}
```

**Features:**
- Revokes all active sessions for user
- Requires authentication

## 🔒 Security Features

### Token Security
- **Access tokens**: Short-lived (15 min) with standard JWT claims
- **Refresh tokens**: Cryptographically secure random 256-bit tokens
- **Token rotation**: New refresh token on each refresh
- **Secure storage**: Refresh tokens stored as bcrypt hashes

### Session Management
- **Idle timeout**: Automatic logout after 2 hours of inactivity
- **IP tracking**: Records client IP addresses for security
- **User agent logging**: Tracks client browser/application
- **Automatic cleanup**: Removes expired and revoked sessions

### Cookie Security
- **HTTP-only**: Prevents XSS attacks
- **Secure**: Set to true in production with HTTPS
- **SameSite**: Configurable (lax for development, strict for production)
- **Path restriction**: Limited to `/api/auth` endpoints

## 🚀 Implementation Steps

### 1. Database Migration
Run the migration script to create the sessions table:

```bash
cd zimmer-backend
python migrate_sessions.py
```

### 2. Environment Setup
Update your `.env` file with session configuration.

### 3. Restart Server
Restart the backend server to load the new authentication system.

### 4. Test the System
Run the comprehensive test suite:

```bash
python test_auth_sessions.py
```

## 🔧 Frontend Integration

### Login Flow
1. Call `/api/auth/login` with credentials
2. Store access token in memory/state
3. Refresh token is automatically handled by cookies

### Token Refresh
1. Intercept 401 responses from API calls
2. Call `/api/auth/refresh` to get new access token
3. Retry original request with new token

### Logout Flow
1. Call `/api/auth/logout` to clear current session
2. Clear stored access token
3. Redirect to login page

### Example Frontend Code

```typescript
// Login
const login = async (email: string, password: string) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // Important for cookies
    body: JSON.stringify({ email, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    // Store access token
    setAccessToken(data.access_token);
    // Refresh token is automatically handled by cookies
  }
};

// API call with automatic refresh
const apiCall = async (url: string, options: RequestInit = {}) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${accessToken}`
      },
      credentials: 'include'
    });
    
    if (response.status === 401) {
      // Token expired, try to refresh
      const refreshResponse = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include'
      });
      
      if (refreshResponse.ok) {
        const { access_token } = await refreshResponse.json();
        setAccessToken(access_token);
        
        // Retry original request
        return fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            'Authorization': `Bearer ${access_token}`
          },
          credentials: 'include'
        });
      } else {
        // Refresh failed, redirect to login
        redirectToLogin();
        return;
      }
    }
    
    return response;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};
```

## 🧪 Testing

### Test Coverage
The test suite covers:
- ✅ Login and session creation
- ✅ Token refresh and rotation
- ✅ Idle timeout enforcement
- ✅ Logout and session revocation
- ✅ Invalid credential handling
- ✅ Missing token scenarios

### Running Tests
```bash
# Make sure backend is running
python test_auth_sessions.py
```

### Test Requirements
- Backend server running on `${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}`
- Test user with email `admin@zimmerai.com` and password `admin123`
- `httpx` library installed

## 🔄 Migration from Legacy System

### Backward Compatibility
- Legacy JWT tokens continue to work during transition
- New endpoints are additive, not replacing existing ones
- Gradual migration path available

### Migration Strategy
1. **Phase 1**: Deploy new system alongside existing
2. **Phase 2**: Update frontend to use new endpoints
3. **Phase 3**: Deprecate legacy authentication
4. **Phase 4**: Remove legacy code

## 🚨 Security Considerations

### Production Deployment
- Set `secure=True` for cookies when using HTTPS
- Use `SameSite=Strict` if no cross-site requirements
- Configure appropriate CORS origins
- Monitor session logs for suspicious activity

### Token Management
- Access tokens are short-lived for security
- Refresh tokens are rotated on each use
- Sessions are automatically cleaned up
- Idle timeout prevents session hijacking

### Monitoring
- Log all authentication events
- Track failed login attempts
- Monitor session creation and revocation
- Alert on unusual authentication patterns

## 📚 Additional Resources

- [JWT Security Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [Session Management Security](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)

## 🤝 Support

For questions or issues with the authentication system:
1. Check the test suite for common scenarios
2. Review server logs for error details
3. Verify environment configuration
4. Test with the provided examples

---

**Note**: This system provides enterprise-grade security while maintaining ease of use. Always test thoroughly in your environment before production deployment.
