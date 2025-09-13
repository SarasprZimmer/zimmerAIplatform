# Bot Token Uniqueness Implementation

This document describes the implementation of bot token uniqueness in the Zimmer system, ensuring that each Telegram bot token can only be associated with one user automation.

## Overview

The bot token uniqueness feature prevents multiple users from using the same Telegram bot token, which is essential for:
- Security: Preventing unauthorized access to bot functionality
- Data integrity: Ensuring each bot token maps to a single user automation
- User experience: Providing clear error messages when duplicate tokens are detected

## Implementation Details

### 1. Database Changes

#### Model Updates (`models/user_automation.py`)
- Added unique constraint on `telegram_bot_token` field
- Added `UniqueConstraint` import from SQLAlchemy
- Added `__table_args__` with unique constraint definition

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, UniqueConstraint

class UserAutomation(Base):
    __tablename__ = "user_automations"
    # ... existing fields ...
    
    # Add unique constraint for bot token
    __table_args__ = (
        UniqueConstraint('telegram_bot_token', name='uq_telegram_bot_token'),
    )
```

#### Migration Script (`migrate_bot_token_uniqueness.py`)
- Checks for existing duplicate bot tokens before adding constraint
- Adds unique index on `telegram_bot_token` column
- Includes testing functionality to verify constraint works

### 2. Schema Updates

#### New Schemas (`schemas/user.py`)
- `UserAutomationCreate`: For creating user automations with bot token
- `UserAutomationUpdate`: For updating user automations with bot token validation

```python
class UserAutomationCreate(BaseModel):
    automation_id: int
    telegram_bot_token: Optional[str] = None
    tokens_remaining: Optional[int] = 0

class UserAutomationUpdate(BaseModel):
    telegram_bot_token: Optional[str] = None
    tokens_remaining: Optional[int] = None
    status: Optional[str] = None
```

### 3. API Endpoints

#### New Endpoints (`routers/users.py`)

##### POST `/api/user/automations`
Creates a new user automation with bot token uniqueness validation:

```python
@router.post("/user/automations", response_model=UserAutomationResponse)
async def create_user_automation(
    automation_data: UserAutomationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check bot token uniqueness if provided
    if automation_data.telegram_bot_token:
        existing_bot = db.query(UserAutomation).filter(
            UserAutomation.telegram_bot_token == automation_data.telegram_bot_token
        ).first()
        
        if existing_bot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="این توکن ربات قبلاً ثبت شده است. لطفاً یک توکن دیگر وارد کنید."
            )
```

##### PUT `/api/user/automations/{automation_id}`
Updates a user automation with bot token uniqueness validation:

```python
@router.put("/user/automations/{automation_id}", response_model=UserAutomationResponse)
async def update_user_automation(
    automation_id: int = Path(..., description="User automation ID to update"),
    automation_data: UserAutomationUpdate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check bot token uniqueness if updating
    if automation_data and automation_data.telegram_bot_token:
        existing_bot = db.query(UserAutomation).filter(
            UserAutomation.telegram_bot_token == automation_data.telegram_bot_token,
            UserAutomation.id != automation_id
        ).first()
        
        if existing_bot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="این توکن ربات قبلاً ثبت شده است. لطفاً یک توکن دیگر وارد کنید."
            )
```

### 4. Error Handling

#### Persian Error Messages
All error messages for bot token uniqueness are in Persian:

- **Creation Error**: "این توکن ربات قبلاً ثبت شده است. لطفاً یک توکن دیگر وارد کنید."
- **Update Error**: "این توکن ربات قبلاً ثبت شده است. لطفاً یک توکن دیگر وارد کنید."
- **Database Constraint Error**: Handled with the same Persian message

#### Integrity Error Handling
Both API-level and database-level uniqueness violations are handled:

```python
except IntegrityError as e:
    db.rollback()
    if "uq_telegram_bot_token" in str(e):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این توکن ربات قبلاً ثبت شده است. لطفاً یک توکن دیگر وارد کنید."
        )
```

### 5. Frontend Implementation

#### Purchase Page (`zimmer_user_panel/app/automation/purchase/page.tsx`)
- Form for purchasing automations with bot token input
- Error handling for duplicate bot tokens
- Persian error messages displayed to users
- Loading states and success feedback

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  // ... form submission logic ...
  
  if (!response.ok) {
    // Handle specific bot token uniqueness error
    if (response.status === 400 && data.detail && data.detail.includes('این توکن ربات قبلاً ثبت شده است')) {
      setError('این ربات قبلاً به یک حساب دیگر متصل شده است.');
    } else {
      setError(data.detail || 'خطا در خرید اتوماسیون');
    }
    return;
  }
};
```

#### Updated Components
- `AvailableAutomationsCard`: Links to purchase page
- Error handling with Persian messages
- Loading states during form submission

### 6. Testing

#### Test Scripts
1. **`test_bot_token_uniqueness.py`**: Basic functionality testing
2. **`test_complete_bot_token_uniqueness.py`**: Comprehensive testing including:
   - API-level uniqueness validation
   - Database constraint enforcement
   - Persian error message verification
   - Update operation testing

#### Test Coverage
- ✅ API endpoint creation with unique bot token
- ✅ API endpoint creation with duplicate bot token (should fail)
- ✅ API endpoint update with duplicate bot token (should fail)
- ✅ Database constraint enforcement
- ✅ Persian error messages
- ✅ Error handling for both creation and updates

## Usage Examples

### Creating User Automation with Bot Token
```bash
POST /api/user/automations
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "automation_id": 1,
  "telegram_bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  "tokens_remaining": 100
}
```

### Successful Response
```json
{
  "id": 1,
  "automation_id": 1,
  "automation_name": "Test Automation",
  "tokens_remaining": 100,
  "demo_tokens": 5,
  "is_demo_active": true,
  "demo_expired": false,
  "status": "active",
  "created_at": "2025-01-27T10:30:00Z"
}
```

### Error Response (Duplicate Token)
```json
{
  "detail": "این توکن ربات قبلاً ثبت شده است. لطفاً یک توکن دیگر وارد کنید."
}
```

## Security Considerations

1. **JWT Authentication**: All endpoints require valid JWT tokens
2. **User Isolation**: Users can only access their own automations
3. **Database Constraints**: Unique constraint enforced at database level
4. **Input Validation**: Bot token format validation (can be enhanced)
5. **Error Information**: Error messages don't reveal sensitive information

## Migration Instructions

1. **Run Migration Script**:
   ```bash
   cd zimmer-backend
   python migrate_bot_token_uniqueness.py
   ```

2. **Verify Migration**:
   ```bash
   python test_bot_token_uniqueness.py
   ```

3. **Test Complete System**:
   ```bash
   python test_complete_bot_token_uniqueness.py
   ```

## Future Enhancements

1. **Bot Token Validation**: Add format validation for Telegram bot tokens
2. **Token Verification**: Verify bot token with Telegram API
3. **Bulk Operations**: Handle multiple bot token assignments
4. **Audit Logging**: Log bot token assignments and changes
5. **Rate Limiting**: Prevent abuse of bot token creation endpoints

## Troubleshooting

### Common Issues

1. **Migration Fails Due to Duplicates**:
   - Check for existing duplicate bot tokens in database
   - Resolve duplicates before running migration

2. **API Returns 500 Error**:
   - Check database connection
   - Verify unique constraint exists
   - Check server logs for detailed error

3. **Frontend Shows Generic Error**:
   - Verify API endpoint is accessible
   - Check CORS configuration
   - Ensure JWT token is valid

### Debug Commands

```bash
# Check database constraints
sqlite3 zimmer_dashboard.db "PRAGMA index_list(user_automations);"

# Check for duplicate bot tokens
sqlite3 zimmer_dashboard.db "SELECT telegram_bot_token, COUNT(*) FROM user_automations WHERE telegram_bot_token IS NOT NULL GROUP BY telegram_bot_token HAVING COUNT(*) > 1;"

# Test API endpoint
curl -X POST ${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api/user/automations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"automation_id": 1, "telegram_bot_token": "test_token"}'
```

## Conclusion

The bot token uniqueness implementation provides a robust solution for preventing duplicate bot token assignments while maintaining a good user experience with clear Persian error messages. The system works at both the API and database levels to ensure data integrity and security. 