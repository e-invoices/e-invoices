<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed, ref, onMounted, watch } from 'vue'
import LoginModal from '@/components/auth/LoginModal.vue'
import RegisterModal from '@/components/auth/RegisterModal.vue'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/composables/useTheme'
import type { User } from '@/types/auth'

const { t, locale } = useI18n()
const { isDark, toggleTheme } = useTheme()
const {
  showLoginModal,
  showRegisterModal,
  currentUser,
  isAuthenticated,
  isGoogleLoaded,
  openLogin,
  openRegister,
  closeModals,
  switchToRegister,
  switchToLogin,
  handleLoginSuccess,
  handleRegisterSuccess,
  logout,
  initializeGoogle,
  loadGoogleScript,
  checkSession,
} = useAuth()

// Type assertion for template usage
const user = computed(() => currentUser.value as User | null)

const mobileMenuOpen = ref(false)
const loginModalRef = ref<InstanceType<typeof LoginModal> | null>(null)
const registerModalRef = ref<InstanceType<typeof RegisterModal> | null>(null)

const menuItems = computed(() => [
  { label: t('nav.howItWorks'), path: '/how-it-works' },
  { label: t('nav.benefits'), path: '/benefits' },
  { label: t('nav.pricing'), path: '/pricing' },
])

const toggleLanguage = () => {
  locale.value = locale.value === 'mk' ? 'en' : 'mk'
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const handleMobileLogin = () => {
  closeMobileMenu()
  openLogin()
}

const handleMobileRegister = () => {
  closeMobileMenu()
  openRegister()
}

const handleMobileLogout = () => {
  closeMobileMenu()
  logout()
}

// Initialize Google Sign-In when modals open
watch(showLoginModal, async (isOpen) => {
  if (isOpen && isGoogleLoaded.value) {
    // Wait for DOM to update
    await new Promise(resolve => setTimeout(resolve, 100))
    initializeGoogle('google-login-button', (response) => {
      loginModalRef.value?.handleGoogleLogin(response)
    })
  }
})

watch(showRegisterModal, async (isOpen) => {
  if (isOpen && isGoogleLoaded.value) {
    await new Promise(resolve => setTimeout(resolve, 100))
    initializeGoogle('google-register-button', (response) => {
      registerModalRef.value?.handleGoogleRegister(response)
    })
  }
})

onMounted(async () => {
  await loadGoogleScript()
  await checkSession()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 font-sans text-slate-800 dark:text-slate-200">
    <!-- Header -->
    <header class="bg-white dark:bg-slate-900 shadow-sm dark:shadow-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16 md:h-20">
          <!-- Logo -->
          <div class="flex-shrink-0 w-28 md:w-32">
            <RouterLink to="/" class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white no-underline">
              e-Faktura
            </RouterLink>
          </div>

          <!-- Desktop Navigation -->
          <nav class="hidden md:flex items-center gap-6 lg:gap-8">
            <RouterLink
              v-for="item in menuItems"
              :key="item.path"
              :to="item.path"
              class="min-w-[100px] text-center text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white font-medium transition-colors duration-200 no-underline whitespace-nowrap"
            >
              {{ item.label }}
            </RouterLink>
          </nav>

          <!-- Desktop Right Section -->
          <div class="hidden md:flex items-center gap-4 lg:gap-6">
            <!-- Theme Toggle -->
            <button
              @click="toggleTheme"
              class="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors duration-200 bg-transparent border-none cursor-pointer"
              :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
            >
              <!-- Sun icon (shown in dark mode) -->
              <svg v-if="isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <!-- Moon icon (shown in light mode) -->
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            </button>

            <!-- Language Toggle -->
            <button
              @click="toggleLanguage"
              class="w-10 px-3 py-2 font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors duration-200 bg-transparent border-none cursor-pointer"
            >
              {{ locale === 'mk' ? 'EN' : 'MK' }}
            </button>

            <!-- Auth buttons when not logged in -->
            <div v-if="!isAuthenticated" class="flex items-center gap-3">
              <button
                @click="openLogin"
                class="min-w-[110px] text-center px-4 lg:px-6 py-2 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white font-semibold rounded-full hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600 transition-all duration-200 bg-transparent cursor-pointer text-sm whitespace-nowrap"
              >
                {{ t('nav.login') }}
              </button>
              <button
                @click="openRegister"
                class="min-w-[130px] text-center px-4 lg:px-6 py-2 bg-blue-500 text-white font-semibold rounded-full hover:bg-blue-600 transition-all duration-200 border-none cursor-pointer text-sm whitespace-nowrap"
              >
                {{ t('nav.register') }}
              </button>
            </div>

            <!-- User menu when logged in -->
            <div v-else class="flex items-center gap-3">
              <span class="text-sm text-slate-600 dark:text-slate-400">{{ user?.full_name || user?.email }}</span>
              <button
                @click="logout"
                class="px-4 py-2 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white font-semibold rounded-full hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600 transition-all duration-200 bg-transparent cursor-pointer text-sm"
              >
                {{ t('nav.logout') }}
              </button>
            </div>
          </div>

          <!-- Mobile Menu Button -->
          <button
            @click="toggleMobileMenu"
            class="md:hidden p-2 rounded-md text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors duration-200 bg-transparent border-none cursor-pointer"
          >
            <svg v-if="!mobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Mobile Menu -->
        <div
          v-show="mobileMenuOpen"
          class="md:hidden border-t border-slate-100 dark:border-slate-800 py-4"
        >
          <nav class="flex flex-col gap-2">
            <RouterLink
              v-for="item in menuItems"
              :key="item.path"
              :to="item.path"
              class="px-3 py-2 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg font-medium transition-colors duration-200 no-underline"
              @click="mobileMenuOpen = false"
            >
              {{ item.label }}
            </RouterLink>
          </nav>
          <div class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-col gap-3">
            <!-- Theme Toggle for Mobile -->
            <button
              @click="toggleTheme"
              class="flex items-center gap-2 px-3 py-2 text-left font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors duration-200 bg-transparent border-none cursor-pointer"
            >
              <svg v-if="isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
              {{ isDark ? t('theme.light') : t('theme.dark') }}
            </button>

            <!-- Language Toggle -->
            <button
              @click="toggleLanguage"
              class="px-3 py-2 text-left font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors duration-200 bg-transparent border-none cursor-pointer"
            >
              {{ locale === 'mk' ? 'Switch to English' : 'Премини на Македонски' }}
            </button>

            <!-- Mobile auth buttons -->
            <div v-if="!isAuthenticated" class="flex flex-col gap-2 px-3">
              <button
                @click="handleMobileLogin"
                class="w-full text-center px-4 py-2 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white font-semibold rounded-full hover:bg-slate-50 dark:hover:bg-slate-800 transition-all duration-200 bg-transparent cursor-pointer text-sm"
              >
                {{ t('nav.login') }}
              </button>
              <button
                @click="handleMobileRegister"
                class="w-full text-center px-4 py-2 bg-blue-500 text-white font-semibold rounded-full hover:bg-blue-600 transition-all duration-200 border-none cursor-pointer text-sm"
              >
                {{ t('nav.register') }}
              </button>
            </div>

            <!-- Mobile user menu -->
            <div v-else class="flex flex-col gap-2 px-3">
              <span class="text-sm text-slate-600 dark:text-slate-400 py-2">{{ user?.full_name || user?.email }}</span>
              <button
                @click="handleMobileLogout"
                class="w-full text-center px-4 py-2 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white font-semibold rounded-full hover:bg-slate-50 dark:hover:bg-slate-800 transition-all duration-200 bg-transparent cursor-pointer text-sm"
              >
                {{ t('nav.logout') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main>
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 mt-12 md:mt-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8 text-center">
        <p class="text-slate-500 dark:text-slate-400 text-sm md:text-base">{{ t('footer.rights') }}</p>
      </div>
    </footer>

    <!-- Auth Modals -->
    <LoginModal
      ref="loginModalRef"
      :is-open="showLoginModal"
      @close="closeModals"
      @switch-to-register="switchToRegister"
      @login-success="handleLoginSuccess"
    />

    <RegisterModal
      ref="registerModalRef"
      :is-open="showRegisterModal"
      @close="closeModals"
      @switch-to-login="switchToLogin"
      @register-success="handleRegisterSuccess"
    />
  </div>
</template>
