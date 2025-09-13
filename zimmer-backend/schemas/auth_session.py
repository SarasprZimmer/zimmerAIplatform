from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class SignupRequest(BaseModel):
    """Request schema for user signup"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (minimum 6 characters)")
    name: str = Field(..., min_length=2, description="User full name")


class LoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class LoginResponse(BaseModel):
    """Response schema for successful login"""
    access_token: str = Field(..., description="JWT access token")
    user: dict = Field(..., description="User information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "id": 1,
                    "name": "کاربر نمونه",
                    "email": "user@example.com",
                    "is_admin": False
                }
            }
        }


class RefreshResponse(BaseModel):
    """Response schema for token refresh"""
    access_token: str = Field(..., description="New JWT access token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class LogoutResponse(BaseModel):
    """Response schema for logout"""
    ok: bool = Field(..., description="Logout success status")
    message: str = Field(..., description="Logout message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ok": True,
                "message": "خروج موفقیت‌آمیز بود"
            }
        }


class SessionInfo(BaseModel):
    """Schema for session information"""
    id: int
    user_id: int
    user_agent: Optional[str]
    ip_address: Optional[str]
    last_used_at: datetime
    expires_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Response schema for listing user sessions"""
    total: int
    items: list[SessionInfo]
