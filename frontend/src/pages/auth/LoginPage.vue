<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '@/composables/useAuth'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const { handleLoginSuccess, initializeGoogle, loadGoogleScript, isAuthenticated, checkSession } = useAuth()

// Redirect if already logged in
onMounted(async () => {
  // Check session first if there's a token
  const hasToken = !!localStorage.getItem('access_token')
  if (hasToken && !isAuthenticated.value) {
    await checkSession()
  }

  // Now check if authenticated and redirect
  if (isAuthenticated.value) {
    const redirect = route.query.redirect as string
    await router.push(redirect || '/organization')
  }
})

// Form state
const email = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')
const showForgotPassword = ref(false)
const forgotPasswordEmail = ref('')
const forgotPasswordLoading = ref(false)
const forgotPasswordSuccess = ref(false)

// Redirect URL for after login
const redirectUrl = computed(() => route.query.redirect as string || '/organization')

// Handle email/password login
const handleSubmit = async () => {
  error.value = ''

  if (!email.value || !password.value) {
    error.value = t('auth.errors.fillAllFields')
    return
  }

  isLoading.value = true

  try {
    const { authApi } = await import('@/api/v1/auth')
    const response = await authApi.login({
      email: email.value,
      password: password.value,
    })
    handleLoginSuccess(response)
    await router.push(redirectUrl.value)
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e?.response?.data?.detail || t('auth.errors.loginFailed')
  } finally {
    isLoading.value = false
  }
}

// Handle Google login
const handleGoogleCallback = async (response: { credential: string }) => {
  error.value = ''
  isLoading.value = true

  try {
    const { authApi } = await import('@/api/v1/auth')
    const authResponse = await authApi.googleAuth({
      credential: response.credential,
      is_registration: false,
    })
    handleLoginSuccess(authResponse)
    await router.push(redirectUrl.value)
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e?.response?.data?.detail || t('auth.errors.googleLoginFailed')
  } finally {
    isLoading.value = false
  }
}

// Handle forgot password
const handleForgotPassword = async () => {
  if (!forgotPasswordEmail.value) {
    error.value = t('auth.errors.fillAllFields')
    return
  }

  forgotPasswordLoading.value = true
  error.value = ''

  try {
    const { authApi } = await import('@/api/v1/auth')
    await authApi.forgotPassword({ email: forgotPasswordEmail.value })
    forgotPasswordSuccess.value = true
  } catch {
    error.value = t('auth.errors.forgotPasswordFailed')
  } finally {
    forgotPasswordLoading.value = false
  }
}

// Initialize Google Sign-In
onMounted(async () => {
  await loadGoogleScript()
  initializeGoogle('google-login-btn', handleGoogleCallback)
})
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Forgot Password View -->
      <div v-if="showForgotPassword" class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
        <button
          @click="showForgotPassword = false; forgotPasswordSuccess = false; error = ''"
          class="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 mb-4 flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ t('auth.backToLogin') }}
        </button>

        <div v-if="forgotPasswordSuccess" class="text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">
            {{ t('auth.forgotPasswordSuccess') }}
          </h2>
        </div>

        <div v-else>
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            {{ t('auth.forgotPassword') }}
          </h2>
          <p class="text-slate-600 dark:text-slate-400 mb-6">
            {{ t('auth.forgotPasswordSubtitle') }}
          </p>

          <form @submit.prevent="handleForgotPassword" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                {{ t('auth.email') }}
              </label>
              <input
                v-model="forgotPasswordEmail"
                type="email"
                :placeholder="t('auth.emailPlaceholder')"
                class="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-slate-700 dark:text-white"
              />
            </div>

            <div v-if="error" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p class="text-sm text-red-700 dark:text-red-300">{{ error }}</p>
            </div>

            <button
              type="submit"
              :disabled="forgotPasswordLoading"
              class="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ forgotPasswordLoading ? t('auth.loading') : t('auth.sendResetLink') }}
            </button>
          </form>
        </div>
      </div>

      <!-- Login Form -->
      <div v-else class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
        <div class="text-center mb-8">
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white">
            {{ t('auth.login.title') }}
          </h1>
          <p class="text-slate-600 dark:text-slate-400 mt-2">
            {{ t('auth.login.subtitle') }}
          </p>
        </div>

        <!-- Google Sign-In Button -->
        <div id="google-login-btn" class="flex justify-center mb-6"></div>

        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-slate-300 dark:border-slate-600"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white dark:bg-slate-800 text-slate-500">
              {{ t('auth.or') }}
            </span>
          </div>
        </div>

        <!-- Email/Password Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('auth.email') }}
            </label>
            <input
              v-model="email"
              type="email"
              :placeholder="t('auth.emailPlaceholder')"
              class="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-slate-700 dark:text-white"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('auth.password') }}
            </label>
            <input
              v-model="password"
              type="password"
              :placeholder="t('auth.passwordPlaceholder')"
              class="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-slate-700 dark:text-white"
            />
          </div>

          <div class="flex justify-end">
            <button
              type="button"
              @click="showForgotPassword = true; error = ''"
              class="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
            >
              {{ t('auth.forgotPassword') }}
            </button>
          </div>

          <div v-if="error" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p class="text-sm text-red-700 dark:text-red-300">{{ error }}</p>
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ isLoading ? t('auth.loading') : t('auth.login.button') }}
          </button>
        </form>

        <!-- Register Link -->
        <p class="text-center mt-6 text-slate-600 dark:text-slate-400">
          {{ t('auth.login.noAccount') }}
          <router-link
            :to="{ path: '/register', query: route.query }"
            class="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
          >
            {{ t('auth.login.registerLink') }}
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>
