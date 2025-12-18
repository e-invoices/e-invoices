import logging
from datetime import UTC, datetime, timedelta
from typing import Any, Optional

from app.core.config import get_settings
from app.schemas.auth import UserContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash

settings = get_settings()
pwd_hasher = PasswordHash.recommended()

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_hasher.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_hasher.hash(password)


def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    organization_id: Optional[int] = None,
    organization_role: Optional[str] = None,
    token_type: str = "access",
) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": token_type}

    # Add organization context if provided
    if organization_id is not None:
        to_encode["org_id"] = organization_id
    if organization_role is not None:
        to_encode["org_role"] = organization_role

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | int, expires_delta: Optional[timedelta] = None
) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(days=settings.refresh_token_expire_days)
    )
    to_encode: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


def get_user_context(token: str = Depends(oauth2_scheme)) -> UserContext:
    """Extract user context from JWT token"""
    try:
        payload = decode_access_token(token)
        return UserContext(
            user_id=int(payload.get("sub")),
            organization_id=payload.get("org_id"),
            role=payload.get("org_role"),
        )
    except (ValueError, TypeError) as e:
        logger.warning("Invalid token: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
