# 🚀 Google OAuth Quick Setup Guide

## Step 1: Get Google OAuth Credentials

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create/Select Project**: Create a new project or select existing one
3. **Enable APIs**: 
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" and enable it
   - Search for "Google OAuth2 API" and enable it
4. **Create OAuth Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - **Authorized redirect URIs**: `http://localhost:8000/api/auth/google/callback`
   - **Authorized JavaScript origins**: `http://localhost:3000`
5. **Copy Credentials**: Copy the Client ID and Client Secret

## Step 2: Update Environment Files

### Backend Environment (`zimmer-backend/env.backend`)

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=PASTE_YOUR_GOOGLE_CLIENT_ID_HERE
GOOGLE_CLIENT_SECRET=PASTE_YOUR_GOOGLE_CLIENT_SECRET_HERE
GOOGLE_REDIRECT_URL=http://localhost:8000/api/auth/google/callback
FRONTEND_BASE_URL=http://localhost:3000
```

### Frontend Environment (`zimmer_user_panel/env.user`)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Step 3: Rename Environment Files

```bash
# Backend
cd zimmer-backend
cp env.backend .env

# Frontend  
cd zimmer_user_panel
cp env.user .env
```

## Step 4: Install Dependencies

```bash
# Backend
cd zimmer-backend
pip install -r requirements.txt

# Frontend
cd zimmer_user_panel
npm install
```

## Step 5: Start the Servers

```bash
# Terminal 1 - Backend
cd zimmer-backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd zimmer_user_panel
npm run dev
```

## Step 6: Test Google OAuth

1. **Visit**: http://localhost:3000/login
2. **Click**: "ورود با گوگل" (Login with Google)
3. **Complete**: Google OAuth flow
4. **Should redirect**: To dashboard with access token

## Step 7: Test Configuration

Visit: http://localhost:3000/test-google-auth

This page will show you if Google OAuth is properly configured.

## 🔧 Troubleshooting

### "Google OAuth not configured" error
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in `.env`
- Restart backend server after updating `.env`

### Redirect URI mismatch
- Verify redirect URI in Google Console matches exactly: `http://localhost:8000/api/auth/google/callback`
- Check for trailing slashes

### CORS errors
- Ensure `http://localhost:3000` is in Google Console authorized origins
- Check backend CORS settings

## 📋 What You Need to Paste

**From Google Cloud Console, copy these two values:**

1. **Client ID**: `1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com`
2. **Client Secret**: `GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Paste them into `zimmer-backend/.env`:**
```bash
GOOGLE_CLIENT_ID=1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

That's it! 🎉
