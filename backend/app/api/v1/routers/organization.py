import logging
from typing import List

from app.core.security import get_user_context
from app.db.session import get_session
from app.models.organization import OrganizationRole
from app.schemas.auth import UserContext
from app.schemas.organization import (
    InvitationCreate,
    InvitationResponse,
    InvitationWithLink,
    JoinOrganizationRequest,
    JoinOrganizationResponse,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    OrganizationWithRole,
    UserOrganizationsResponse,
)
from app.services.organization import organization_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED
)
async def create_organization(
    data: OrganizationCreate,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> OrganizationResponse:
    """Create a new organization. The creator becomes the owner."""
    # Check if organization with same EDB already exists
    existing = await organization_service.get_organization_by_edb(session, data.edb)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Организација со овој даночен број веќе постои.",
        )

    organization, _ = await organization_service.create_organization(
        session, data, ctx.user_id
    )
    logger.info(
        f"Organization created: {organization.company_name} by user {ctx.user_id}"
    )
    return organization


@router.get("", response_model=UserOrganizationsResponse)
async def get_my_organizations(
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> UserOrganizationsResponse:
    """Get all organizations the current user is a member of."""
    organizations = await organization_service.get_user_organizations(
        session, ctx.user_id
    )
    return UserOrganizationsResponse(
        organizations=organizations, total=len(organizations)
    )


@router.get("/{organization_id}", response_model=OrganizationWithRole)
async def get_organization(
    organization_id: int,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> OrganizationWithRole:
    """Get organization details. User must be a member."""
    # Check if user is a member
    role = await organization_service.get_user_role_in_organization(
        session, ctx.user_id, organization_id
    )
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Немате пристап до оваа организација.",
        )

    organization = await organization_service.get_organization_by_id(
        session, organization_id
    )
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организацијата не е пронајдена.",
        )

    # Get user's membership info
    orgs = await organization_service.get_user_organizations(session, ctx.user_id)
    org_with_role = next((o for o in orgs if o.id == organization_id), None)

    if not org_with_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организацијата не е пронајдена.",
        )

    return org_with_role


@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: int,
    data: OrganizationUpdate,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> OrganizationResponse:
    """Update organization details. Only owners and admins can update."""
    role = await organization_service.get_user_role_in_organization(
        session, ctx.user_id, organization_id
    )
    if role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Немате дозвола да ја измените оваа организација.",
        )

    organization = await organization_service.update_organization(
        session, organization_id, data
    )
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организацијата не е пронајдена.",
        )

    return organization


# Invitation endpoints
@router.post("/{organization_id}/invitations", response_model=InvitationWithLink)
async def create_invitation(
    organization_id: int,
    data: InvitationCreate,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> InvitationWithLink:
    """Create an invitation link. Only owners, admins, and accountants can create invitations."""
    role = await organization_service.get_user_role_in_organization(
        session, ctx.user_id, organization_id
    )
    if role not in [
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
        OrganizationRole.ACCOUNTANT,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Немате дозвола да креирате покани за оваа организација.",
        )

    invitation = await organization_service.create_invitation(
        session, organization_id, ctx.user_id, data
    )

    # Build the invitation link (frontend URL)
    link = f"/join?code={invitation.code}"

    return InvitationWithLink(
        id=invitation.id,
        organization_id=invitation.organization_id,
        code=invitation.code,
        role=invitation.role,
        target_email=invitation.target_email,
        expires_at=invitation.expires_at,
        max_uses=invitation.max_uses,
        use_count=invitation.use_count,
        is_active=invitation.is_active,
        created_at=invitation.created_at,
        link=link,
    )


@router.get("/{organization_id}/invitations", response_model=List[InvitationResponse])
async def get_invitations(
    organization_id: int,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> List[InvitationResponse]:
    """Get all invitations for an organization."""
    role = await organization_service.get_user_role_in_organization(
        session, ctx.user_id, organization_id
    )
    if role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Немате дозвола да ги видите поканите.",
        )

    invitations = await organization_service.get_organization_invitations(
        session, organization_id
    )
    return invitations


@router.delete(
    "/{organization_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_invitation(
    organization_id: int,
    invitation_id: int,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
):
    """Deactivate an invitation."""
    success = await organization_service.deactivate_invitation(
        session, invitation_id, ctx.user_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Поканата не е пронајдена или немате дозвола.",
        )


# Join via invitation code
@router.post("/join", response_model=JoinOrganizationResponse)
async def join_organization(
    data: JoinOrganizationRequest,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> JoinOrganizationResponse:
    """Join an organization using an invitation code."""
    (
        success,
        message,
        organization,
        role,
    ) = await organization_service.join_organization_via_invitation(
        session, ctx.user_id, data.code
    )

    if not success or not organization or not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    logger.info(f"User {ctx.user_id} joined organization {organization.id}")

    return JoinOrganizationResponse(
        message=message,
        organization=OrganizationResponse.model_validate(organization),
        role=role,
    )


# Validate invitation code (without joining - for preview)
@router.get("/join/validate", response_model=dict)
async def validate_invitation_code(
    code: str,
    ctx: UserContext = Depends(get_user_context),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Validate an invitation code and return organization info."""
    is_valid, message, invitation = await organization_service.validate_invitation(
        session, code
    )

    if not is_valid or not invitation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    # Check if user is already a member
    is_member = await organization_service.is_user_member(
        session, ctx.user_id, invitation.organization_id
    )

    return {
        "valid": True,
        "organization_name": invitation.organization.company_name,
        "role": invitation.role,
        "already_member": is_member,
    }
