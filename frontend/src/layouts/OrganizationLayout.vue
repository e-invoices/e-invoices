<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import SideMenu from '@/components/app/SideMenu.vue'
import ThemeToggle from '@/components/ui/ThemeToggle.vue'
import LanguageSwitcher from '@/components/ui/LanguageSwitcher.vue'
import ProfileDropdown from '@/components/app/ProfileDropdown.vue'
import { useAuth } from '@/composables/useAuth'
import type { User } from '@/types/auth'

const { showSidebar = true, showProfile = true } = defineProps<{
  showSidebar?: boolean
  showProfile?: boolean
}>()

const { currentUser, logout, checkSession } = useAuth()
const user = computed(() => currentUser.value as User | null)

const sideMenuOpen = ref(false)
const sideMenuCollapsed = ref(false)

const toggleSideMenu = () => {
  sideMenuOpen.value = !sideMenuOpen.value
}

const closeSideMenu = () => {
  sideMenuOpen.value = false
}

// Ensure user session is loaded
onMounted(async () => {
  const hasToken = !!localStorage.getItem('access_token')
  if (hasToken && !currentUser.value) {
    await checkSession()
  }
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 font-sans text-slate-800 dark:text-slate-200">
    <!-- Minimal Header -->
    <header :class="[
      'h-14 md:h-16 flex items-center px-4 sm:px-6 lg:px-8',
      showSidebar ? 'justify-between lg:justify-end' : 'justify-between'
    ]">
      <!-- Left: Mobile menu toggle + Logo -->
      <div class="flex items-center gap-4" :class="{ 'lg:hidden': showSidebar }">
        <!-- Mobile menu toggle button (only if sidebar is enabled) -->
        <button
          v-if="showSidebar"
          @click="toggleSideMenu"
          class="lg:hidden p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          <svg v-if="!sideMenuOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-2">
          <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-sm">eF</span>
          </div>
          <span class="text-xl font-semibold text-slate-900 dark:text-white">e-Faktura</span>
        </RouterLink>
      </div>

      <!-- Right: Language + Theme + Profile -->
      <div class="flex items-center gap-2">
        <LanguageSwitcher />
        <ThemeToggle />
        <ProfileDropdown v-if="showProfile" :user="user" @logout="logout" />
      </div>
    </header>

    <!-- Side Menu (only if enabled) -->
    <SideMenu
      v-if="showSidebar"
      :is-open="sideMenuOpen"
      v-model:is-collapsed="sideMenuCollapsed"
      @close="closeSideMenu"
    />

    <!-- Main Content -->
    <main
      :class="[
        'min-h-[calc(100vh-3.5rem)] md:min-h-[calc(100vh-4rem)] transition-all duration-300',
        showSidebar ? (sideMenuCollapsed ? 'lg:ml-16' : 'lg:ml-64') : ''
      ]"
    >
      <RouterView />
    </main>
  </div>
</template>
