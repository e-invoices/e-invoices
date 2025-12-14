import logging
from datetime import timedelta
from typing import Optional

from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import user as user_models
from app.models.user import AuthProvider
from app.schemas.auth import (
    AuthResponse,
    GoogleAuthRequest,
    GoogleUserInfo,
    LoginRequest,
    RegisterRequest,
    Token,
)
from app.schemas.user import UserCreateOAuth, UserRead
from app.services.user import UserService
from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic.v1 import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserService(session)

    async def login(self, payload: LoginRequest) -> AuthResponse:
        """Authenticate user with email and password"""
        user = await self.user_service.get_by_email(str(payload.email))

        if not user:
            logger.warning("Login attempt for non-existent email %s", payload.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check if user registered via OAuth (no password)
        if user.is_oauth_user() or not user.hashed_password:
            logger.warning("Password login attempt for OAuth user %s", payload.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This account uses Google sign-in. Please use 'Continue with Google'.",
            )

        if not verify_password(payload.password, user.hashed_password):
            logger.warning("Failed password verification for %s", payload.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated",
            )

        await self.user_service.update_last_login(user)
        token = self._generate_token(user.id)
        user_read = UserRead.model_validate(user)

        logger.info("User %s logged in successfully", payload.email)
        return AuthResponse(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            user=user_read,
        )

    async def register(self, payload: RegisterRequest) -> AuthResponse:
        """Register a new user with email and password"""
        existing_user = await self.user_service.get_by_email(str(payload.email))

        if existing_user:
            logger.warning("Registration attempt for existing email %s", payload.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        from app.schemas.user import UserCreate

        hashed_password = get_password_hash(payload.password)
        user_create = UserCreate(
            email=payload.email, password=payload.password, full_name=payload.name
        )
        user_read = await self.user_service.create_user(
            user_create, hashed_password=hashed_password
        )

        # Send verification email
        await self._send_verification_email(
            user_read.id, str(payload.email), payload.name
        )

        token = self._generate_token(user_read.id)

        logger.info("User %s registered successfully", payload.email)
        return AuthResponse(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            user=user_read,
        )

    async def google_auth(self, payload: GoogleAuthRequest) -> AuthResponse:
        """Authenticate or register user via Google OAuth"""
        # Verify Google token
        google_user = await self._verify_google_token(payload.credential)

        if not google_user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google email is not verified",
            )

        # Check if user exists by Google ID
        user = await self.user_service.get_by_google_id(google_user.sub)

        if not user:
            # Check if user exists by email
            user = await self.user_service.get_by_email(google_user.email)

            if user:
                # Link Google account to existing user
                await self.user_service.update_oauth_info(
                    user,
                    google_id=google_user.sub,
                    picture_url=google_user.picture,
                    full_name=google_user.name,
                )
                logger.info("Linked Google account to existing user %s", user.email)
            else:
                # Create new user
                oauth_user = UserCreateOAuth(
                    email=EmailStr(google_user.email),
                    full_name=google_user.name,
                    auth_provider=AuthProvider.GOOGLE.value,
                    google_id=google_user.sub,
                    picture_url=google_user.picture,
                    is_verified=True,
                )
                user_read = await self.user_service.create_oauth_user(oauth_user)
                user = await self.user_service.get_by_id(user_read.id)
                logger.info("Created new user via Google OAuth: %s", google_user.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create or retrieve user",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated",
            )

        await self.user_service.update_last_login(user)
        token = self._generate_token(user.id)
        user_read = UserRead.model_validate(user)

        return AuthResponse(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            user=user_read,
        )

    async def get_current_user(self, user_id: int) -> UserRead:
        """Get current user by ID"""
        user = await self.user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserRead.model_validate(user)

    async def set_password(
        self, user_id: int, password: str, confirm_password: str
    ) -> UserRead:
        """Set password for OAuth user who wants to add email/password login"""
        if password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
            )

        user = await self.user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password already set. Use change password instead.",
            )

        hashed_password = get_password_hash(password)
        return await self.user_service.set_password(user, hashed_password)

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
        confirm_password: str,
    ) -> UserRead:
        """Change password for user with existing password"""
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match",
            )

        user = await self.user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No password set. Use set password instead.",
            )

        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect",
            )

        hashed_password = get_password_hash(new_password)
        return await self.user_service.set_password(user, hashed_password)

    async def _verify_google_token(self, token: str) -> GoogleUserInfo:
        """Verify Google ID token and extract user info"""
        if not settings.google_client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth is not configured",
            )

        try:
            # Verify the token
            id_info = id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.google_client_id
            )

            # Verify issuer
            if id_info["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise ValueError("Invalid issuer")

            return GoogleUserInfo(
                sub=id_info["sub"],
                email=id_info["email"],
                email_verified=id_info.get("email_verified", False),
                name=id_info.get("name"),
                given_name=id_info.get("given_name"),
                family_name=id_info.get("family_name"),
                picture=id_info.get("picture"),
            )
        except ValueError as e:
            logger.error("Google token verification failed: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token"
            )

    async def _send_verification_email(
        self, user_id: int, email: str, name: Optional[str]
    ) -> None:
        """Send verification email to user"""
        from app.services.email import email_service

        verification_token = email_service.generate_verification_token(user_id)
        success = email_service.send_verification_email(
            to_email=email, user_name=name, verification_token=verification_token
        )
        if not success:
            logger.warning("Failed to send verification email to %s", email)

    async def verify_email(self, token: str) -> UserRead:
        """Verify user email with token"""
        from app.core.security import decode_access_token

        try:
            payload = decode_access_token(token)
            user_id = int(payload.get("sub"))
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        user = await self.user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified"
            )

        user_read = await self.user_service.verify_user(user)

        # Send welcome email
        from app.services.email import email_service

        email_service.send_welcome_email(user.email, user.full_name)

        logger.info("User %s verified email successfully", user.email)
        return user_read

    async def resend_verification_email(self, user_id: int) -> dict:
        """Resend verification email to user"""
        user = await self.user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified"
            )

        await self._send_verification_email(user.id, user.email, user.full_name)
        return {"message": "Verification email sent"}

    # Legacy methods for backwards compatibility
    async def authenticate_user(self, email: str, password: str) -> user_models.User:
        user = await self.user_service.get_by_email(email)
        logger.info("Authenticating user %s", email)
        if (
            not user
            or not user.hashed_password
            or not verify_password(password, user.hashed_password)
        ):
            logger.warning("Failed authentication for %s", email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        return user

    async def register_user(self, payload) -> UserRead:
        user = await self.user_service.get_by_email(str(payload.email))
        logger.debug("Registering user %s", payload.email)
        if user:
            logger.warning("Registration attempt for existing email %s", payload.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        hashed_password = get_password_hash(payload.password)
        return await self.user_service.create_user(
            payload, hashed_password=hashed_password
        )

    @staticmethod
    def _generate_token(
        user_id: int, expires_delta: Optional[timedelta] = None
    ) -> Token:
        from app.core.security import create_refresh_token

        logger.debug("Generating tokens for user_id=%s", user_id)
        access_token = create_access_token(user_id, expires_delta)
        refresh_token = create_refresh_token(user_id)
        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @staticmethod
    def generate_token(
        user_id: int, expires_delta: Optional[timedelta] = None
    ) -> Token:
        """Public method for backwards compatibility"""
        return AuthService._generate_token(user_id, expires_delta)
