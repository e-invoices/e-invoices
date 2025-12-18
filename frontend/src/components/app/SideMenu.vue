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
    path: '/app/overview',
    icon: 'home',
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
      'fixed top-16 md:top-20 left-0 z-40 h-[calc(100vh-4rem)] md:h-[calc(100vh-5rem)] bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 transition-all duration-300 ease-in-out flex flex-col',
      isCollapsed ? 'lg:w-16' : 'lg:w-64',
      isOpen ? 'translate-x-0 w-64' : '-translate-x-full lg:translate-x-0'
    ]"
  >
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
