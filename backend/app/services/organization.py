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
    InvitationWithLink,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationWithRole,
    TeamMember,
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
            role=OrganizationRole.OWNER,
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
    async def create_invitation_with_notification(
        db: AsyncSession,
        organization_id: int,
        inviter_id: int,
        data: InvitationCreate,
    ) -> InvitationWithLink:
        """Create invitation and optionally send email notification."""
        from app.core.config import get_settings
        from app.services.email import email_service
        from app.services.user import UserService

        settings = get_settings()

        invitation = await OrganizationService.create_invitation(
            db, organization_id, inviter_id, data
        )

        # Build the invitation link (frontend URL)
        link = f"/organization?join={invitation.code}"

        # Send invitation email if target_email is provided
        if data.target_email:
            organization = await OrganizationService.get_organization_by_id(
                db, organization_id
            )
            user_service = UserService(db)
            inviter = await user_service.get_by_id(inviter_id)

            # Check if user with this email already exists
            existing_user = await user_service.get_by_email(data.target_email)
            user_exists = existing_user is not None

            if organization:
                email_service.send_organization_invitation_email(
                    to_email=data.target_email,
                    organization_name=organization.company_name,
                    inviter_name=inviter.full_name if inviter else None,
                    role=invitation.role.value,
                    invitation_code=invitation.code,
                    base_url=settings.frontend_url,
                    user_exists=user_exists,
                )

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

        # Check if user is already an active member
        is_member = await OrganizationService.is_user_member(
            db, user_id, invitation.organization_id
        )
        if is_member:
            return False, "Веќе сте член на оваа организација.", None, None

        # Check if invitation is for specific email
        if invitation.target_email:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user and user.email.lower() != invitation.target_email.lower():
                return False, "Оваа покана е наменета за друга е-пошта.", None, None

        # Check if there's an existing inactive membership (user was previously removed)
        result = await db.execute(
            select(UserOrganization).where(
                and_(
                    UserOrganization.user_id == user_id,
                    UserOrganization.organization_id == invitation.organization_id,
                )
            )
        )
        existing_membership = result.scalar_one_or_none()

        if existing_membership:
            # Reactivate the existing membership with the new role
            existing_membership.is_active = True
            existing_membership.role = invitation.role
            existing_membership.invited_by = invitation.created_by
        else:
            # Create new user-organization relationship
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

    @staticmethod
    async def get_organization_members(
        db: AsyncSession, organization_id: int
    ) -> List[TeamMember]:
        """Get all members of an organization with their user details."""
        result = await db.execute(
            select(UserOrganization)
            .options(selectinload(UserOrganization.user))
            .where(
                and_(
                    UserOrganization.organization_id == organization_id,
                    UserOrganization.is_active,
                )
            )
            .order_by(UserOrganization.joined_at.asc())
        )
        user_orgs = result.scalars().all()

        members = []
        for user_org in user_orgs:
            user = user_org.user
            members.append(
                TeamMember(
                    id=user_org.id,
                    user_id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    picture_url=user.picture_url,
                    role=user_org.role,
                    joined_at=user_org.joined_at,
                )
            )

        return members

    @staticmethod
    async def remove_member(
        db: AsyncSession,
        organization_id: int,
        member_id: int,
        requester_id: int,
    ) -> Tuple[bool, str]:
        """
        Remove a member from an organization.
        Returns (success, message).

        Permission rules:
        - Owner can remove anyone except themselves
        - Admin can remove accountants, members, and viewers (not owner or other admins)
        - Cannot remove yourself
        """
        # Get the member to remove
        result = await db.execute(
            select(UserOrganization).where(
                and_(
                    UserOrganization.id == member_id,
                    UserOrganization.organization_id == organization_id,
                    UserOrganization.is_active,
                )
            )
        )
        member = result.scalar_one_or_none()

        if not member:
            return False, "Членот не е пронајден."

        # Cannot remove yourself
        if member.user_id == requester_id:
            return False, "Не можете да се отстраните себеси."

        # Get requester's role
        requester_role = await OrganizationService.get_user_role_in_organization(
            db, requester_id, organization_id
        )

        if not requester_role:
            return False, "Немате пристап до оваа организација."

        # Define role hierarchy (lower number = higher authority)
        role_hierarchy = {
            OrganizationRole.OWNER: 0,
            OrganizationRole.ADMIN: 1,
            OrganizationRole.ACCOUNTANT: 2,
            OrganizationRole.MEMBER: 3,
            OrganizationRole.VIEWER: 4,
        }

        requester_level = role_hierarchy.get(requester_role, 99)
        member_level = role_hierarchy.get(member.role, 99)

        # Only owner and admin can remove members
        if requester_role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
            return False, "Немате дозвола да отстранувате членови."

        # Can only remove users with lower authority
        if requester_level >= member_level:
            return False, "Немате дозвола да го отстраните овој член."

        # Deactivate the membership (soft delete)
        member.is_active = False
        await db.commit()

        return True, "Членот е успешно отстранет."

    @staticmethod
    async def change_member_role(
        db: AsyncSession,
        organization_id: int,
        member_id: int,
        new_role: OrganizationRole,
        requester_id: int,
    ) -> Tuple[bool, str]:
        """
        Change a member's role in an organization.
        Returns (success, message).

        Permission rules:
        - Owner can change anyone's role (except themselves) to any role except owner
        - Admin can change roles of accountants, members, and viewers (not owner or other admins)
        - Admin cannot promote someone to admin or owner
        - Cannot change your own role
        """
        # Get the member whose role will be changed
        result = await db.execute(
            select(UserOrganization).where(
                and_(
                    UserOrganization.id == member_id,
                    UserOrganization.organization_id == organization_id,
                    UserOrganization.is_active,
                )
            )
        )
        member = result.scalar_one_or_none()

        if not member:
            return False, "Членот не е пронајден."

        # Cannot change your own role
        if member.user_id == requester_id:
            return False, "Не можете да ја промените сопствената улога."

        # Get requester's role
        requester_role = await OrganizationService.get_user_role_in_organization(
            db, requester_id, organization_id
        )

        if not requester_role:
            return False, "Немате пристап до оваа организација."

        # Define role hierarchy (lower number = higher authority)
        role_hierarchy = {
            OrganizationRole.OWNER: 0,
            OrganizationRole.ADMIN: 1,
            OrganizationRole.ACCOUNTANT: 2,
            OrganizationRole.MEMBER: 3,
            OrganizationRole.VIEWER: 4,
        }

        requester_level = role_hierarchy.get(requester_role, 99)
        member_current_level = role_hierarchy.get(member.role, 99)
        new_role_level = role_hierarchy.get(new_role, 99)

        # Only owner and admin can change roles
        if requester_role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
            return False, "Немате дозвола да менувате улоги."

        # Cannot change to owner role
        if new_role == OrganizationRole.OWNER:
            return False, "Не може да се додели улога на сопственик."

        # Can only change roles of users with lower authority
        if requester_level >= member_current_level:
            return False, "Немате дозвола да ја промените улогата на овој член."

        # Admin cannot promote someone to admin level
        if (
            requester_role == OrganizationRole.ADMIN
            and new_role_level <= requester_level
        ):
            return False, "Немате дозвола да доделите оваа улога."

        # Update the role
        member.role = new_role
        await db.commit()

        return True, "Улогата е успешно променета."


# Create singleton instance
organization_service = OrganizationService()
