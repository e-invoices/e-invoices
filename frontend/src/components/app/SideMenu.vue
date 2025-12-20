<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  isOpen: boolean
  isCollapsed: boolean
}>()

const emit = defineEmits<{
  close: []
  'update:isCollapsed': [value: boolean]
}>()

const { t } = useI18n()
const route = useRoute()

const menuItems = computed(() => [
  {
    label: t('nav.overview'),
    path: '/organization/overview',
    icon: 'home',
  },
  {
    label: t('nav.settingsSettings'),
    path: '/organization/settings',
    icon: 'settings',
  },
  {
    label: t('nav.settingsTeam'),
    path: '/organization/team',
    icon: 'team',
  },
])

const isActive = (path: string) => {
  return route.path === path
}

const handleLinkClick = () => {
  // Close menu on mobile after clicking a link
  emit('close')
}

const toggleCollapse = () => {
  emit('update:isCollapsed', !props.isCollapsed)
}
</script>

<template>
  <!-- Backdrop for mobile -->
  <div
    v-if="isOpen"
    class="fixed inset-0 bg-black/50 z-40 lg:hidden"
    @click="emit('close')"
  ></div>

  <!-- Sidebar -->
  <aside
    :class="[
      'fixed left-0 z-40 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 transition-all duration-300 ease-in-out flex flex-col',
      'top-14 md:top-16 h-[calc(100vh-3.5rem)] md:h-[calc(100vh-4rem)]',
      'lg:top-0 lg:h-screen',
      isCollapsed ? 'lg:w-16' : 'lg:w-64',
      isOpen ? 'translate-x-0 w-64' : '-translate-x-full lg:translate-x-0'
    ]"
  >
    <!-- Logo (desktop only) -->
    <div :class="['hidden lg:flex items-center h-14 md:h-16 px-4 border-b border-slate-200 dark:border-slate-800', isCollapsed ? 'justify-center' : 'gap-3']">
      <RouterLink to="/" class="flex items-center gap-3">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <span class="text-white font-bold text-sm">eF</span>
        </div>
        <span v-if="!isCollapsed" class="text-xl font-semibold text-slate-900 dark:text-white">e-Faktura</span>
      </RouterLink>
    </div>

    <!-- Menu Items -->
    <nav class="flex-1 p-2 space-y-1">
      <RouterLink
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        @click="handleLinkClick"
        :class="[
          'flex items-center gap-3 px-3 py-3 rounded-lg font-medium transition-colors duration-200 no-underline',
          isCollapsed ? 'lg:justify-center lg:px-0' : '',
          isActive(item.path)
            ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white'
        ]"
        :title="isCollapsed ? item.label : undefined"
      >
        <!-- Home/Overview Icon -->
        <svg v-if="item.icon === 'home'" class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <!-- Settings Icon -->
        <svg v-if="item.icon === 'settings'" class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <!-- Team Icon -->
        <svg v-if="item.icon === 'team'" class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <span :class="['transition-opacity duration-200', isCollapsed ? 'lg:hidden' : '']">
          {{ item.label }}
        </span>
      </RouterLink>
    </nav>

    <!-- Collapse Toggle Button (desktop only) -->
    <div class="hidden lg:block p-2 border-t border-slate-200 dark:border-slate-800">
      <button
        @click="toggleCollapse"
        class="w-full flex items-center justify-center p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors duration-200"
        :title="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <svg
          class="w-5 h-5 transition-transform duration-300"
          :class="isCollapsed ? 'rotate-180' : ''"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
      </button>
    </div>
  </aside>
</template>
