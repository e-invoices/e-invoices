from typing import Optional

from app.schemas.user import UserRead
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: int
    exp: int
    type: str = "access"  # "access" or "refresh"


class AuthResponse(BaseModel):
    """Response returned after successful authentication"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token"""

    refresh_token: str


class LoginRequest(BaseModel):
    """Email/password login request"""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Email/password registration request"""

    email: EmailStr
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    name: Optional[str] = Field(None, max_length=255)


class GoogleAuthRequest(BaseModel):
    """Google OAuth authentication request"""

    credential: str = Field(..., description="Google ID token (JWT)")
    is_registration: bool = Field(
        default=False, description="Whether this is a registration attempt"
    )


class GoogleUserInfo(BaseModel):
    """User info extracted from Google ID token"""

    sub: str  # Google user ID
    email: str
    email_verified: bool = False
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None


class SetPasswordRequest(BaseModel):
    """Request to set password for OAuth users"""

    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    confirm_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Request to change password for existing password users"""

    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
