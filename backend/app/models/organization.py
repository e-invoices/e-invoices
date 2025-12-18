import secrets
from datetime import datetime
from enum import Enum
from typing import Optional

from app.db.base import Base
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class OrganizationRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    MEMBER = "member"
    VIEWER = "viewer"


class Organization(Base):
    __tablename__ = "organizations"

    id: int = Column(Integer, primary_key=True, index=True)

    # Company identification
    company_name: str = Column(String(255), nullable=False)  # Brand name
    registration_name: str = Column(
        String(255), nullable=False
    )  # From Central Registry
    edb: str = Column(
        String(13), unique=True, nullable=False, index=True
    )  # Tax number (13 digits)
    embs: str = Column(String(20), nullable=False)  # Company ID (Matichen broj)

    # VAT status
    vat_registered: bool = Column(Boolean, default=True, nullable=False)

    # Address
    address: str = Column(Text, nullable=False)

    # Contact information
    contact_person: str = Column(String(255), nullable=False)
    contact_email: str = Column(String(255), nullable=False)
    contact_phone: str = Column(String(50), nullable=False)

    # Status
    is_active: bool = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    members = relationship(
        "UserOrganization", back_populates="organization", cascade="all, delete-orphan"
    )
    invitations = relationship(
        "OrganizationInvitation",
        back_populates="organization",
        cascade="all, delete-orphan",
    )


class UserOrganization(Base):
    __tablename__ = "user_organizations"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: int = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    # Role within organization
    role: OrganizationRole = Column(
        SQLEnum(
            OrganizationRole,
            name="organizationrole",
            create_constraint=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=OrganizationRole.MEMBER.value,
        nullable=False,
    )

    # Tracking
    joined_at: datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    invited_by: Optional[int] = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Status
    is_active: bool = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship(
        "User", foreign_keys="UserOrganization.user_id", back_populates="organizations"
    )
    organization = relationship("Organization", back_populates="members")
    inviter = relationship("User", foreign_keys="UserOrganization.invited_by")


class OrganizationInvitation(Base):
    __tablename__ = "organization_invitations"

    id: int = Column(Integer, primary_key=True, index=True)
    organization_id: int = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    # Invitation code (8 characters)
    code: str = Column(String(64), unique=True, nullable=False, index=True)

    # Who created the invitation
    created_by: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Optional: target specific email
    target_email: Optional[str] = Column(String(255), nullable=True)

    # Role the invitee will get
    role: OrganizationRole = Column(
        SQLEnum(
            OrganizationRole,
            name="organizationrole",
            create_constraint=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=OrganizationRole.MEMBER.value,
        nullable=False,
    )

    # Expiration and limits
    expires_at: datetime = Column(DateTime(timezone=True), nullable=False)
    max_uses: Optional[int] = Column(Integer, nullable=True)  # NULL = unlimited
    use_count: int = Column(Integer, default=0, nullable=False)

    # Status
    is_active: bool = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    organization = relationship("Organization", back_populates="invitations")
    creator = relationship("User", foreign_keys="OrganizationInvitation.created_by")

    @staticmethod
    def generate_code() -> str:
        """Generate a unique 8-character invitation code."""
        return secrets.token_urlsafe(6)[:8].upper()
