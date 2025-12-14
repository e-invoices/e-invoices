import logging
from datetime import UTC, datetime
from typing import List, Optional

from app.core.security import get_password_hash
from app.models import user as user_models
from app.models.user import AuthProvider
from app.schemas.user import UserCreate, UserCreateOAuth, UserRead
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def normalize_email(email: str) -> str:
    """
    Normalize email address for consistent storage and lookup.

    Gmail ignores dots in the local part, so:
    - pipo.jordanoski@gmail.com
    - pipojordanoski@gmail.com
    - p.i.p.o.jordanoski@gmail.com

    Are all the same inbox. This function normalizes Gmail addresses
    by removing dots from the local part.
    """
    email = email.lower().strip()
    local_part, domain = email.rsplit("@", 1)

    # Gmail and Google-hosted domains ignore dots
    gmail_domains = {"gmail.com", "googlemail.com"}
    if domain in gmail_domains:
        local_part = local_part.replace(".", "")

    return f"{local_part}@{domain}"


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[user_models.User]:
        result = await self.session.execute(
            select(user_models.User).where(user_models.User.id == user_id)
        )
        user = result.scalar_one_or_none()
        logger.debug("Fetched user by id %s => %s", user_id, bool(user))
        return user

    async def get_by_email(self, email: str) -> Optional[user_models.User]:
        normalized = normalize_email(str(email))
        result = await self.session.execute(
            select(user_models.User).where(user_models.User.email == normalized)
        )
        user = result.scalar_one_or_none()
        logger.debug("Fetched user by email %s (normalized: %s) => %s", email, normalized, bool(user))
        return user

    async def get_by_google_id(self, google_id: str) -> Optional[user_models.User]:
        result = await self.session.execute(
            select(user_models.User).where(user_models.User.google_id == google_id)
        )
        user = result.scalar_one_or_none()
        logger.debug("Fetched user by google_id %s => %s", google_id, bool(user))
        return user

    async def create_user(
        self, payload: UserCreate, *, hashed_password: Optional[str] = None
    ) -> UserRead:
        password_value = hashed_password or get_password_hash(payload.password)
        normalized_email = normalize_email(str(payload.email))
        user = user_models.User(
            email=normalized_email,
            hashed_password=password_value,
            full_name=payload.full_name,
            auth_provider=AuthProvider.EMAIL.value,
            is_verified=False,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info("Created user %s", user.email)
        return UserRead.model_validate(user)

    async def create_oauth_user(self, payload: UserCreateOAuth) -> UserRead:
        normalized_email = normalize_email(str(payload.email))
        user = user_models.User(
            email=normalized_email,
            hashed_password=None,  # OAuth users don't have passwords
            full_name=payload.full_name,
            auth_provider=payload.auth_provider,
            google_id=payload.google_id,
            picture_url=payload.picture_url,
            is_verified=payload.is_verified,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info("Created OAuth user %s via %s", user.email, payload.auth_provider)
        return UserRead.model_validate(user)

    async def update_last_login(self, user: user_models.User) -> None:
        user.last_login_at = datetime.now(UTC)
        await self.session.commit()
        logger.debug("Updated last login for user %s", user.email)

    async def set_password(self, user: user_models.User, hashed_password: str) -> UserRead:
        """Set password for a user (typically OAuth users adding password login)"""
        user.hashed_password = hashed_password
        await self.session.commit()
        await self.session.refresh(user)
        logger.info("Password set for user %s", user.email)
        return UserRead.model_validate(user)

    async def verify_user(self, user: user_models.User) -> UserRead:
        """Mark user as verified"""
        user.is_verified = True
        await self.session.commit()
        await self.session.refresh(user)
        logger.info("User %s verified", user.email)
        return UserRead.model_validate(user)

    async def update_oauth_info(
        self,
        user: user_models.User,
        *,
        google_id: Optional[str] = None,
        picture_url: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> UserRead:
        if google_id and not user.google_id:
            user.google_id = google_id
        if picture_url:
            user.picture_url = picture_url
        if full_name and not user.full_name:
            user.full_name = full_name
        await self.session.commit()
        await self.session.refresh(user)
        logger.debug("Updated OAuth info for user %s", user.email)
        return UserRead.model_validate(user)

    async def list_users(self) -> List[UserRead]:
        result = await self.session.execute(select(user_models.User))
        records = [UserRead.model_validate(user) for user in result.scalars().all()]
        logger.debug("List users returned %d records", len(records))
        return records
