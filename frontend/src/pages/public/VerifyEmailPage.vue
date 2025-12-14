<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Loading State -->
      <div v-if="isLoading" class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
        <p class="mt-4 text-gray-600">{{ t('verifyEmail.verifying') }}</p>
      </div>

      <!-- Success State -->
      <div v-else-if="isSuccess" class="text-center">
        <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
          <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        </div>
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">{{ t('verifyEmail.successTitle') }}</h2>
        <p class="mt-2 text-sm text-gray-600">{{ t('verifyEmail.successMessage') }}</p>
        <div class="mt-6">
          <button
            @click="goToLogin"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {{ t('verifyEmail.loginButton') }}
          </button>
        </div>
      </div>

      <!-- Error State -->
      <div v-else class="text-center">
        <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100">
          <svg class="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </div>
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">{{ t('verifyEmail.errorTitle') }}</h2>
        <p class="mt-2 text-sm text-gray-600">{{ errorMessage }}</p>
        <div class="mt-6">
          <button
            @click="goToHome"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {{ t('verifyEmail.homeButton') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authApi } from '@/api/v1/auth'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const isLoading = ref(true)
const isSuccess = ref(false)
const errorMessage = ref('')

onMounted(async () => {
  const token = route.query.token as string

  if (!token) {
    isLoading.value = false
    errorMessage.value = t('verifyEmail.noToken')
    return
  }

  try {
    await authApi.verifyEmail(token)
    isSuccess.value = true
  } catch (error: unknown) {
    const axiosError = error as { response?: { data?: { detail?: string } } }
    errorMessage.value = axiosError.response?.data?.detail || t('verifyEmail.genericError')
  } finally {
    isLoading.value = false
  }
})

const goToLogin = () => {
  router.push({ name: 'landing' })
}

const goToHome = () => {
  router.push({ name: 'landing' })
}
</script>

