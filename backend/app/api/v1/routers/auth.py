import logging

from app.core.security import get_user_context
from app.db.session import get_session
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    GoogleAuthRequest,
    LinkGoogleRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SwitchOrganizationRequest,
    SwitchOrganizationResponse,
    Token,
    UpdateProfileRequest,
    UserContext,
)
from app.schemas.user import UserRead
from app.services.auth import AuthService
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


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
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    """Get current authenticated user"""
    auth_service = AuthService(session)
    return await auth_service.get_current_user(ctx.user_id)


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Request password reset email (for users who forgot their password)"""
    auth_service = AuthService(session)
    logger.debug("Forgot password request for email=%s", payload.email)
    return await auth_service.request_password_reset(str(payload.email))


@router.post("/request-password-reset")
async def request_password_reset(
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Request password reset email for authenticated user (set or change password)"""
    auth_service = AuthService(session)
    logger.debug("Password reset request for user_id=%s", ctx.user_id)
    return await auth_service.request_password_reset_authenticated(ctx.user_id)


@router.post("/reset-password", response_model=UserRead)
async def reset_password(
    payload: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    """Reset password using token from email"""
    auth_service = AuthService(session)
    logger.debug("Reset password request")
    return await auth_service.reset_password(
        payload.token, payload.password, payload.confirm_password
    )


@router.put("/profile", response_model=UserRead)
async def update_profile(
    payload: UpdateProfileRequest,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    """Update current user's profile"""
    auth_service = AuthService(session)
    logger.debug("Update profile request for user_id=%s", ctx.user_id)
    return await auth_service.update_profile(ctx.user_id, payload.full_name)


@router.post("/link-google", response_model=UserRead)
async def link_google(
    payload: LinkGoogleRequest,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    """Link Google account to existing user"""
    auth_service = AuthService(session)
    logger.debug("Link Google request for user_id=%s", ctx.user_id)
    return await auth_service.link_google(ctx.user_id, payload.credential)


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
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Resend verification email to current user"""
    auth_service = AuthService(session)
    logger.debug("Resend verification email for user_id=%s", ctx.user_id)
    return await auth_service.resend_verification_email(ctx.user_id)


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
    auth_service = AuthService(session)
    return await auth_service.refresh_token(payload.refresh_token)


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


@router.post("/switch-organization", response_model=SwitchOrganizationResponse)
async def switch_organization(
    payload: SwitchOrganizationRequest,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> SwitchOrganizationResponse:
    """Switch to a different organization and get new tokens with org context"""
    auth_service = AuthService(session)
    return await auth_service.switch_organization(ctx.user_id, payload.organization_id)
