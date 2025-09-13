# Google OAuth Setup Guide for Zimmer Platform

This guide covers the complete setup of Google OAuth authentication for both development and production environments.

## Overview

The implementation includes:
- Backend Google OAuth routes (`/api/auth/google/login`, `/api/auth/google/callback`)
- Frontend Google login button and callback handling
- Email verification integration with Google's `email_verified` claim
- In-memory access token + refresh cookie authentication model

## Backend Changes Made

### 1. Dependencies Added
- `authlib==1.3.1` - OAuth/OIDC client library

### 2. Settings Added
```python
# Google OAuth
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URL: str = os.getenv("GOOGLE_REDIRECT_URL", "http://localhost:8000/api/auth/google/callback")
FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")

# Email Verification (enabled by default)
REQUIRE_VERIFIED_EMAIL_FOR_LOGIN: bool = os.getenv("REQUIRE_VERIFIED_EMAIL_FOR_LOGIN", "True").lower() == "true"
```

### 3. New Files
- `routers/auth_google.py` - Google OAuth implementation
- `tests/test_auth_google_config.py` - Smoke tests

### 4. Modified Files
- `main.py` - Added Google OAuth router
- `routers/auth.py` - Added email verification check to login
- `settings.py` - Added Google OAuth and email verification settings

## Frontend Changes Made

### 1. New Files
- `pages/auth/google/done.tsx` - OAuth callback handler
- `pages/test-google-auth.tsx` - Test page for Google OAuth

### 2. Modified Files
- `pages/login.tsx` - Added Google login button

## Development Setup

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API and Google OAuth2 API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Choose "Web application"
6. Add authorized redirect URIs:
   - `http://localhost:8000/api/auth/google/callback`
7. Add authorized JavaScript origins:
   - `http://localhost:3000`

### 2. Backend Environment Variables

Create/update `zimmer-backend/.env`:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URL=http://localhost:8000/api/auth/google/callback
FRONTEND_BASE_URL=http://localhost:3000

# Email Verification (enabled by default)
REQUIRE_VERIFIED_EMAIL_FOR_LOGIN=true

# Existing settings...
DATABASE_URL=sqlite:///./dev.db
SECRET_KEY=your-secret-key-here
```

### 3. Frontend Environment Variables

Update `zimmer_user_panel/env.user`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 4. Install Dependencies

```bash
# Backend
cd zimmer-backend
pip install -r requirements.txt

# Frontend
cd zimmer_user_panel
npm install
```

### 5. Run Development Servers

```bash
# Terminal 1 - Backend
cd zimmer-backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd zimmer_user_panel
npm run dev
```

### 6. Test the Implementation

1. Visit `http://localhost:3000/login`
2. Click "ورود با گوگل" (Login with Google)
3. Complete Google OAuth flow
4. Should redirect to dashboard with access token

Or test configuration:
- Visit `http://localhost:3000/test-google-auth`

## Production Setup

### 1. Google Cloud Console (Production)

1. Update OAuth 2.0 Client ID settings:
   - Authorized redirect URIs:
     - `https://api.zimmerai.com/api/auth/google/callback`
   - Authorized JavaScript origins:
     - `https://zimmerai.com` (or your frontend domain)

### 2. Backend Environment Variables (Production)

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_CLIENT_SECRET=your_production_google_client_secret
GOOGLE_REDIRECT_URL=https://api.zimmerai.com/api/auth/google/callback
FRONTEND_BASE_URL=https://zimmerai.com

# Email Verification
REQUIRE_VERIFIED_EMAIL_FOR_LOGIN=true

# Other production settings...
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-production-secret-key
```

### 3. Frontend Environment Variables (Production)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://api.zimmerai.com
NEXT_PUBLIC_API_BASE_URL=https://api.zimmerai.com
```

### 4. Nginx Configuration

Ensure your Nginx configuration includes:

```nginx
# Backend API proxy
location /api/ {
    proxy_pass http://backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Allow cookies for OAuth
    proxy_cookie_path / /;
    proxy_cookie_domain localhost api.zimmerai.com;
}

# Frontend
location / {
    proxy_pass http://frontend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 5. Environment Variables

Update your environment variables in your deployment configuration:

```bash
# Backend environment variables
export GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
export GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
export GOOGLE_REDIRECT_URL=${GOOGLE_REDIRECT_URL}
export FRONTEND_BASE_URL=${FRONTEND_BASE_URL}
export REQUIRE_VERIFIED_EMAIL_FOR_LOGIN=true

# Frontend environment variables
export NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
export NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
```

## Testing

### Backend Tests

```bash
cd zimmer-backend
python -m pytest tests/test_auth_google_config.py -v
```

### Frontend Test

Visit `http://localhost:3000/test-google-auth` to check Google OAuth configuration.

### Manual Testing

1. **Google Login Flow:**
   - Click "ورود با گوگل" on login page
   - Complete Google OAuth consent
   - Should redirect to dashboard

2. **Email Verification:**
   - Try login with unverified email (password login)
   - Should get "email_not_verified" error
   - Google login should auto-verify if Google says email is verified

3. **Token Handling:**
   - Check that access token is stored in memory
   - Check that refresh cookie is set
   - Verify API calls work with stored token

## Troubleshooting

### Common Issues

1. **"Google OAuth not configured" error:**
   - Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
   - Restart backend server

2. **Redirect URI mismatch:**
   - Verify redirect URI in Google Console matches `GOOGLE_REDIRECT_URL`
   - Check for trailing slashes

3. **CORS errors:**
   - Ensure frontend domain is in Google Console authorized origins
   - Check backend CORS settings

4. **Token not stored:**
   - Check browser console for JavaScript errors
   - Verify `authClient.ts` is working correctly

### Debug Endpoints

- `GET /api/auth/google/configured` - Check if Google OAuth is configured
- `GET /api/auth/google/login` - Initiate Google OAuth flow
- `GET /api/auth/google/callback` - Handle OAuth callback

## Security Notes

1. **HTTPS Required in Production:**
   - Google OAuth requires HTTPS in production
   - Set `secure=True` for cookies in production

2. **State Parameter:**
   - CSRF protection via state parameter is implemented
   - Don't disable this security feature

3. **Token Storage:**
   - Access tokens are stored in memory (client-side)
   - Refresh tokens are stored in HTTP-only cookies
   - This is the existing pattern, maintained for consistency

4. **Email Verification:**
   - Google's `email_verified` claim is trusted
   - Users created via Google OAuth are auto-verified if Google says so
   - Password login still requires email verification

## Migration Notes

- Existing users are not affected
- Email verification is now enabled by default
- Google OAuth is additive - doesn't replace existing auth
- All existing authentication flows continue to work
