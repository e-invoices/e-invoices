export interface Organization {
  id: number
  company_name: string
  registration_name: string
  edb: string
  embs: string
  vat_registered: boolean
  address: string
  contact_person: string
  contact_email: string
  contact_phone: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface OrganizationWithRole extends Organization {
  role: OrganizationRole
  joined_at: string
}

export type OrganizationRole = 'owner' | 'admin' | 'accountant' | 'member' | 'viewer'

export interface OrganizationCreate {
  company_name: string
  registration_name: string
  edb: string
  embs: string
  vat_registered: boolean
  address: string
  contact_person: string
  contact_email: string
  contact_phone: string
}

export interface UserOrganizationsResponse {
  organizations: OrganizationWithRole[]
  total: number
}

export interface InvitationCreate {
  role?: OrganizationRole
  target_email?: string
  max_uses?: number
}

export interface InvitationResponse {
  id: number
  organization_id: number
  code: string
  role: OrganizationRole
  target_email: string | null
  expires_at: string
  max_uses: number | null
  use_count: number
  is_active: boolean
  created_at: string
  link?: string
}

export interface JoinOrganizationRequest {
  code: string
}

export interface JoinOrganizationResponse {
  message: string
  organization: Organization
  role: OrganizationRole
}

export interface ValidateInvitationResponse {
  valid: boolean
  organization_name: string
  role: OrganizationRole
  already_member: boolean
}
