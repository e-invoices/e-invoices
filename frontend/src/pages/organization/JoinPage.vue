<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '@/composables/useAuth'
import { organizationApi } from '@/api/v1/organization'
import type { ValidateInvitationResponse } from '@/types/organization'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const { isAuthenticated, currentUser, logout, checkSession } = useAuth()

const loading = ref(true)
const error = ref('')
const invitationData = ref<ValidateInvitationResponse | null>(null)

const invitationCode = computed(() => route.query.code as string || '')

// Check if logged-in user's email matches the invitation target
const emailMismatch = computed(() => {
  if (!isAuthenticated.value || !invitationData.value?.target_email) {
    return false
  }
  const currentEmail = invitationData.value.current_user_email || currentUser.value?.email
  if (!currentEmail) return false
  return currentEmail.toLowerCase() !== invitationData.value.target_email.toLowerCase()
})

// Computed properties for template display
const targetEmail = computed(() => invitationData.value?.target_email ?? '')
const loggedInEmail = computed(() => invitationData.value?.current_user_email ?? '')

const validateAndJoin = async () => {
  if (!invitationCode.value) {
    error.value = t('organization.join.invalidCode')
    loading.value = false
    return
  }

  try {
    // First check if user has a session (token in localStorage)
    const hasToken = !!localStorage.getItem('access_token')
    if (hasToken && !isAuthenticated.value) {
      // Verify the session is valid - wait for it to complete
      await checkSession()
    }

    // Now validate the invitation
    const validation = await organizationApi.validateInvitation(invitationCode.value)
    invitationData.value = validation

    // Re-check authentication after validation (in case checkSession updated it)
    if (!isAuthenticated.value) {
      // User is not authenticated, redirect to login/register
      await router.push({
        path: '/login',
        query: { redirect: `/organization/join?code=${invitationCode.value}` }
      })
      return
    }

    // Check if already a member
    if (validation.already_member) {
      // User is already a member - set org ID and redirect directly to overview
      localStorage.setItem('selected_organization_id', validation.organization_id.toString())
      await router.push('/organization/overview')
      return
    }

    // User is authenticated - check if email matches (if invitation has target email)
    if (emailMismatch.value) {
      loading.value = false
      return // Show the email mismatch UI
    }

    // Try to join the organization
    const joinResult = await organizationApi.joinOrganization(invitationCode.value)

    // Successfully joined - redirect to the organization
    localStorage.setItem('selected_organization_id', joinResult.organization.id.toString())
    await router.push('/organization/overview')
  } catch (err: unknown) {
    const e = err as { message?: string }
    const errorMessage = e.message || t('organization.join.error')

    // Check for specific error cases
    if (errorMessage.includes('already a member') || errorMessage.includes('веќе член')) {
      // User is already a member - set org ID and redirect directly to overview
      if (invitationData.value?.organization_id) {
        localStorage.setItem('selected_organization_id', invitationData.value.organization_id.toString())
        await router.push('/organization/overview')
      } else {
        await router.push('/organization')
      }
      return
    }

    if (errorMessage.includes('different email') || errorMessage.includes('друга е-пошта')) {
      // Email mismatch from backend - show the mismatch UI
      loading.value = false
      return
    }

    error.value = errorMessage
    loading.value = false
  }
}

const handleLogoutAndRetry = async () => {
  logout()
  // After logout, redirect to login with the invitation
  await router.push({
    path: '/login',
    query: { redirect: `/organization/join?code=${invitationCode.value}` }
  })
}

const goToOrganizations = () => {
  router.push('/organization')
}

onMounted(() => {
  validateAndJoin()
})
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Loading State -->
      <div v-if="loading" class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p class="text-slate-600 dark:text-slate-400">{{ t('organization.join.processing') }}</p>
      </div>

      <!-- Email Mismatch -->
      <div v-else-if="emailMismatch" class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
        <div class="text-center mb-6">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
            <svg class="w-8 h-8 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">
            {{ t('organization.join.emailMismatch') }}
          </h2>
        </div>

        <div class="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4 mb-6">
          <p class="text-sm text-slate-600 dark:text-slate-400 mb-2">
            {{ t('organization.join.invitationFor') }}
          </p>
          <p class="font-medium text-slate-900 dark:text-white">
            {{ targetEmail }}
          </p>
          <p class="text-sm text-slate-600 dark:text-slate-400 mt-3 mb-2">
            {{ t('organization.join.loggedInAs') }}
          </p>
          <p class="font-medium text-slate-900 dark:text-white">
            {{ loggedInEmail }}
          </p>
        </div>

        <p class="text-sm text-slate-600 dark:text-slate-400 mb-6">
          {{ t('organization.join.emailMismatchDescription') }}
        </p>

        <div class="flex flex-col gap-3">
          <button
            @click="handleLogoutAndRetry"
            class="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            {{ t('organization.join.switchAccount') }}
          </button>
          <button
            @click="goToOrganizations"
            class="w-full py-3 px-4 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 font-medium rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            {{ t('organization.join.goToMyOrganizations') }}
          </button>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
        <div class="text-center mb-6">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <svg class="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">
            {{ t('organization.join.errorTitle') }}
          </h2>
          <p class="text-slate-600 dark:text-slate-400">
            {{ error }}
          </p>
        </div>

        <button
          @click="goToOrganizations"
          class="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          {{ t('organization.join.goToMyOrganizations') }}
        </button>
      </div>
    </div>
  </div>
</template>
