<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { OrganizationRole, InvitationResponse } from '@/types/organization.ts'

const props = defineProps<{
  show: boolean
  userRole: OrganizationRole
  createdInvitation: InvitationResponse | null
  loading: boolean
  error: string
}>()

const emit = defineEmits<{
  close: []
  create: [data: { email: string; role: OrganizationRole; sendEmail: boolean }]
  copy: [invitation: InvitationResponse]
  createAnother: []
}>()

const { t } = useI18n()

// Get base URL for invitation links
const baseUrl = computed(() => window.location.origin)

// Form state
const inviteForm = ref({
  email: '',
  role: 'member' as OrganizationRole,
  sendEmail: true,
})

// Available roles for invitation
const availableRoles = computed(() => {
  const roles: { value: OrganizationRole; label: string }[] = [
    { value: 'viewer', label: t('organization.roles.viewer') },
    { value: 'member', label: t('organization.roles.member') },
    { value: 'accountant', label: t('organization.roles.accountant') },
  ]

  // Only owner can invite admins
  if (props.userRole === 'owner') {
    roles.push({ value: 'admin', label: t('organization.roles.admin') })
  }

  return roles
})

// Reset form when modal opens
watch(() => props.show, (newVal) => {
  if (newVal && !props.createdInvitation) {
    inviteForm.value = {
      email: '',
      role: 'member',
      sendEmail: true,
    }
  }
})

const handleCreate = () => {
  emit('create', {
    email: inviteForm.value.email,
    role: inviteForm.value.role,
    sendEmail: inviteForm.value.sendEmail,
  })
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <!-- Backdrop -->
      <div
        class="absolute inset-0 bg-black/50"
        @click="emit('close')"
      ></div>

      <!-- Modal Content -->
      <div class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-xl max-w-md w-full p-6">
        <h3 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
          {{ t('settings.manageTeam.inviteMember') }}
        </h3>

        <!-- Created Invitation View -->
        <div v-if="createdInvitation">
          <div class="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <p class="text-green-700 dark:text-green-300 font-medium mb-2">
              {{ t('settings.manageTeam.inviteCreated') }}
            </p>
            <p class="text-sm text-green-600 dark:text-green-400">
              {{ t('settings.manageTeam.inviteExpiresIn') }}
            </p>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              {{ t('settings.manageTeam.invitationLink') }}
            </label>
            <div class="flex gap-2">
              <input
                :value="`${baseUrl}/organization?join=${createdInvitation.code}`"
                type="text"
                readonly
                class="flex-1 px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-white text-sm font-mono"
              />
              <button
                @click="emit('copy', createdInvitation)"
                class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
              >
                {{ t('settings.manageTeam.copy') }}
              </button>
            </div>
          </div>

          <div class="flex gap-2">
            <button
              @click="emit('close')"
              class="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors font-medium"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              @click="emit('createAnother')"
              class="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
            >
              {{ t('settings.manageTeam.createAnother') }}
            </button>
          </div>
        </div>

        <!-- Create Invitation Form -->
        <div v-else>
          <div class="space-y-4 mb-6">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                {{ t('settings.manageTeam.emailOptional') }}
              </label>
              <input
                v-model="inviteForm.email"
                type="email"
                :placeholder="t('settings.manageTeam.emailPlaceholder')"
                class="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
              />
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {{ t('settings.manageTeam.emailHint') }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                {{ t('settings.manageTeam.role') }}
              </label>
              <select
                v-model="inviteForm.role"
                class="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
              >
                <option v-for="role in availableRoles" :key="role.value" :value="role.value">
                  {{ role.label }}
                </option>
              </select>
            </div>

            <div v-if="inviteForm.email" class="flex items-center gap-3">
              <input
                v-model="inviteForm.sendEmail"
                type="checkbox"
                id="sendEmail"
                class="w-5 h-5 rounded border-slate-300 dark:border-slate-600 text-blue-500 focus:ring-blue-500"
              />
              <label for="sendEmail" class="text-sm text-slate-700 dark:text-slate-300">
                {{ t('settings.manageTeam.sendEmailInvite') }}
              </label>
            </div>
          </div>

          <!-- Error -->
          <div v-if="error" class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300 text-sm">
            {{ error }}
          </div>

          <div class="flex gap-2">
            <button
              @click="emit('close')"
              class="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors font-medium"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              @click="handleCreate"
              :disabled="loading"
              class="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium disabled:opacity-50"
            >
              {{ loading ? t('common.loading') : t('settings.manageTeam.createInvite') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
