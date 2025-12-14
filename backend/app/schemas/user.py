from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=1)]


class UserCreateOAuth(BaseModel):
    """Schema for creating OAuth users (no password required)"""
    email: EmailStr
    full_name: Optional[str] = None
    auth_provider: str
    google_id: Optional[str] = None
    picture_url: Optional[str] = None
    is_verified: bool = True  # OAuth users are pre-verified


class UserRead(UserBase):
    id: int
    auth_provider: str = "email"
    picture_url: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    has_password: bool = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        # Add has_password based on whether hashed_password exists
        if hasattr(obj, 'hashed_password'):
            # Create a dict and add has_password
            data = {
                'id': obj.id,
                'email': obj.email,
                'full_name': obj.full_name,
                'auth_provider': obj.auth_provider,
                'picture_url': obj.picture_url,
                'is_active': obj.is_active,
                'is_verified': obj.is_verified,
                'has_password': bool(obj.hashed_password),
                'created_at': obj.created_at,
            }
            return cls(**data)
        return super().model_validate(obj, *args, **kwargs)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    picture_url: Optional[str] = None

