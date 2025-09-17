from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class LoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(False, description="Whether to remember the user")

    model_config = ConfigDict(from_attributes=True)


class SignupRequest(BaseModel):
    """Request schema for user signup"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    name: str = Field(..., description="User full name")
    confirm_password: str = Field(..., description="Password confirmation")

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    """Response schema for successful login"""
    access_token: str = Field(..., description="JWT access token")
    user: dict = Field(..., description="User information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "id": 1,
                    "name": "کاربر نمونه",
                    "email": "user@example.com",
                    "is_admin": False
                }
            }
        },
        from_attributes=True
    )


class RefreshResponse(BaseModel):
    """Response schema for token refresh"""
    access_token: str = Field(..., description="New JWT access token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        },
        from_attributes=True
    )


class LogoutResponse(BaseModel):
    """Response schema for logout"""
    ok: bool = Field(..., description="Whether logout was successful")
    message: str = Field(..., description="Logout message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ok": True,
                "message": "خروج موفقیت‌آمیز بود"
            }
        },
        from_attributes=True
    )


class SessionStatus(BaseModel):
    """Schema for session status"""
    is_authenticated: bool = Field(..., description="Whether user is authenticated")
    user: Optional[Dict[str, Any]] = Field(None, description="User information if authenticated")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")

    model_config = ConfigDict(from_attributes=True)
