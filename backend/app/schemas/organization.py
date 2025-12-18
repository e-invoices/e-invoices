from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class OrganizationRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    MEMBER = "member"
    VIEWER = "viewer"


# Organization schemas
class OrganizationBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    registration_name: str = Field(..., min_length=1, max_length=255)
    edb: str = Field(..., min_length=13, max_length=13, pattern=r"^\d{13}$")
    embs: str = Field(..., min_length=1, max_length=20)
    vat_registered: bool = True
    address: str = Field(..., min_length=1)
    contact_person: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr
    contact_phone: str = Field(..., min_length=1, max_length=50)


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""

    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""

    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    registration_name: Optional[str] = Field(None, min_length=1, max_length=255)
    vat_registered: Optional[bool] = None
    address: Optional[str] = Field(None, min_length=1)
    contact_person: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, min_length=1, max_length=50)


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizationWithRole(OrganizationResponse):
    """Organization response with user's role."""

    role: OrganizationRole
    joined_at: datetime


# User Organization schemas
class UserOrganizationBase(BaseModel):
    role: OrganizationRole = OrganizationRole.MEMBER


class UserOrganizationCreate(UserOrganizationBase):
    user_id: int
    organization_id: int
    invited_by: Optional[int] = None


class UserOrganizationResponse(BaseModel):
    id: int
    user_id: int
    organization_id: int
    role: OrganizationRole
    joined_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Invitation schemas
class InvitationCreate(BaseModel):
    """Schema for creating an invitation."""

    role: OrganizationRole = OrganizationRole.MEMBER
    target_email: Optional[EmailStr] = None
    max_uses: Optional[int] = Field(None, ge=1)


class InvitationResponse(BaseModel):
    """Schema for invitation response."""

    id: int
    organization_id: int
    code: str
    role: OrganizationRole
    target_email: Optional[str]
    expires_at: datetime
    max_uses: Optional[int]
    use_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InvitationWithLink(InvitationResponse):
    """Invitation response with full link."""

    link: str


class JoinOrganizationRequest(BaseModel):
    """Schema for joining an organization via invitation code."""

    code: str = Field(..., min_length=1, max_length=64)


class JoinOrganizationResponse(BaseModel):
    """Response after successfully joining an organization."""

    message: str
    organization: OrganizationResponse
    role: OrganizationRole


# List responses
class UserOrganizationsResponse(BaseModel):
    """List of user's organizations."""

    organizations: List[OrganizationWithRole]
    total: int
