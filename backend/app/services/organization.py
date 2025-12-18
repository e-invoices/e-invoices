from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from app.models.organization import (
    Organization,
    OrganizationInvitation,
    OrganizationRole,
    UserOrganization,
)
from app.models.user import User
from app.schemas.organization import (
    InvitationCreate,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationWithRole,
)
from pydantic.v1 import EmailStr
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Invitation validity duration (30 minutes)
INVITATION_VALIDITY_MINUTES = 30


class OrganizationService:
    """Service for organization-related operations."""

    @staticmethod
    async def create_organization(
        db: AsyncSession, data: OrganizationCreate, owner_id: int
    ) -> Tuple[Organization, UserOrganization]:
        """Create a new organization and set the creator as owner."""
        # Create organization
        organization = Organization(
            company_name=data.company_name,
            registration_name=data.registration_name,
            edb=data.edb,
            embs=data.embs,
            vat_registered=data.vat_registered,
            address=data.address,
            contact_person=data.contact_person,
            contact_email=EmailStr(data.contact_email),
            contact_phone=data.contact_phone,
        )
        db.add(organization)
        await db.flush()  # Get the organization ID

        # Create user-organization relationship with owner role
        user_org = UserOrganization(
            user_id=owner_id,
            organization_id=organization.id,
            role=OrganizationRole.OWNER.value,
        )
        db.add(user_org)
        await db.commit()
        await db.refresh(organization)
        await db.refresh(user_org)

        return organization, user_org

    @staticmethod
    async def get_organization_by_id(
        db: AsyncSession, organization_id: int
    ) -> Optional[Organization]:
        """Get organization by ID."""
        result = await db.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_organization_by_edb(
        db: AsyncSession, edb: str
    ) -> Optional[Organization]:
        """Get organization by EDB (tax number)."""
        result = await db.execute(select(Organization).where(Organization.edb == edb))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_organizations(
        db: AsyncSession, user_id: int
    ) -> List[OrganizationWithRole]:
        """Get all organizations for a user with their roles."""
        result = await db.execute(
            select(UserOrganization)
            .options(selectinload(UserOrganization.organization))
            .where(
                and_(
                    UserOrganization.user_id == user_id,
                    UserOrganization.is_active,
                )
            )
        )
        user_orgs = result.scalars().all()

        organizations = []
        for user_org in user_orgs:
            org = user_org.organization
            org_with_role = OrganizationWithRole(
                id=org.id,
                company_name=org.company_name,
                registration_name=org.registration_name,
                edb=org.edb,
                embs=org.embs,
                vat_registered=org.vat_registered,
                address=org.address,
                contact_person=org.contact_person,
                contact_email=org.contact_email,
                contact_phone=org.contact_phone,
                is_active=org.is_active,
                created_at=org.created_at,
                updated_at=org.updated_at,
                role=user_org.role,
                joined_at=user_org.joined_at,
            )
            organizations.append(org_with_role)

        return organizations

    @staticmethod
    async def get_user_role_in_organization(
        db: AsyncSession, user_id: int, organization_id: int
    ) -> Optional[OrganizationRole]:
        """Get user's role in a specific organization."""
        result = await db.execute(
            select(UserOrganization).where(
                and_(
                    UserOrganization.user_id == user_id,
                    UserOrganization.organization_id == organization_id,
                    UserOrganization.is_active,
                )
            )
        )
        user_org = result.scalar_one_or_none()
        return user_org.role if user_org else None

    @staticmethod
    async def is_user_member(
        db: AsyncSession, user_id: int, organization_id: int
    ) -> bool:
        """Check if user is a member of the organization."""
        role = await OrganizationService.get_user_role_in_organization(
            db, user_id, organization_id
        )
        return role is not None

    @staticmethod
    async def create_invitation(
        db: AsyncSession, organization_id: int, created_by: int, data: InvitationCreate
    ) -> OrganizationInvitation:
        """Create an invitation link for an organization."""
        invitation = OrganizationInvitation(
            organization_id=organization_id,
            code=OrganizationInvitation.generate_code(),
            created_by=created_by,
            target_email=data.target_email,
            role=data.role,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=INVITATION_VALIDITY_MINUTES),
            max_uses=data.max_uses,
        )
        db.add(invitation)
        await db.commit()
        await db.refresh(invitation)
        return invitation

    @staticmethod
    async def get_invitation_by_code(
        db: AsyncSession, code: str
    ) -> Optional[OrganizationInvitation]:
        """Get invitation by code."""
        result = await db.execute(
            select(OrganizationInvitation)
            .options(selectinload(OrganizationInvitation.organization))
            .where(OrganizationInvitation.code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def validate_invitation(
        db: AsyncSession, code: str
    ) -> Tuple[bool, str, Optional[OrganizationInvitation]]:
        """
        Validate an invitation code.
        Returns (is_valid, message, invitation).
        """
        invitation = await OrganizationService.get_invitation_by_code(db, code)

        if not invitation:
            return False, "Невалиден код за покана.", None

        if not invitation.is_active:
            return False, "Оваа покана е деактивирана.", None

        if invitation.expires_at < datetime.now(timezone.utc):
            return False, "Оваа покана е истечена.", None

        if invitation.max_uses and invitation.use_count >= invitation.max_uses:
            return False, "Оваа покана ја достигна максималната употреба.", None

        return True, "Поканата е валидна.", invitation

    @staticmethod
    async def join_organization_via_invitation(
        db: AsyncSession, user_id: int, code: str
    ) -> Tuple[bool, str, Optional[Organization], Optional[OrganizationRole]]:
        """
        Join an organization using an invitation code.
        Returns (success, message, organization, role).
        """
        # Validate invitation
        is_valid, message, invitation = await OrganizationService.validate_invitation(
            db, code
        )

        if not is_valid or not invitation:
            return False, message, None, None

        # Check if user is already a member
        is_member = await OrganizationService.is_user_member(
            db, user_id, invitation.organization_id
        )
        if is_member:
            return False, "Веќе сте член на оваа организација.", None, None

        # Check if invitation is for specific email
        if invitation.target_email:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user and user.email != invitation.target_email:
                return False, "Оваа покана е наменета за друга е-пошта.", None, None

        # Create user-organization relationship
        user_org = UserOrganization(
            user_id=user_id,
            organization_id=invitation.organization_id,
            role=invitation.role,
            invited_by=invitation.created_by,
        )
        db.add(user_org)

        # Update invitation use count
        invitation.use_count += 1

        await db.commit()

        # Get the organization
        organization = await OrganizationService.get_organization_by_id(
            db, invitation.organization_id
        )

        return (
            True,
            "Успешно се приклучивте на организацијата!",
            organization,
            invitation.role,
        )

    @staticmethod
    async def update_organization(
        db: AsyncSession, organization_id: int, data: OrganizationUpdate
    ) -> Optional[Organization]:
        """Update organization details."""
        organization = await OrganizationService.get_organization_by_id(
            db, organization_id
        )
        if not organization:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(organization, field, value)

        await db.commit()
        await db.refresh(organization)
        return organization

    @staticmethod
    async def deactivate_invitation(
        db: AsyncSession, invitation_id: int, user_id: int
    ) -> bool:
        """Deactivate an invitation (only by creator or org admin)."""
        result = await db.execute(
            select(OrganizationInvitation).where(
                OrganizationInvitation.id == invitation_id
            )
        )
        invitation = result.scalar_one_or_none()

        if not invitation:
            return False

        # Check if user has permission (creator or admin/owner of org)
        role = await OrganizationService.get_user_role_in_organization(
            db, user_id, invitation.organization_id
        )

        if invitation.created_by != user_id and role not in [
            OrganizationRole.OWNER,
            OrganizationRole.ADMIN,
        ]:
            return False

        invitation.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def get_organization_invitations(
        db: AsyncSession, organization_id: int
    ) -> List[OrganizationInvitation]:
        """Get all invitations for an organization."""
        result = await db.execute(
            select(OrganizationInvitation)
            .where(OrganizationInvitation.organization_id == organization_id)
            .order_by(OrganizationInvitation.created_at.desc())
        )
        return list(result.scalars().all())


# Create singleton instance
organization_service = OrganizationService()
