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
  switchToLogin: []
  registerSuccess: [response: AuthResponse]
}>()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptTerms = ref(false)
const isLoading = ref(false)
const error = ref('')

const handleEmailRegister = async () => {
  // Validation
  if (!name.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = t('auth.errors.fillAllFields')
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = t('auth.errors.passwordMismatch')
    return
  }

  if (password.value.length < 8) {
    error.value = t('auth.errors.passwordTooShort')
    return
  }

  if (!acceptTerms.value) {
    error.value = t('auth.errors.acceptTerms')
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const data = await authApi.register({
      name: name.value,
      email: email.value,
      password: password.value
    })
    emit('registerSuccess', data)
    emit('close')
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('auth.errors.registerFailed')
  } finally {
    isLoading.value = false
  }
}

const handleGoogleRegister = async (response: GoogleCredentialResponse) => {
  isLoading.value = true
  error.value = ''

  try {
    const data = await authApi.googleAuth({
      credential: response.credential,
      is_registration: true
    })
    emit('registerSuccess', data)
    emit('close')
  } catch {
    error.value = t('auth.errors.googleRegisterFailed')
  } finally {
    isLoading.value = false
  }
}

const handleGoogleError = () => {
  error.value = t('auth.errors.googleRegisterFailed')
}

// Expose for Google callback
defineExpose({ handleGoogleRegister, handleGoogleError })
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
        <div class="relative w-full max-w-md bg-white rounded-2xl shadow-2xl p-6 md:p-8 transform transition-all max-h-[90vh] overflow-y-auto">
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
            <h2 class="text-2xl font-bold text-slate-900">{{ t('auth.register.title') }}</h2>
            <p class="mt-2 text-slate-500">{{ t('auth.register.subtitle') }}</p>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            {{ error }}
          </div>

          <!-- Google Sign Up Button -->
          <div class="mb-6">
            <div id="google-register-button" class="flex justify-center"></div>
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

          <!-- Registration Form -->
          <form @submit.prevent="handleEmailRegister" class="space-y-4">
            <div>
              <label for="register-name" class="block text-sm font-medium text-slate-700 mb-1">
                {{ t('auth.fullName') }}
              </label>
              <input
                id="register-name"
                v-model="name"
                type="text"
                autocomplete="name"
                class="w-full px-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                :placeholder="t('auth.fullNamePlaceholder')"
              />
            </div>

            <div>
              <label for="register-email" class="block text-sm font-medium text-slate-700 mb-1">
                {{ t('auth.email') }}
              </label>
              <input
                id="register-email"
                v-model="email"
                type="email"
                autocomplete="email"
                class="w-full px-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                :placeholder="t('auth.emailPlaceholder')"
              />
            </div>

            <div>
              <label for="register-password" class="block text-sm font-medium text-slate-700 mb-1">
                {{ t('auth.password') }}
              </label>
              <input
                id="register-password"
                v-model="password"
                type="password"
                autocomplete="new-password"
                class="w-full px-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                :placeholder="t('auth.passwordPlaceholder')"
              />
            </div>

            <div>
              <label for="register-confirm-password" class="block text-sm font-medium text-slate-700 mb-1">
                {{ t('auth.confirmPassword') }}
              </label>
              <input
                id="register-confirm-password"
                v-model="confirmPassword"
                type="password"
                autocomplete="new-password"
                class="w-full px-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                :placeholder="t('auth.confirmPasswordPlaceholder')"
              />
            </div>

            <div class="flex items-start gap-2">
              <input
                id="accept-terms"
                v-model="acceptTerms"
                type="checkbox"
                class="mt-1 w-4 h-4 text-blue-500 border-slate-300 rounded focus:ring-blue-500"
              />
              <label for="accept-terms" class="text-sm text-slate-600">
                {{ t('auth.register.acceptTerms') }}
                <a href="/terms" class="text-blue-500 hover:text-blue-600 no-underline">
                  {{ t('auth.register.termsLink') }}
                </a>
              </label>
            </div>

            <button
              type="submit"
              :disabled="isLoading"
              class="w-full py-3 px-4 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <span v-if="isLoading">{{ t('auth.loading') }}</span>
              <span v-else>{{ t('auth.register.button') }}</span>
            </button>
          </form>

          <!-- Switch to Login -->
          <p class="mt-6 text-center text-slate-500 text-sm">
            {{ t('auth.register.hasAccount') }}
            <button
              @click="emit('switchToLogin')"
              class="text-blue-500 hover:text-blue-600 font-semibold bg-transparent border-none cursor-pointer"
            >
              {{ t('auth.register.loginLink') }}
            </button>
          </p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
