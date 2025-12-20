<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '@/composables/useAuth'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
 const { handleRegisterSuccess, initializeGoogle, loadGoogleScript, isAuthenticated, checkSession } = useAuth()

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
const fullName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptTerms = ref(false)
const isLoading = ref(false)
const error = ref('')

// Redirect URL for after registration
const redirectUrl = computed(() => route.query.redirect as string || '/organization')

// Validate form
const validateForm = () => {
  if (!fullName.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = t('auth.errors.fillAllFields')
    return false
  }

  if (password.value.length < 8) {
    error.value = t('auth.errors.passwordTooShort')
    return false
  }

  if (password.value !== confirmPassword.value) {
    error.value = t('auth.errors.passwordMismatch')
    return false
  }

  if (!acceptTerms.value) {
    error.value = t('auth.errors.acceptTerms')
    return false
  }

  return true
}

// Handle email/password registration
const handleSubmit = async () => {
  error.value = ''

  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    const { authApi } = await import('@/api/v1/auth')
    const response = await authApi.register({
      name: fullName.value,
      email: email.value,
      password: password.value,
    })
    handleRegisterSuccess(response)
    await router.push(redirectUrl.value)
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e?.response?.data?.detail || t('auth.errors.registerFailed')
  } finally {
    isLoading.value = false
  }
}

// Handle Google registration
const handleGoogleCallback = async (response: { credential: string }) => {
  error.value = ''
  isLoading.value = true

  try {
    const { authApi } = await import('@/api/v1/auth')
    const authResponse = await authApi.googleAuth({
      credential: response.credential,
      is_registration: true,
    })
    handleRegisterSuccess(authResponse)
    await router.push(redirectUrl.value)
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e?.response?.data?.detail || t('auth.errors.googleRegisterFailed')
  } finally {
    isLoading.value = false
  }
}

// Initialize Google Sign-In
onMounted(async () => {
  await loadGoogleScript()
  initializeGoogle('google-register-btn', handleGoogleCallback)
})
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
        <div class="text-center mb-8">
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white">
            {{ t('auth.register.title') }}
          </h1>
          <p class="text-slate-600 dark:text-slate-400 mt-2">
            {{ t('auth.register.subtitle') }}
          </p>
        </div>

        <!-- Google Sign-Up Button -->
        <div id="google-register-btn" class="flex justify-center mb-6"></div>

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

        <!-- Registration Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('auth.fullName') }}
            </label>
            <input
              v-model="fullName"
              type="text"
              :placeholder="t('auth.fullNamePlaceholder')"
              class="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-slate-700 dark:text-white"
            />
          </div>

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

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('auth.confirmPassword') }}
            </label>
            <input
              v-model="confirmPassword"
              type="password"
              :placeholder="t('auth.confirmPasswordPlaceholder')"
              class="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-slate-700 dark:text-white"
            />
          </div>

          <div class="flex items-start gap-3">
            <input
              v-model="acceptTerms"
              type="checkbox"
              id="terms"
              class="mt-1 w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-blue-600 focus:ring-blue-500"
            />
            <label for="terms" class="text-sm text-slate-600 dark:text-slate-400">
              {{ t('auth.register.acceptTerms') }}
              <a href="#" class="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                {{ t('auth.register.termsLink') }}
              </a>
            </label>
          </div>

          <div v-if="error" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p class="text-sm text-red-700 dark:text-red-300">{{ error }}</p>
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ isLoading ? t('auth.loading') : t('auth.register.button') }}
          </button>
        </form>

        <!-- Login Link -->
        <p class="text-center mt-6 text-slate-600 dark:text-slate-400">
          {{ t('auth.register.hasAccount') }}
          <router-link
            :to="{ path: '/login', query: route.query }"
            class="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
          >
            {{ t('auth.register.loginLink') }}
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>
