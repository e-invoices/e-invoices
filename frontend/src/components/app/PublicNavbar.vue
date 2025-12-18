<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed, ref, onMounted, watch } from 'vue'
import LoginModal from '@/components/auth/LoginModal.vue'
import RegisterModal from '@/components/auth/RegisterModal.vue'
import LanguageFlag from '@/components/ui/LanguageFlag.vue'
import ProfileDropdown from '@/components/app/ProfileDropdown.vue'
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

// Language dropdown
const languageDropdownOpen = ref(false)

interface LangOption {
  code: string
  name: string
}

const languages: LangOption[] = [
  { code: 'mk', name: 'Македонски' },
  { code: 'en', name: 'English' },
  { code: 'sq', name: 'Shqip' },
]

const currentLanguage = computed((): LangOption => {
  return languages.find(lang => lang.code === locale.value) || languages[0]!
})

const setLanguage = (code: string) => {
  locale.value = code
  languageDropdownOpen.value = false
}

const toggleLanguageDropdown = () => {
  languageDropdownOpen.value = !languageDropdownOpen.value
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

// Get initials for mobile menu avatar
const getMobileInitials = () => {
  if (!user.value) return '?'

  const name = user.value.full_name || user.value.name || user.value.email
  if (!name) return '?'

  const parts = name.trim().split(/\s+/)
  const firstPart = parts[0]
  const lastPart = parts[parts.length - 1]

  if (parts.length >= 2 && firstPart && lastPart && firstPart[0] && lastPart[0]) {
    return (firstPart[0] + lastPart[0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

// Close language dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.language-dropdown')) {
    languageDropdownOpen.value = false
  }
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
  document.addEventListener('click', handleClickOutside)
})
</script>

<template>
  <!-- Header -->
  <header class="bg-white dark:bg-slate-900 shadow-sm dark:shadow-slate-800">
    <div class="w-full px-4 sm:px-6 lg:px-8">
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

          <!-- Language Dropdown -->
          <div class="relative language-dropdown">
            <button
              @click="toggleLanguageDropdown"
              class="flex items-center gap-2 px-3 py-2 font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors duration-200 bg-transparent border-none cursor-pointer"
            >
              <LanguageFlag :code="currentLanguage.code" />
              <span class="text-sm">{{ currentLanguage.name }}</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <div
              v-show="languageDropdownOpen"
              class="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-1 z-50"
            >
              <button
                v-for="lang in languages"
                :key="lang.code"
                @click="setLanguage(lang.code)"
                class="w-full flex items-center gap-3 px-4 py-2 text-left text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors bg-transparent border-none cursor-pointer"
                :class="{ 'bg-slate-100 dark:bg-slate-700': locale === lang.code }"
              >
                <LanguageFlag :code="lang.code" />
                <span class="text-sm">{{ lang.name }}</span>
              </button>
            </div>
          </div>

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
          <div v-else>
            <ProfileDropdown :user="user" @logout="logout" />
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

          <!-- Language Selection for Mobile -->
          <div class="flex flex-col gap-1">
            <span class="px-3 py-1 text-xs text-slate-400 dark:text-slate-500 uppercase tracking-wider">{{ t('language.label') }}</span>
            <button
              v-for="lang in languages"
              :key="lang.code"
              @click="setLanguage(lang.code); closeMobileMenu()"
              class="flex items-center gap-3 px-3 py-2 text-left font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors duration-200 bg-transparent border-none cursor-pointer"
              :class="{ 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white': locale === lang.code }"
            >
              <LanguageFlag :code="lang.code" />
              <span class="text-sm">{{ lang.name }}</span>
            </button>
          </div>

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
          <div v-else class="flex flex-col gap-1 px-3">
            <!-- User info -->
            <div class="flex items-center gap-3 py-3 border-b border-slate-200 dark:border-slate-700 mb-2">
              <div class="w-10 h-10 rounded-full flex items-center justify-center overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
                <img
                  v-if="user?.picture_url"
                  :src="user.picture_url"
                  :alt="user?.full_name || user?.email"
                  class="w-full h-full object-cover"
                />
                <span v-else>{{ getMobileInitials() }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-900 dark:text-white truncate">
                  {{ user?.full_name || user?.name || user?.email }}
                </p>
                <p class="text-xs text-slate-500 dark:text-slate-400 truncate">
                  {{ user?.email }}
                </p>
              </div>
            </div>

            <!-- Account Settings link -->
            <RouterLink
              to="/account/settings"
              @click="closeMobileMenu"
              class="flex items-center gap-3 px-3 py-2.5 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors no-underline"
            >
              <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span class="text-sm font-medium">{{ t('profile.accountSettings') }}</span>
            </RouterLink>

            <!-- Switch organization -->
            <RouterLink
              to="/organization"
              @click="closeMobileMenu"
              class="flex items-center gap-3 px-3 py-2.5 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors no-underline"
            >
              <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <span class="text-sm font-medium">{{ t('profile.switchOrganization') }}</span>
            </RouterLink>

            <!-- Logout -->
            <button
              @click="handleMobileLogout"
              class="flex items-center gap-3 px-3 py-2.5 mt-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors w-full text-left bg-transparent border-none cursor-pointer"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span class="text-sm font-medium">{{ t('nav.logout') }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>

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
</template>
