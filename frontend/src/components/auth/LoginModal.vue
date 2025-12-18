<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { GoogleCredentialResponse, AuthResponse } from '@/types/auth'
import { authApi } from '@/api/v1/auth'
import { useAuth } from '@/composables/useAuth'

const { t } = useI18n()
const { isGoogleLoaded } = useAuth()

defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  close: []
  switchToRegister: []
  loginSuccess: [response: AuthResponse]
}>()

const email = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

// Forgot password state
const showForgotPassword = ref(false)
const forgotPasswordEmail = ref('')
const forgotPasswordLoading = ref(false)
const forgotPasswordSuccess = ref(false)
const forgotPasswordError = ref('')

const handleEmailLogin = async () => {
  if (!email.value || !password.value) {
    error.value = t('auth.errors.fillAllFields')
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const data = await authApi.login({ email: email.value, password: password.value })
    emit('loginSuccess', data)
    emit('close')
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('auth.errors.invalidCredentials')
  } finally {
    isLoading.value = false
  }
}

const handleGoogleLogin = async (response: GoogleCredentialResponse) => {
  isLoading.value = true
  error.value = ''

  try {
    const data = await authApi.googleAuth({ credential: response.credential })
    emit('loginSuccess', data)
    emit('close')
  } catch {
    error.value = t('auth.errors.googleLoginFailed')
  } finally {
    isLoading.value = false
  }
}

const handleGoogleError = () => {
  error.value = t('auth.errors.googleLoginFailed')
}

const openForgotPassword = () => {
  showForgotPassword.value = true
  forgotPasswordEmail.value = email.value // Pre-fill with login email if entered
  forgotPasswordError.value = ''
  forgotPasswordSuccess.value = false
}

const closeForgotPassword = () => {
  showForgotPassword.value = false
  forgotPasswordError.value = ''
  forgotPasswordSuccess.value = false
}

const handleForgotPassword = async () => {
  if (!forgotPasswordEmail.value) {
    forgotPasswordError.value = t('auth.errors.fillAllFields')
    return
  }

  forgotPasswordLoading.value = true
  forgotPasswordError.value = ''

  try {
    await authApi.forgotPassword({ email: forgotPasswordEmail.value })
    forgotPasswordSuccess.value = true
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    forgotPasswordError.value = e?.response?.data?.detail || t('auth.errors.forgotPasswordFailed')
  } finally {
    forgotPasswordLoading.value = false
  }
}

// Expose for Google callback
defineExpose({ handleGoogleLogin, handleGoogleError })
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="emit('close')"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="emit('close')"></div>

        <!-- Modal -->
        <div class="relative w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl p-6 md:p-8 transform transition-all">
          <!-- Close Button -->
          <button
            @click="emit('close')"
            class="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors bg-transparent border-none cursor-pointer"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <!-- Forgot Password View -->
          <div v-if="showForgotPassword">
            <!-- Back Button -->
            <button
              @click="closeForgotPassword"
              class="flex items-center gap-1 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 mb-4 bg-transparent border-none cursor-pointer"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              {{ t('common.back') }}
            </button>

            <!-- Header -->
            <div class="text-center mb-6">
              <h2 class="text-2xl font-bold text-slate-900 dark:text-white">{{ t('auth.forgotPassword') }}</h2>
              <p class="mt-2 text-slate-500 dark:text-slate-400">{{ t('auth.forgotPasswordSubtitle') }}</p>
            </div>

            <!-- Success Message -->
            <div v-if="forgotPasswordSuccess" class="mb-4 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg">
              <div class="flex items-center gap-3">
                <svg class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <p class="text-green-700 dark:text-green-300 text-sm">{{ t('auth.forgotPasswordSuccess') }}</p>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="forgotPasswordError" class="mb-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
              {{ forgotPasswordError }}
            </div>

            <!-- Forgot Password Form -->
            <form v-if="!forgotPasswordSuccess" @submit.prevent="handleForgotPassword" class="space-y-4">
              <div>
                <label for="forgot-email" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  {{ t('auth.email') }}
                </label>
                <input
                  id="forgot-email"
                  v-model="forgotPasswordEmail"
                  type="email"
                  autocomplete="email"
                  class="w-full px-4 py-3 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                  :placeholder="t('auth.emailPlaceholder')"
                />
              </div>

              <button
                type="submit"
                :disabled="forgotPasswordLoading"
                class="w-full py-3 px-4 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                <span v-if="forgotPasswordLoading">{{ t('auth.loading') }}</span>
                <span v-else>{{ t('auth.sendResetLink') }}</span>
              </button>
            </form>

            <!-- Back to Login after success -->
            <button
              v-if="forgotPasswordSuccess"
              @click="closeForgotPassword"
              class="w-full py-3 px-4 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 transition-all"
            >
              {{ t('auth.backToLogin') }}
            </button>
          </div>

          <!-- Login View -->
          <div v-else>
            <!-- Header -->
            <div class="text-center mb-6">
              <h2 class="text-2xl font-bold text-slate-900 dark:text-white">{{ t('auth.login.title') }}</h2>
              <p class="mt-2 text-slate-500 dark:text-slate-400">{{ t('auth.login.subtitle') }}</p>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="mb-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
              {{ error }}
            </div>

            <!-- Google Sign In Button -->
            <div class="mb-6">
              <!-- Google SDK Button (rendered by Google) -->
              <div v-show="isGoogleLoaded" id="google-login-button" class="flex justify-center"></div>

              <!-- Fallback button when SDK fails to load -->
              <div v-if="!isGoogleLoaded" class="flex justify-center">
                <button
                  type="button"
                  disabled
                  class="flex items-center justify-center gap-3 w-full max-w-[320px] px-4 py-3 border border-slate-300 rounded-lg bg-slate-100 text-slate-400 cursor-not-allowed"
                >
                  <svg class="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#9CA3AF" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#9CA3AF" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#9CA3AF" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#9CA3AF" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  <span class="text-sm font-medium">Google не е достапно</span>
                </button>
              </div>
            </div>

            <!-- Divider -->
            <div class="relative mb-6">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-slate-200 dark:border-slate-700"></div>
              </div>
              <div class="relative flex justify-center text-sm">
                <span class="px-4 bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400">{{ t('auth.or') }}</span>
              </div>
            </div>

            <!-- Email/Password Form -->
            <form @submit.prevent="handleEmailLogin" class="space-y-4">
              <div>
                <label for="login-email" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  {{ t('auth.email') }}
                </label>
                <input
                  id="login-email"
                  v-model="email"
                  type="email"
                  autocomplete="email"
                  class="w-full px-4 py-3 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                  :placeholder="t('auth.emailPlaceholder')"
                />
              </div>

              <div>
                <label for="login-password" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  {{ t('auth.password') }}
                </label>
                <input
                  id="login-password"
                  v-model="password"
                  type="password"
                  autocomplete="current-password"
                  class="w-full px-4 py-3 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                  :placeholder="t('auth.passwordPlaceholder')"
                />
              </div>

              <div class="flex items-center justify-end">
                <button
                  type="button"
                  @click="openForgotPassword"
                  class="text-sm text-blue-500 hover:text-blue-600 bg-transparent border-none cursor-pointer"
                >
                  {{ t('auth.forgotPassword') }}
                </button>
              </div>

              <button
                type="submit"
                :disabled="isLoading"
                class="w-full py-3 px-4 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                <span v-if="isLoading">{{ t('auth.loading') }}</span>
                <span v-else>{{ t('auth.login.button') }}</span>
              </button>
            </form>

            <!-- Switch to Register -->
            <p class="mt-6 text-center text-slate-500 dark:text-slate-400 text-sm">
              {{ t('auth.login.noAccount') }}
              <button
                @click="emit('switchToRegister')"
                class="text-blue-500 hover:text-blue-600 font-semibold bg-transparent border-none cursor-pointer"
              >
                {{ t('auth.login.registerLink') }}
              </button>
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>

</style>
