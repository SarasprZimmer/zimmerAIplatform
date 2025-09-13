# Security Hardening Guide

## Overview

This document outlines the comprehensive security measures implemented in the Zimmer backend to protect against common web application vulnerabilities.

## 1. Input Validation & Sanitization

### Sanitization Utilities (`utils/sanitize.py`)

#### Text Sanitization
- **`sanitize_text()`**: Strips whitespace, normalizes unicode spaces, removes control characters
- **`forbid_html()`**: Removes HTML tags and escapes entities (prevents XSS)
- **`escape_html()`**: Escapes HTML entities while preserving formatting

#### Field Validation
- **Email validation**: RFC 5321 compliant with length limits
- **Phone validation**: Iranian phone number format support
- **String validation**: Configurable length limits with HTML filtering
- **Text validation**: Longer content fields (up to 20k chars)

#### Pydantic Integration
All schemas now include automatic validation:
```python
@validator('name')
def validate_name(cls, v):
    return validate_string_field(v, max_length=100)

@validator('email')
def validate_email(cls, v):
    return validate_email(v)
```

### Schema Updates

#### User Schemas (`schemas/user.py`)
- Name: max 100 chars
- Email: RFC 5321 validation
- Phone: Iranian format validation
- Password: 8-128 chars

#### Ticket Schemas (`schemas/ticket.py`)
- Subject: max 200 chars
- Message: max 10,000 chars
- Attachment path: max 500 chars

#### Knowledge Base (`schemas/knowledge.py`)
- Category: max 64 chars
- Answer: max 20,000 chars

#### Payment Schemas (`schemas/payment_zp.py`)
- Return path: max 200 chars
- Authority: max 255 chars
- Status: max 10 chars

## 2. CSRF Protection

### Implementation (`utils/csrf.py`)

#### Double-Submit Token Pattern
1. **Token Generation**: `GET /api/auth/csrf` returns token + sets cookie
2. **Cookie**: `XSRF-TOKEN` with `SameSite=Strict`, `Secure=true`
3. **Header**: `X-CSRF-Token` must match cookie hash
4. **Validation**: Automatic check for unsafe methods with cookies

#### Middleware Behavior
- **Safe methods** (GET, HEAD, OPTIONS): No CSRF check
- **No cookies**: Skip CSRF check (API-only requests)
- **Authorization header**: Skip CSRF check (token-based auth)
- **Unsafe methods + cookies**: Require valid CSRF token

#### Usage
```javascript
// Frontend implementation
const response = await fetch('/api/auth/csrf');
const { csrf_token } = await response.json();

// Include in unsafe requests
fetch('/api/admin/users', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrf_token,
    'Content-Type': 'application/json'
  },
  credentials: 'include'
});
```

## 3. Rate Limiting

### Implementation (`utils/rate_limit.py`)

#### Rate Limits
- **Login**: 5 requests per minute per IP
- **Token refresh**: 60 requests per hour per IP
- **Payment init**: 10 requests per minute per user

#### Features
- **In-memory storage**: Simple implementation (use Redis in production)
- **Automatic cleanup**: Old entries removed periodically
- **Persian error messages**: User-friendly rate limit messages
- **IP-based tracking**: X-Forwarded-For header support

#### Error Response
```json
{
  "detail": "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً کمی صبر کنید."
}
```

## 4. Security Headers

### Implementation (`utils/security_headers.py`)

#### Headers Set
- **X-Content-Type-Options**: `nosniff` (prevents MIME sniffing)
- **X-Frame-Options**: `DENY` (prevents clickjacking)
- **Referrer-Policy**: `no-referrer` (privacy protection)
- **Strict-Transport-Security**: `max-age=15552000; includeSubDomains` (HSTS)
- **X-XSS-Protection**: `1; mode=block` (XSS protection)
- **X-Permitted-Cross-Domain-Policies**: `none` (prevents cross-domain data)
- **X-Download-Options**: `noopen` (prevents file execution)

#### Content Security Policy
```javascript
"default-src 'self'; 
 script-src 'self' 'unsafe-inline' 'unsafe-eval'; 
 style-src 'self' 'unsafe-inline'; 
 img-src 'self' data: https:; 
 font-src 'self'; 
 connect-src 'self'; 
 frame-ancestors 'none';"
```

### CORS Configuration
- **Tight origins**: Only specified domains allowed
- **Credentials**: `allow_credentials=True` for cookies
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Authorization, Content-Type, X-CSRF-Token, X-Requested-With
- **Max age**: 1 hour cache

## 5. Middleware Stack

### Order of Execution
1. **Security Headers**: Add headers to all responses
2. **Rate Limiting**: Check request limits
3. **CSRF Protection**: Validate tokens for unsafe methods
4. **Trusted Host**: Validate host headers
5. **CORS**: Handle cross-origin requests

### Configuration (`main.py`)
```python
# Security middleware in order
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(TrustedHostMiddleware)

# CORS with tight settings
configure_cors(app, allowed_origins=[...])
```

## 6. Authentication Security

### Session Management
- **Access tokens**: Short-lived (15 minutes), in-memory only
- **Refresh tokens**: Long-lived (7 days), httpOnly cookies
- **Session tracking**: Database-backed session storage
- **Idle timeout**: Automatic session revocation
- **Token rotation**: New refresh token on each refresh

### Password Security
- **Bcrypt hashing**: Secure password storage
- **Length validation**: 8-128 characters
- **Rate limiting**: Prevents brute force attacks

## 7. Production Considerations

### Environment Variables
```env
# Security settings
ACCESS_TOKEN_TTL_MIN=15
REFRESH_TOKEN_TTL_DAYS=7
SESSION_IDLE_TIMEOUT_MIN=30
JWT_ALG=HS256

# CORS origins (production)
ALLOWED_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

### Recommended Improvements
1. **Redis**: Replace in-memory rate limiting with Redis
2. **Database sessions**: Store CSRF tokens in database
3. **Monitoring**: Add security event logging
4. **WAF**: Consider web application firewall
5. **HTTPS**: Enforce HTTPS in production
6. **Secrets management**: Use proper secrets management

### Security Headers for Production
```python
# Additional headers for production
response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
```

## 8. Testing Security

### Validation Testing
```python
# Test input validation
def test_email_validation():
    assert validate_email("test@example.com") == "test@example.com"
    with pytest.raises(ValueError):
        validate_email("invalid-email")

def test_xss_prevention():
    malicious_input = "<script>alert('xss')</script>"
    sanitized = forbid_html(malicious_input)
    assert "<script>" not in sanitized
```

### Rate Limiting Testing
```python
# Test rate limiting
def test_login_rate_limit():
    for _ in range(6):
        response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 429
```

### CSRF Testing
```python
# Test CSRF protection
def test_csrf_required():
    response = client.post("/api/admin/users", json=user_data)
    assert response.status_code == 403
```

## 9. Monitoring & Logging

### Security Events
- Failed login attempts
- Rate limit violations
- CSRF token failures
- Invalid input attempts
- Session revocations

### Log Format
```json
{
  "timestamp": "2025-01-20T10:30:00Z",
  "event": "rate_limit_exceeded",
  "ip": "192.168.1.1",
  "endpoint": "POST /api/auth/login",
  "user_agent": "Mozilla/5.0..."
}
```

## 10. Incident Response

### Rate Limit Violations
1. Log the incident
2. Monitor for patterns
3. Consider IP blocking for repeated violations
4. Review security logs

### CSRF Attacks
1. Log failed CSRF attempts
2. Review request patterns
3. Check for compromised tokens
4. Consider token rotation

### XSS Attempts
1. Log sanitization events
2. Review input patterns
3. Update sanitization rules if needed
4. Monitor for successful bypasses

This security implementation provides comprehensive protection against common web application vulnerabilities while maintaining usability and performance.
