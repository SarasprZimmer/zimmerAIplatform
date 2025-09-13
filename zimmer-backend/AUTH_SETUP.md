# Authentication System Setup Guide

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///./zimmer_dashboard.db

# JWT Configuration (REQUIRED)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# OpenAI Configuration (if using GPT services)
OPENAI_API_KEY=your-openai-api-key

# Other Configuration
ENVIRONMENT=development
```

## Installation

1. Install the new dependencies:
```bash
pip install -r requirements.txt
```

2. The new packages added are:
   - `bcrypt==4.1.2` - For password hashing
   - `pyjwt==2.8.0` - For JWT token handling

## Database Migration

Since we added a new `password_hash` field to the User model, you'll need to handle existing users:

1. For new installations: The database will be created automatically
2. For existing installations: You may need to add a migration script or manually update existing users

## API Endpoints

### Signup
```
POST /api/signup
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+1234567890",
    "password": "securepassword123"
}
```

### Login
```
POST /api/login
Content-Type: application/json

{
    "email": "john@example.com",
    "password": "securepassword123"
}
```

Response includes JWT token:
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user_id": 1,
    "email": "john@example.com",
    "name": "John Doe"
}
```

## Protected Routes

To protect routes that require authentication, use the dependency:

```python
from utils.auth_dependency import get_current_user, get_current_admin_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.name}"}

@router.get("/admin-only")
async def admin_route(current_user: User = Depends(get_current_admin_user)):
    return {"message": "Admin access granted"}
```

## Testing

Run the authentication test:
```bash
python test_auth.py
```

This will test:
- User signup
- User login
- Invalid login attempts
- Duplicate signup prevention

## Security Features

1. **Password Hashing**: All passwords are hashed using bcrypt with salt
2. **JWT Tokens**: Secure tokens with 7-day expiry
3. **No Plain Passwords**: Passwords are never stored or returned in plain text
4. **Input Validation**: Email validation and password requirements
5. **Error Handling**: Secure error messages that don't leak information

## Usage in Frontend

1. Store the JWT token securely (localStorage, sessionStorage, or httpOnly cookies)
2. Include the token in Authorization header:
   ```
   Authorization: Bearer <your-jwt-token>
   ```
3. Handle 401/403 responses for expired/invalid tokens
4. Implement token refresh logic if needed

## Production Considerations

1. Change the JWT_SECRET_KEY to a strong, random value
2. Use HTTPS in production
3. Consider implementing token refresh mechanism
4. Add rate limiting for login attempts
5. Implement password strength requirements
6. Add email verification if needed 