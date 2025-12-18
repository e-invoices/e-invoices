<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { authApi } from '@/api/v1/auth'


const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const token = ref('')
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const isSuccess = ref(false)
const error = ref('')
const formErrors = ref<{ password?: string; confirmPassword?: string }>({})

onMounted(() => {
  token.value = (route.query.token as string) || ''
  if (!token.value) {
    error.value = t('resetPassword.noToken')
  }
})

const validateForm = () => {
  formErrors.value = {}

  if (!password.value) {
    formErrors.value.password = t('resetPassword.errors.passwordRequired')
  } else if (password.value.length < 8) {
    formErrors.value.password = t('resetPassword.errors.passwordTooShort')
  }

  if (!confirmPassword.value) {
    formErrors.value.confirmPassword = t('resetPassword.errors.confirmPasswordRequired')
  } else if (password.value !== confirmPassword.value) {
    formErrors.value.confirmPassword = t('resetPassword.errors.passwordMismatch')
  }

  return Object.keys(formErrors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return

  isLoading.value = true
  error.value = ''

  try {
    await authApi.resetPassword({
      token: token.value,
      password: password.value,
      confirm_password: confirmPassword.value
    })
    isSuccess.value = true
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e?.response?.data?.detail || t('resetPassword.errors.resetFailed')
  } finally {
    isLoading.value = false
  }
}

const goToLogin = () => {
  router.push('/')
}
</script>

<template>
  <div class="flex-1 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
        <!-- Success State -->
        <div v-if="isSuccess" class="bg-white dark:bg-slate-800 rounded-2xl shadow-lg p-8 text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            {{ t('resetPassword.successTitle') }}
          </h1>
          <p class="text-slate-600 dark:text-slate-400 mb-6">
            {{ t('resetPassword.successMessage') }}
          </p>
          <button
            @click="goToLogin"
            class="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            {{ t('resetPassword.loginButton') }}
          </button>
        </div>

        <!-- Error State (no token) -->
        <div v-else-if="!token && error" class="bg-white dark:bg-slate-800 rounded-2xl shadow-lg p-8 text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <svg class="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            {{ t('resetPassword.errorTitle') }}
          </h1>
          <p class="text-slate-600 dark:text-slate-400 mb-6">
            {{ error }}
          </p>
          <button
            @click="goToLogin"
            class="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            {{ t('resetPassword.homeButton') }}
          </button>
        </div>

        <!-- Reset Form -->
        <div v-else class="bg-white dark:bg-slate-800 rounded-2xl shadow-lg p-8">
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2 text-center">
            {{ t('resetPassword.title') }}
          </h1>
          <p class="text-slate-600 dark:text-slate-400 mb-6 text-center">
            {{ t('resetPassword.subtitle') }}
          </p>

          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                {{ t('resetPassword.newPassword') }}
              </label>
              <input
                v-model="password"
                type="password"
                :placeholder="t('resetPassword.newPasswordPlaceholder')"
                class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                :class="{ 'border-red-500': formErrors.password }"
              />
              <p v-if="formErrors.password" class="mt-1 text-sm text-red-600">{{ formErrors.password }}</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                {{ t('resetPassword.confirmPassword') }}
              </label>
              <input
                v-model="confirmPassword"
                type="password"
                :placeholder="t('resetPassword.confirmPasswordPlaceholder')"
                class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-slate-700 dark:border-slate-600 dark:text-white"
                :class="{ 'border-red-500': formErrors.confirmPassword }"
              />
              <p v-if="formErrors.confirmPassword" class="mt-1 text-sm text-red-600">{{ formErrors.confirmPassword }}</p>
            </div>

            <div v-if="error" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p class="text-sm text-red-700 dark:text-red-300">{{ error }}</p>
            </div>

            <button
              type="submit"
              :disabled="isLoading"
              class="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ isLoading ? t('common.loading') : t('resetPassword.submitButton') }}
            </button>
          </form>
      </div>
    </div>
  </div>
</template>
