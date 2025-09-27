from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from models.user import UserRole
from utils.sanitize import validate_email, validate_phone, validate_string_field, validate_text_field

class UserSignupRequest(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    password: str

    @validator('name')
    def validate_name(cls, v):
        return validate_string_field(v, max_length=100)

    @validator('email')
    def validate_email(cls, v):
        return validate_email(v)

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        return validate_phone(v)

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password too long. Maximum 128 characters allowed.")
        return v

class UserSignupResponse(BaseModel):
    message: str
    user_id: int
    email: str
    access_token: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

    @validator('email')
    def validate_email(cls, v):
        return validate_email(v)

    @validator('password')
    def validate_password(cls, v):
        if len(v) > 128:
            raise ValueError("Password too long. Maximum 128 characters allowed.")
        return v

class UserLoginResponse(BaseModel):
    message: str
    access_token: str
    user_id: int
    email: str
    name: str
    role: UserRole

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if v is None:
            return v
        return validate_string_field(v, max_length=100)

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        return validate_phone(v)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserAutomationCreate(BaseModel):
    automation_id: int
    telegram_bot_token: Optional[str] = None
    tokens_remaining: Optional[int] = 0

    @validator('telegram_bot_token')
    def validate_telegram_bot_token(cls, v):
        if v is None:
            return v
        return validate_string_field(v, max_length=255)

class UserAutomationUpdate(BaseModel):
    telegram_bot_token: Optional[str] = None
    tokens_remaining: Optional[int] = None
    status: Optional[str] = None

    @validator('telegram_bot_token')
    def validate_telegram_bot_token(cls, v):
        if v is None:
            return v
        return validate_string_field(v, max_length=255)

    @validator('status')
    def validate_status(cls, v):
        if v is None:
            return v
        return validate_string_field(v, max_length=50)

class UserAutomationResponse(BaseModel):
    id: int
    automation_id: int
    automation_name: str
    tokens_remaining: int
    demo_tokens: int
    is_demo_active: bool
    demo_expired: bool
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserDashboardResponse(BaseModel):
    user: UserResponse
    automations: list[UserAutomationResponse]
    total_demo_tokens: int
    total_paid_tokens: int
    has_active_demo: bool
    has_expired_demo: bool

# New schemas for user management
class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    password: str
    role: UserRole = UserRole.support_staff
    is_admin: Optional[bool] = False

    @validator('name')
    def validate_name(cls, v):
        return validate_string_field(v, max_length=100)

    @validator('email')
    def validate_email(cls, v):
        return validate_email(v)

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        return validate_phone(v)

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password too long. Maximum 128 characters allowed.")
        return v

class UserUpdateRoleRequest(BaseModel):
    role: UserRole
    is_active: Optional[bool] = None

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if v is None:
            return v
        return validate_string_field(v, max_length=100)

    @validator('email')
    def validate_email(cls, v):
        if v is None:
            return v
        return validate_email(v)

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        return validate_phone(v)

    @validator('password')
    def validate_password(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password too long. Maximum 128 characters allowed.")
        return v

class UserListResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: Optional[str] = None
    role: UserRole
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserSettingsResponse(BaseModel):
    """User settings response model"""
    id: int
    name: str
    email: str
    phone_number: Optional[str] = None
    role: UserRole
    is_active: bool
    email_verified: bool
    twofa_enabled: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    preferences: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True) 