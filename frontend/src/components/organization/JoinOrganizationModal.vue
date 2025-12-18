<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { organizationApi } from '@/api/v1/organization'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const { t } = useI18n()

interface OrganizationPreview {
  organization_name: string
  role: string
  already_member: boolean
}

const invitationCode = ref('')
const loading = ref(false)
const validating = ref(false)
const error = ref('')
const organizationPreview = ref<OrganizationPreview | null>(null)

// Reset state when modal opens/closes
watch(() => props.show, (isVisible) => {
  if (!isVisible) {
    invitationCode.value = ''
    error.value = ''
    organizationPreview.value = null
    loading.value = false
    validating.value = false
  }
})

// Extract code from full URL or use as-is
const extractCode = (input: string): string => {
  // Check if it's a full URL with code parameter
  try {
    if (input.includes('?code=') || input.includes('&code=')) {
      const url = new URL(input, window.location.origin)
      return url.searchParams.get('code') || input
    }
  } catch {
    // Not a valid URL, use as-is
  }
  return input.trim()
}

const validateCode = async () => {
  const code = extractCode(invitationCode.value)
  if (!code) {
    error.value = t('organization.join.enterCode')
    return
  }

  try {
    validating.value = true
    error.value = ''
    organizationPreview.value = null

    const response = await organizationApi.validateInvitation(code)

    if (response.already_member) {
      error.value = t('organization.join.alreadyMember')
      return
    }

    organizationPreview.value = response
  } catch (err) {
    error.value = (err as Error).message || t('organization.join.invalidCode')
  } finally {
    validating.value = false
  }
}

const joinOrganization = async () => {
  const code = extractCode(invitationCode.value)
  if (!code) {
    error.value = t('organization.join.enterCode')
    return
  }

  try {
    loading.value = true
    error.value = ''

    await organizationApi.joinOrganization(code)
    emit('success')
  } catch (err) {
    error.value = (err as Error).message || t('organization.join.joinFailed')
  } finally {
    loading.value = false
  }
}

const getRoleLabel = (role: string) => {
  const labels: Record<string, string> = {
    owner: t('organization.roles.owner'),
    admin: t('organization.roles.admin'),
    accountant: t('organization.roles.accountant'),
    member: t('organization.roles.member'),
    viewer: t('organization.roles.viewer'),
  }
  return labels[role] || role
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50 backdrop-blur-sm"
          @click="emit('close')"
        ></div>

        <!-- Modal -->
        <div class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-xl w-full max-w-md p-6 sm:p-8">
          <!-- Close Button -->
          <button
            @click="emit('close')"
            class="absolute top-4 right-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <!-- Header -->
          <div class="text-center mb-6">
            <div class="w-16 h-16 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </div>
            <h2 class="text-xl font-bold text-slate-900 dark:text-white">
              {{ t('organization.join.title') }}
            </h2>
            <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
              {{ t('organization.join.subtitle') }}
            </p>
          </div>

          <!-- Form -->
          <div class="space-y-4">
            <!-- Code Input -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                {{ t('organization.join.codeLabel') }}
              </label>
              <div class="flex gap-2">
                <input
                  v-model="invitationCode"
                  type="text"
                  :placeholder="t('organization.join.codePlaceholder')"
                  class="flex-1 px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-shadow"
                  :disabled="loading"
                  @keyup.enter="organizationPreview ? joinOrganization() : validateCode()"
                />
                <button
                  v-if="!organizationPreview"
                  @click="validateCode"
                  :disabled="validating || !invitationCode.trim()"
                  class="px-4 py-3 bg-slate-100 dark:bg-slate-600 text-slate-700 dark:text-slate-200 font-medium rounded-lg hover:bg-slate-200 dark:hover:bg-slate-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <span v-if="validating">...</span>
                  <span v-else>{{ t('organization.join.validate') }}</span>
                </button>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm p-3 rounded-lg">
              {{ error }}
            </div>

            <!-- Organization Preview -->
            <div
              v-if="organizationPreview"
              class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4"
            >
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-green-100 dark:bg-green-800 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div>
                  <p class="font-semibold text-slate-900 dark:text-white">
                    {{ organizationPreview.organization_name }}
                  </p>
                  <p class="text-sm text-slate-500 dark:text-slate-400">
                    {{ t('organization.join.rolePreview') }}: {{ getRoleLabel(organizationPreview.role) }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Join Button -->
            <button
              v-if="organizationPreview"
              @click="joinOrganization"
              :disabled="loading"
              class="w-full py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg shadow-lg shadow-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span v-if="loading" class="flex items-center justify-center gap-2">
                <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ t('organization.join.joining') }}
              </span>
              <span v-else>{{ t('organization.join.joinButton') }}</span>
            </button>
          </div>

          <!-- Help Text -->
          <p class="text-xs text-slate-400 dark:text-slate-500 text-center mt-4">
            {{ t('organization.join.helpText') }}
          </p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active > div:last-child,
.modal-leave-active > div:last-child {
  transition: transform 0.2s ease;
}

.modal-enter-from > div:last-child,
.modal-leave-to > div:last-child {
  transform: scale(0.95);
}
</style>
