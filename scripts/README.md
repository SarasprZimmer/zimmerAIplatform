# 🔍 Zimmer API Endpoint Test Suite

This test suite will help you identify which API endpoints are working and which ones need fixing on both the admin and user panels.

## 🚀 Quick Start

### Option 1: PowerShell (Recommended for Windows)
```powershell
# Navigate to scripts directory
cd scripts

# Run the test
.\run_api_test.bat
```

### Option 2: Python (Cross-platform)
```bash
# Navigate to scripts directory
cd scripts

# Install requirements (if needed)
pip install requests

# Run the test
python api_endpoint_test.py
```

## 📊 What the Test Does

The test suite will:

1. **Test all public endpoints** (no authentication required)
2. **Check response status codes** (200, 401, 422, 500, etc.)
3. **Measure response times** for performance analysis
4. **Generate a detailed report** showing:
   - ✅ Working endpoints
   - ❌ Failed endpoints with error details
   - Success rate percentage
   - Response time statistics

## 🎯 Endpoints Tested

### Public Endpoints (No Auth Required)
- CORS test endpoint
- Available automations list
- Password reset endpoints
- Payment initialization

### Protected Endpoints (Auth Required)
- User management (admin panel)
- Automation management (admin panel)
- Support tickets
- Knowledge base
- System monitoring
- Token management
- User-specific data

## 📋 Expected Results

### ✅ Good Responses
- **200**: Endpoint exists and works
- **401**: Endpoint exists but requires authentication (expected for protected routes)
- **422**: Endpoint exists but validation failed (expected for invalid test data)

### ❌ Problem Responses
- **404**: Endpoint doesn't exist (backend routing issue)
- **500**: Server error (backend code issue)
- **Connection Error**: Backend not running or unreachable

## 🔧 How to Fix Issues

### 1. Backend Issues (500 errors, missing endpoints)
- Check backend logs for error details
- Verify router configurations in `main.py`
- Ensure database connections are working
- Check environment variables

### 2. Frontend Issues (Wrong URLs, missing /api prefixes)
- Verify `NEXT_PUBLIC_API_URL` in `.env` files
- Check all API calls include `/api` prefix
- Ensure consistent URL construction

### 3. Authentication Issues
- Verify JWT secret keys match between frontend and backend
- Check CORS configuration
- Ensure refresh token logic works

## 📈 Success Metrics

- **Excellent**: 90%+ endpoints working
- **Good**: 70-89% endpoints working
- **Needs Work**: 50-69% endpoints working
- **Critical**: <50% endpoints working

## 🚨 Troubleshooting

### Test Won't Run
- Ensure backend is running on `${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}`
- Check PowerShell execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Verify Python and requests library are installed

### All Tests Fail
- Backend might not be running
- Check if backend is on different port
- Verify firewall/network settings

### Some Tests Fail
- Review the detailed error messages in the report
- Check backend logs for specific errors
- Verify endpoint URLs match between frontend and backend

## 📝 Report Files

The test generates a timestamped report file:
- `api_test_report_YYYYMMDD_HHMMSS.md`
- Contains detailed results and error information
- Use this to prioritize fixes

## 🔄 Re-running Tests

After fixing issues:
1. Restart the backend service
2. Clear frontend build caches
3. Re-run the test suite
4. Compare results to track progress

## 🎯 Next Steps

1. **Run the test suite** to get baseline results
2. **Fix backend issues first** (500 errors, missing endpoints)
3. **Fix frontend API calls** (wrong URLs, missing /api prefixes)
4. **Test authentication flow** manually
5. **Re-run tests** to verify fixes
6. **Repeat until 90%+ success rate**

---

**Happy testing! 🚀**
