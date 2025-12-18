<script setup lang="ts">
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import PublicNavbar from '@/components/app/PublicNavbar.vue'
import SideMenu from '@/components/app/SideMenu.vue'

const sideMenuOpen = ref(false)
const sideMenuCollapsed = ref(false)

const toggleSideMenu = () => {
  sideMenuOpen.value = !sideMenuOpen.value
}

const closeSideMenu = () => {
  sideMenuOpen.value = false
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 font-sans text-slate-800 dark:text-slate-200">
    <!-- Navbar with menu toggle button -->
    <div class="relative">
      <PublicNavbar />
      <!-- Mobile menu toggle button -->
      <button
        @click="toggleSideMenu"
        class="lg:hidden fixed top-4 md:top-5 left-4 z-50 p-2 rounded-lg bg-white dark:bg-slate-800 shadow-md border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
      >
        <svg v-if="!sideMenuOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Side Menu -->
    <SideMenu
      :is-open="sideMenuOpen"
      v-model:is-collapsed="sideMenuCollapsed"
      @close="closeSideMenu"
    />

    <!-- Main Content (with left padding for sidebar on desktop) -->
    <main
      :class="[
        'min-h-[calc(100vh-4rem)] md:min-h-[calc(100vh-5rem)] transition-all duration-300',
        sideMenuCollapsed ? 'lg:ml-16' : 'lg:ml-64'
      ]"
    >
      <RouterView />
    </main>
  </div>
</template>
