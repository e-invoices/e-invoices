import logging

from app.core.security import decode_access_token
from app.db.session import get_session
from app.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    GoogleAuthRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    SetPasswordRequest,
    Token,
)
from app.schemas.user import UserRead
from app.services.auth import AuthService
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Extract user ID from JWT token"""
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        return user_id
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest, session: AsyncSession = Depends(get_session)
) -> AuthResponse:
    """Login with email and password"""
    auth_service = AuthService(session)
    logger.debug("Login attempt for %s", payload.email)
    return await auth_service.login(payload)


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    payload: RegisterRequest, session: AsyncSession = Depends(get_session)
) -> AuthResponse:
    """Register a new user with email and password"""
    auth_service = AuthService(session)
    logger.debug("Registration attempt for %s", payload.email)
    return await auth_service.register(payload)


@router.post("/google", response_model=AuthResponse)
async def google_auth(
    payload: GoogleAuthRequest, session: AsyncSession = Depends(get_session)
) -> AuthResponse:
    """Authenticate or register via Google OAuth"""
    auth_service = AuthService(session)
    logger.debug("Google auth attempt (is_registration=%s)", payload.is_registration)
    return await auth_service.google_auth(payload)


@router.get("/me", response_model=UserRead)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    """Get current authenticated user"""
    auth_service = AuthService(session)
    return await auth_service.get_current_user(user_id)


@router.post("/set-password", response_model=UserRead)
async def set_password(
    payload: SetPasswordRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    """Set password for OAuth users who want to add email/password login"""
    auth_service = AuthService(session)
    logger.debug("Set password request for user_id=%s", user_id)
    return await auth_service.set_password(
        user_id, payload.password, payload.confirm_password
    )


@router.post("/change-password", response_model=UserRead)
async def change_password(
    payload: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    """Change password for users with existing password"""
    auth_service = AuthService(session)
    logger.debug("Change password request for user_id=%s", user_id)
    return await auth_service.change_password(
        user_id,
        payload.current_password,
        payload.new_password,
        payload.confirm_password,
    )


@router.post("/verify-email", response_model=UserRead)
async def verify_email(
    token: str, session: AsyncSession = Depends(get_session)
) -> UserRead:
    """Verify user email with token from verification email"""
    auth_service = AuthService(session)
    logger.debug("Email verification request")
    return await auth_service.verify_email(token)


@router.post("/resend-verification")
async def resend_verification(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Resend verification email to current user"""
    auth_service = AuthService(session)
    logger.debug("Resend verification email for user_id=%s", user_id)
    return await auth_service.resend_verification_email(user_id)


@router.post("/logout")
async def logout() -> dict:
    """Logout current user (client should discard token)"""
    # JWT tokens are stateless, so we just return success
    # Client is responsible for removing the token
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    payload: RefreshTokenRequest, session: AsyncSession = Depends(get_session)
) -> AuthResponse:
    """Get new access token using refresh token"""
    try:
        token_payload = decode_access_token(payload.refresh_token)

        # Verify it's a refresh token
        if token_payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        user_id = int(token_payload.get("sub"))
        auth_service = AuthService(session)

        # Get user to verify they still exist and are active
        user = await auth_service.get_current_user(user_id)

        # Generate new tokens
        token = AuthService.generate_token(user_id)

        logger.info("Token refreshed for user_id=%s", user_id)
        return AuthResponse(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            user=user,
        )
    except (ValueError, TypeError) as e:
        logger.warning("Invalid refresh token: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )


# Legacy endpoint for OAuth2PasswordRequestForm compatibility
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Token:
    """Legacy token endpoint for OAuth2 form login"""
    auth_service = AuthService(session)
    logger.debug("Token request for %s", form_data.username)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    return auth_service.generate_token(user.id)
