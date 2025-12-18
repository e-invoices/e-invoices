<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '@/composables/useAuth'
import { authApi } from '@/api/v1/auth'
import type { GoogleCredentialResponse } from '@/types/auth'

const { t } = useI18n()
const { currentUser, loadGoogleScript, isGoogleLoaded } = useAuth()

// Modal states
const showEditProfileModal = ref(false)

// Form states
const editProfileForm = ref({
  full_name: ''
})

// Loading and error states
const isUpdatingProfile = ref(false)
const isRequestingPasswordReset = ref(false)
const isLinkingGoogle = ref(false)

// Error/success keys (for i18n reactivity)
const profileErrorKey = ref('')
const passwordErrorKey = ref('')
const googleErrorKey = ref('')

const profileSuccessKey = ref('')
const passwordSuccessKey = ref('')
const googleSuccessKey = ref('')

// Computed translated messages
const profileError = computed(() => profileErrorKey.value ? t(profileErrorKey.value) : '')
const passwordError = computed(() => passwordErrorKey.value ? t(passwordErrorKey.value) : '')
const googleError = computed(() => googleErrorKey.value ? t(googleErrorKey.value) : '')

const profileSuccess = computed(() => profileSuccessKey.value ? t(profileSuccessKey.value) : '')
const passwordSuccess = computed(() => passwordSuccessKey.value ? t(passwordSuccessKey.value) : '')
const googleSuccess = computed(() => googleSuccessKey.value ? t(googleSuccessKey.value) : '')

// Form errors
const profileFormErrors = ref<{ full_name?: string }>({})

// Computed properties for user data
const userFullName = computed(() => currentUser.value?.full_name || '')
const userEmail = computed(() => currentUser.value?.email || '')
const userHasPassword = computed(() => currentUser.value?.has_password || false)
const userAuthProvider = computed(() => currentUser.value?.auth_provider || 'email')
const userPictureUrl = computed(() => currentUser.value?.picture_url || '')
const userInitials = computed(() => {
  const name = userFullName.value
  if (name) {
    return name.substring(0, 2).toUpperCase()
  }
  return '?'
})

// Computed
const canConnectGoogle = computed(() => {
  return currentUser.value && userAuthProvider.value !== 'google'
})

// Open modals
const openEditProfile = () => {
  editProfileForm.value.full_name = userFullName.value
  profileErrorKey.value = ''
  profileSuccessKey.value = ''
  profileFormErrors.value = {}
  showEditProfileModal.value = true
}

// Validate forms
const validateProfileForm = () => {
  profileFormErrors.value = {}
  if (!editProfileForm.value.full_name.trim()) {
    profileFormErrors.value.full_name = t('account.settings.errors.fullNameRequired')
  }
  return Object.keys(profileFormErrors.value).length === 0
}

// Submit handlers
const handleUpdateProfile = async () => {
  if (!validateProfileForm()) return

  isUpdatingProfile.value = true
  profileErrorKey.value = ''
  profileSuccessKey.value = ''

  try {
    const updatedUser = await authApi.updateProfile({
      full_name: editProfileForm.value.full_name.trim()
    })

    if (currentUser.value) {
      currentUser.value.full_name = updatedUser.full_name
    }

    profileSuccessKey.value = 'account.settings.profileUpdated'
    setTimeout(() => {
      showEditProfileModal.value = false
    }, 1500)
  } catch {
    profileErrorKey.value = 'account.settings.profileUpdateFailed'
  } finally {
    isUpdatingProfile.value = false
  }
}

// Request password reset email (for both set and change password)
const handleRequestPasswordReset = async () => {
  isRequestingPasswordReset.value = true
  passwordErrorKey.value = ''
  passwordSuccessKey.value = ''

  try {
    await authApi.requestPasswordReset()
    passwordSuccessKey.value = 'account.settings.passwordResetEmailSent'
  } catch {
    passwordErrorKey.value = 'account.settings.passwordResetFailed'
  } finally {
    isRequestingPasswordReset.value = false
  }
}

// Google OAuth handler
const handleGoogleLink = async (response: GoogleCredentialResponse) => {
  isLinkingGoogle.value = true
  googleErrorKey.value = ''
  googleSuccessKey.value = ''

  try {
    const updatedUser = await authApi.linkGoogle({
      credential: response.credential
    })

    if (currentUser.value) {
      currentUser.value.auth_provider = updatedUser.auth_provider
      currentUser.value.picture_url = updatedUser.picture_url
    }

    googleSuccessKey.value = 'account.settings.googleLinked'
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : String(error)

    if (errorMessage.includes('already linked to another user')) {
      googleErrorKey.value = 'account.settings.googleAlreadyLinked'
    } else {
      googleErrorKey.value = 'account.settings.googleLinkFailed'
    }
  } finally {
    isLinkingGoogle.value = false
  }
}

// Initialize Google button for linking
const initGoogleLinkButton = () => {
  if (!isGoogleLoaded.value || !window.google || !canConnectGoogle.value) return

  try {
    window.google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      callback: handleGoogleLink,
      auto_select: false,
      cancel_on_tap_outside: true,
    })

    const buttonElement = document.getElementById('google-link-button')
    if (buttonElement) {
      window.google.accounts.id.renderButton(buttonElement, {
        theme: 'outline',
        size: 'large',
        width: 250,
        text: 'continue_with',
        shape: 'rectangular',
        logo_alignment: 'center',
      })
    }
  } catch (error) {
    console.warn('Failed to initialize Google link button:', error)
  }
}

onMounted(async () => {
  await loadGoogleScript()
  initGoogleLinkButton()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-slate-950">
    <div class="max-w-3xl mx-auto px-4 py-8 sm:py-12">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">
          {{ t('account.settings.title') }}
        </h1>
        <p class="mt-1 text-slate-500 dark:text-slate-400">
          {{ t('account.settings.subtitle') }}
        </p>
      </div>

      <!-- Profile Section -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">
            {{ t('account.settings.profile') }}
          </h2>
          <button
            @click="openEditProfile"
            class="px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
          >
            {{ t('account.settings.editProfile') }}
          </button>
        </div>

        <div class="flex items-center gap-4">
          <!-- Avatar -->
          <div class="w-16 h-16 rounded-full flex items-center justify-center overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600 text-white font-bold text-xl">
            <img
              v-if="userPictureUrl"
              :src="userPictureUrl"
              :alt="userFullName || userEmail"
              class="w-full h-full object-cover"
              referrerpolicy="no-referrer"
            />
            <span v-else>{{ userInitials }}</span>
          </div>
          <div>
            <p class="font-medium text-slate-900 dark:text-white">
              {{ userFullName || userEmail }}
            </p>
            <p class="text-sm text-slate-500 dark:text-slate-400">
              {{ userEmail }}
            </p>
          </div>
        </div>
      </div>

      <!-- Security Section -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm p-6">
        <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          {{ t('account.settings.security') }}
        </h2>

        <div class="space-y-4">
          <!-- Password -->
          <div class="flex items-center justify-between py-3 border-b border-slate-200 dark:border-slate-700">
            <div>
              <p class="font-medium text-slate-900 dark:text-white">{{ t('account.settings.password') }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">
                {{ userHasPassword ? t('account.settings.passwordSet') : t('account.settings.passwordNotSet') }}
              </p>
            </div>
            <button
              @click="handleRequestPasswordReset"
              :disabled="isRequestingPasswordReset"
              class="px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors disabled:opacity-50"
            >
              <span v-if="isRequestingPasswordReset">{{ t('common.loading') }}</span>
              <span v-else>{{ userHasPassword ? t('account.settings.changePassword') : t('account.settings.setPassword') }}</span>
            </button>
          </div>

          <!-- Password success/error messages -->
          <div v-if="passwordSuccess" class="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <p class="text-sm text-green-700 dark:text-green-300">{{ passwordSuccess }}</p>
          </div>
          <div v-if="passwordError" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p class="text-sm text-red-700 dark:text-red-300">{{ passwordError }}</p>
          </div>

          <!-- Connected Accounts -->
          <div class="py-3">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">{{ t('account.settings.connectedAccounts') }}</p>
                <p class="text-sm text-slate-500 dark:text-slate-400">
                  {{ userAuthProvider === 'google' ? t('account.settings.googleConnected') : t('account.settings.emailOnly') }}
                </p>
              </div>
              <div class="flex items-center gap-2">
                <svg v-if="userAuthProvider === 'google'" class="w-6 h-6" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span v-if="userAuthProvider === 'google'" class="text-sm text-green-600 dark:text-green-400">
                  {{ t('account.settings.connected') }}
                </span>
              </div>
            </div>

            <!-- Connect Google Button -->
            <div v-if="canConnectGoogle" class="mt-4">
              <p class="text-sm text-slate-500 dark:text-slate-400 mb-3">
                {{ t('account.settings.connectGoogleDescription') }}
              </p>
              <div id="google-link-button" class="flex justify-start"></div>
            </div>

            <!-- Google success/error messages (shown outside conditional to always be visible) -->
            <p v-if="googleError" class="mt-2 text-sm text-red-600 dark:text-red-400">{{ googleError }}</p>
            <p v-if="googleSuccess" class="mt-2 text-sm text-green-600 dark:text-green-400">{{ googleSuccess }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showEditProfileModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="showEditProfileModal = false">
          <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl w-full max-w-md p-6">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              {{ t('account.settings.editProfile') }}
            </h3>

            <form @submit.prevent="handleUpdateProfile" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  {{ t('account.settings.fullName') }}
                </label>
                <input
                  v-model="editProfileForm.full_name"
                  type="text"
                  :placeholder="t('account.settings.fullNamePlaceholder')"
                  class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                  :class="{ 'border-red-500': profileFormErrors.full_name }"
                />
                <p v-if="profileFormErrors.full_name" class="mt-1 text-sm text-red-600">{{ profileFormErrors.full_name }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  {{ t('account.settings.email') }}
                </label>
                <input
                  :value="userEmail"
                  type="email"
                  disabled
                  class="w-full px-4 py-2 border rounded-lg bg-slate-100 dark:bg-slate-600 dark:border-slate-500 dark:text-slate-300 cursor-not-allowed"
                />
                <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ t('account.settings.emailHint') }}</p>
              </div>

              <p v-if="profileError" class="text-sm text-red-600">{{ profileError }}</p>
              <p v-if="profileSuccess" class="text-sm text-green-600">{{ profileSuccess }}</p>

              <div class="flex gap-3 pt-2">
                <button
                  type="button"
                  @click="showEditProfileModal = false"
                  class="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                >
                  {{ t('account.settings.cancel') }}
                </button>
                <button
                  type="submit"
                  :disabled="isUpdatingProfile"
                  class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {{ isUpdatingProfile ? t('account.settings.saving') : t('account.settings.saveChanges') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style>
/* Transition styles for modals - not scoped because of Teleport */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
