import { api } from '../client'
import type {
  Organization,
  OrganizationWithRole,
  OrganizationRole,
  OrganizationCreate,
  UserOrganizationsResponse,
  InvitationCreate,
  InvitationResponse,
  JoinOrganizationResponse,
  ValidateInvitationResponse,
  TeamMember,
  TeamMembersResponse,
} from '@/types/organization'

// Re-export types for convenience
export type {
  Organization,
  OrganizationWithRole,
  OrganizationRole,
  OrganizationCreate,
  UserOrganizationsResponse,
  InvitationCreate,
  InvitationResponse,
  JoinOrganizationRequest,
  JoinOrganizationResponse,
  ValidateInvitationResponse,
  TeamMember,
  TeamMembersResponse,
} from '@/types/organization'

export const organizationApi = {
  // Get all organizations for current user
  getMyOrganizations: () =>
    api.get<UserOrganizationsResponse>('/organizations'),

  // Create a new organization
  createOrganization: (data: OrganizationCreate) =>
    api.post<Organization>('/organizations', data),

  // Get organization by ID
  getOrganization: (id: number) =>
    api.get<OrganizationWithRole>(`/organizations/${id}`),

  // Update organization
  updateOrganization: (id: number, data: Partial<OrganizationCreate>) =>
    api.put<Organization>(`/organizations/${id}`, data),

  // Create invitation
  createInvitation: (organizationId: number, data: InvitationCreate = {}) =>
    api.post<InvitationResponse>(`/organizations/${organizationId}/invitations`, data),

  // Get invitations for organization
  getInvitations: (organizationId: number) =>
    api.get<InvitationResponse[]>(`/organizations/${organizationId}/invitations`),

  // Deactivate invitation
  deactivateInvitation: (organizationId: number, invitationId: number) =>
    api.delete(`/organizations/${organizationId}/invitations/${invitationId}`),

  // Join organization via code
  joinOrganization: (code: string) =>
    api.post<JoinOrganizationResponse>('/organizations/join', { code }),

  // Validate invitation code
  validateInvitation: (code: string) =>
    api.get<ValidateInvitationResponse>(`/organizations/join/validate?code=${encodeURIComponent(code)}`),

  // Get organization members
  getMembers: (organizationId: number) =>
    api.get<TeamMembersResponse>(`/organizations/${organizationId}/members`),

  // Remove a member from the organization
  removeMember: (organizationId: number, memberId: number) =>
    api.delete(`/organizations/${organizationId}/members/${memberId}`),

  // Change a member's role
  changeMemberRole: (organizationId: number, memberId: number, role: OrganizationRole) =>
    api.patch<TeamMember>(`/organizations/${organizationId}/members/${memberId}/role`, { role }),
}

export default organizationApi
