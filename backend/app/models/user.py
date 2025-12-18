from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from app.db.base import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

if TYPE_CHECKING:
    pass


class AuthProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Optional[str] = Column(
        String(255), nullable=True
    )  # Nullable for OAuth users
    full_name: Optional[str] = Column(String(255), nullable=True)

    # OAuth fields
    auth_provider: str = Column(
        String(50), default=AuthProvider.EMAIL.value, nullable=False
    )
    google_id: Optional[str] = Column(
        String(255), unique=True, nullable=True, index=True
    )
    picture_url: Optional[str] = Column(String(500), nullable=True)

    # Account status
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)

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
    last_login_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organizations = relationship(
        "UserOrganization",
        foreign_keys="UserOrganization.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def set_password(self, password_hash: str) -> None:
        self.hashed_password = password_hash

    def is_oauth_user(self) -> bool:
        return self.auth_provider != AuthProvider.EMAIL.value
