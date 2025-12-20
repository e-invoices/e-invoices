<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { organizationApi } from '@/api/v1/organization.ts'
import { useAuth } from '@/composables/useAuth.ts'
import type { OrganizationWithRole, OrganizationRole, InvitationResponse, TeamMember } from '@/types/organization.ts'

// Child components
import TeamMemberCard from './team/TeamMemberCard.vue'
import RemoveMemberModal from './team/RemoveMemberModal.vue'
import ChangeRoleModal from './team/ChangeRoleModal.vue'
import InviteMemberModal from './team/InviteMemberModal.vue'
import InvitationsList from './team/InvitationsList.vue'

const props = defineProps<{
  organization: OrganizationWithRole | null
  userRole: OrganizationRole
  canManage: boolean
}>()

const { t } = useI18n()
const { currentUser } = useAuth()

// State
const loading = ref(false)
const membersLoading = ref(false)
const invitations = ref<InvitationResponse[]>([])
const members = ref<TeamMember[]>([])
const searchQuery = ref('')
const error = ref('')
const success = ref('')

// Modal states
const showInviteModal = ref(false)
const showRemoveModal = ref(false)
const showRoleModal = ref(false)

// Member action states
const memberToRemove = ref<TeamMember | null>(null)
const memberToChangeRole = ref<TeamMember | null>(null)
const removingMember = ref(false)
const changingRole = ref(false)
const removeError = ref('')
const roleChangeError = ref('')

// Invite state
const createdInvitation = ref<InvitationResponse | null>(null)
const creatingInvite = ref(false)
const inviteError = ref('')

// Load invitations
const loadInvitations = async () => {
  if (!props.organization) return

  loading.value = true
  try {
    invitations.value = await organizationApi.getInvitations(props.organization.id)
  } catch (err) {
    console.error('Failed to load invitations', err)
  } finally {
    loading.value = false
  }
}

// Load members
const loadMembers = async () => {
  if (!props.organization) return

  membersLoading.value = true
  try {
    const response = await organizationApi.getMembers(props.organization.id)
    members.value = response.members
  } catch (err) {
    console.error('Failed to load members', err)
  } finally {
    membersLoading.value = false
  }
}

// Filtered members based on search, with current user first
const filteredMembers = computed(() => {
  let result = members.value

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      member =>
        member.full_name.toLowerCase().includes(query) ||
        member.email.toLowerCase().includes(query)
    )
  }

  // Sort to put current user first
  if (currentUser.value) {
    const currentUserId = currentUser.value.id
    result = [...result].sort((a, b) => {
      if (a.user_id === currentUserId) return -1
      if (b.user_id === currentUserId) return 1
      return 0
    })
  }

  return result
})

// Check if a member is the current logged-in user
const isCurrentUser = (member: TeamMember) => {
  return currentUser.value?.id === member.user_id
}

// Role hierarchy helper
const getRoleLevel = (role: OrganizationRole) => {
  const hierarchy: Record<string, number> = {
    owner: 0,
    admin: 1,
    accountant: 2,
    member: 3,
    viewer: 4,
  }
  return hierarchy[role] ?? 99
}

// Check if current user can remove a specific member
const canRemoveMember = (member: TeamMember) => {
  if (!['owner', 'admin'].includes(props.userRole)) return false
  const myLevel = getRoleLevel(props.userRole)
  const memberLevel = getRoleLevel(member.role)
  return myLevel < memberLevel
}

// Check if current user can change a specific member's role
const canChangeRole = (member: TeamMember) => {
  if (!['owner', 'admin'].includes(props.userRole)) return false
  if (isCurrentUser(member)) return false
  const myLevel = getRoleLevel(props.userRole)
  const memberLevel = getRoleLevel(member.role)
  return myLevel < memberLevel
}

// Get available roles for changing a member's role
const getAvailableRolesForMember = (member: TeamMember | null): OrganizationRole[] => {
  if (!member) return []
  const allRoles: OrganizationRole[] = ['admin', 'accountant', 'member', 'viewer']

  if (props.userRole === 'owner') {
    return allRoles.filter(r => r !== member.role)
  }

  if (props.userRole === 'admin') {
    return allRoles.filter(r => r !== 'admin' && r !== member.role)
  }

  return []
}

// Remove member handlers
const openRemoveModal = (member: TeamMember) => {
  memberToRemove.value = member
  removeError.value = ''
  showRemoveModal.value = true
}

const closeRemoveModal = () => {
  memberToRemove.value = null
  showRemoveModal.value = false
  removeError.value = ''
}

const handleRemoveMember = async () => {
  if (!props.organization || !memberToRemove.value) return

  removingMember.value = true
  removeError.value = ''
  const memberName = memberToRemove.value.full_name

  try {
    await organizationApi.removeMember(props.organization.id, memberToRemove.value.id)
    await loadMembers()
    closeRemoveModal()
    success.value = t('settings.manageTeam.memberRemoved', { name: memberName })
  } catch (err: unknown) {
    const errorResponse = err as { response?: { data?: { detail?: string } } }
    removeError.value = errorResponse.response?.data?.detail || t('settings.manageTeam.removeFailed')
  } finally {
    removingMember.value = false
  }
}

// Change role handlers
const openRoleModal = (member: TeamMember) => {
  memberToChangeRole.value = member
  roleChangeError.value = ''
  showRoleModal.value = true
}

const closeRoleModal = () => {
  memberToChangeRole.value = null
  showRoleModal.value = false
  roleChangeError.value = ''
}

const handleChangeRole = async (newRole: OrganizationRole) => {
  if (!props.organization || !memberToChangeRole.value) return

  changingRole.value = true
  roleChangeError.value = ''
  const memberName = memberToChangeRole.value.full_name

  try {
    await organizationApi.changeMemberRole(
      props.organization.id,
      memberToChangeRole.value.id,
      newRole
    )
    await loadMembers()
    closeRoleModal()
    success.value = t('settings.manageTeam.roleChanged', {
      name: memberName,
      role: t(`organization.roles.${newRole}`)
    })
  } catch (err: unknown) {
    const errorResponse = err as { response?: { data?: { detail?: string } } }
    roleChangeError.value = errorResponse.response?.data?.detail || t('settings.manageTeam.roleChangeFailed')
  } finally {
    changingRole.value = false
  }
}

// Invite handlers
const openInviteModal = () => {
  createdInvitation.value = null
  inviteError.value = ''
  success.value = ''
  showInviteModal.value = true
}

const closeInviteModal = () => {
  showInviteModal.value = false
  createdInvitation.value = null
}

const handleCreateInvitation = async (data: { email: string; role: OrganizationRole; sendEmail: boolean }) => {
  if (!props.organization) return

  creatingInvite.value = true
  inviteError.value = ''

  try {
    const invitation = await organizationApi.createInvitation(props.organization.id, {
      role: data.role,
      target_email: data.email || undefined,
    })

    createdInvitation.value = invitation

    if (data.sendEmail && data.email) {
      success.value = t('settings.manageTeam.inviteSent', { email: data.email })
    }

    await loadInvitations()
  } catch (err: unknown) {
    const errorResponse = err as { response?: { data?: { detail?: string } } }
    inviteError.value = errorResponse.response?.data?.detail || t('settings.manageTeam.inviteFailed')
  } finally {
    creatingInvite.value = false
  }
}

const handleCopyInvitation = async (invitation: InvitationResponse) => {
  const link = `${window.location.origin}/organization?join=${invitation.code}`

  try {
    await navigator.clipboard.writeText(link)
  } catch {
    const textArea = document.createElement('textarea')
    textArea.value = link
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
  }
}

const handleDeactivateInvitation = async (invitation: InvitationResponse) => {
  if (!props.organization) return

  try {
    await organizationApi.deactivateInvitation(props.organization.id, invitation.id)
    await loadInvitations()
  } catch (err: unknown) {
    const errorResponse = err as { response?: { data?: { detail?: string } } }
    error.value = errorResponse.response?.data?.detail || t('settings.manageTeam.deactivateFailed')
  }
}

const handleCreateAnother = () => {
  createdInvitation.value = null
}

onMounted(() => {
  loadMembers()
  if (props.canManage) {
    loadInvitations()
  }
})
</script>

<template>
  <div class="p-6 sm:p-8">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-slate-900 dark:text-white">
        {{ t('settings.manageTeam.title') }}
      </h2>
      <button
        v-if="canManage"
        @click="openInviteModal"
        class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        {{ t('settings.manageTeam.inviteMember') }}
      </button>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="success" class="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-300">
      {{ success }}
    </div>
    <div v-if="error" class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300">
      {{ error }}
    </div>

    <!-- Not Allowed Message -->
    <div v-if="!canManage" class="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg text-amber-700 dark:text-amber-300">
      {{ t('settings.manageTeam.noPermission') }}
    </div>

    <!-- Loading -->
    <div v-if="membersLoading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>

    <!-- Team Members Section -->
    <div v-else class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
          {{ t('settings.manageTeam.teamMembers') }} ({{ members.length }})
        </h3>
      </div>

      <!-- Search Bar -->
      <div class="relative mb-4">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="t('settings.manageTeam.searchPlaceholder')"
          class="w-full pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400"
        />
      </div>

      <!-- Members List -->
      <div v-if="filteredMembers.length === 0" class="text-center py-8 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
        <svg class="w-12 h-12 mx-auto text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="text-slate-600 dark:text-slate-400">
          {{ searchQuery ? t('settings.manageTeam.noMembersFound') : t('settings.manageTeam.noMembers') }}
        </p>
      </div>

      <div v-else class="space-y-2">
        <TeamMemberCard
          v-for="member in filteredMembers"
          :key="member.id"
          :member="member"
          :is-current-user="isCurrentUser(member)"
          :can-change-role="canChangeRole(member)"
          :can-remove="canRemoveMember(member)"
          @change-role="openRoleModal"
          @remove="openRemoveModal"
        />
      </div>
    </div>

    <!-- Pending Invitations Section (only for managers) -->
    <InvitationsList
      v-if="canManage"
      :invitations="invitations"
      :loading="loading"
      @copy="handleCopyInvitation"
      @deactivate="handleDeactivateInvitation"
    />

    <!-- Modals -->
    <RemoveMemberModal
      :show="showRemoveModal"
      :member="memberToRemove"
      :loading="removingMember"
      :error="removeError"
      @close="closeRemoveModal"
      @confirm="handleRemoveMember"
    />

    <ChangeRoleModal
      :show="showRoleModal"
      :member="memberToChangeRole"
      :available-roles="getAvailableRolesForMember(memberToChangeRole)"
      :loading="changingRole"
      :error="roleChangeError"
      @close="closeRoleModal"
      @confirm="handleChangeRole"
    />

    <InviteMemberModal
      :show="showInviteModal"
      :user-role="userRole"
      :created-invitation="createdInvitation"
      :loading="creatingInvite"
      :error="inviteError"
      @close="closeInviteModal"
      @create="handleCreateInvitation"
      @copy="handleCopyInvitation"
      @create-another="handleCreateAnother"
    />
  </div>
</template>
