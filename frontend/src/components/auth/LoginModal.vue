<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { GoogleCredentialResponse, AuthResponse } from '@/types/auth'
import { authApi } from '@/api/v1/auth'

const { t } = useI18n()


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
        <div class="relative w-full max-w-md bg-white rounded-2xl shadow-2xl p-6 md:p-8 transform transition-all">
          <!-- Close Button -->
          <button
            @click="emit('close')"
            class="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 transition-colors bg-transparent border-none cursor-pointer"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <!-- Header -->
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-slate-900">{{ t('auth.login.title') }}</h2>
            <p class="mt-2 text-slate-500">{{ t('auth.login.subtitle') }}</p>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            {{ error }}
          </div>

          <!-- Google Sign In Button -->
          <div class="mb-6">
            <div id="google-login-button" class="flex justify-center"></div>
          </div>

          <!-- Divider -->
          <div class="relative mb-6">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-slate-200"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-4 bg-white text-slate-500">{{ t('auth.or') }}</span>
            </div>
          </div>

          <!-- Email/Password Form -->
          <form @submit.prevent="handleEmailLogin" class="space-y-4">
            <div>
              <label for="login-email" class="block text-sm font-medium text-slate-700 mb-1">
                {{ t('auth.email') }}
              </label>
              <input
                id="login-email"
                v-model="email"
                type="email"
                autocomplete="email"
                class="w-full px-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                :placeholder="t('auth.emailPlaceholder')"
              />
            </div>

            <div>
              <label for="login-password" class="block text-sm font-medium text-slate-700 mb-1">
                {{ t('auth.password') }}
              </label>
              <input
                id="login-password"
                v-model="password"
                type="password"
                autocomplete="current-password"
                class="w-full px-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                :placeholder="t('auth.passwordPlaceholder')"
              />
            </div>

            <div class="flex items-center justify-end">
              <a href="#" class="text-sm text-blue-500 hover:text-blue-600 no-underline">
                {{ t('auth.forgotPassword') }}
              </a>
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
          <p class="mt-6 text-center text-slate-500 text-sm">
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
    </Transition>
  </Teleport>
</template>

<style scoped>

</style>

