<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { User } from '@/types/auth'

const props = defineProps<{
  user: User | null
}>()

const emit = defineEmits<{
  logout: []
}>()

const { t } = useI18n()
const router = useRouter()

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)
const imageError = ref(false)

// Reset imageError when user changes
watch(() => props.user?.picture_url, () => {
  imageError.value = false
}, { immediate: true })

// Get initials from user name
const initials = computed(() => {
  if (!props.user) return '?'

  const name = props.user.full_name || props.user.name || props.user.email
  if (!name) return '?'

  const parts = name.trim().split(/\s+/)
  const firstPart = parts[0]
  const lastPart = parts[parts.length - 1]

  if (parts.length >= 2 && firstPart && lastPart && firstPart[0] && lastPart[0]) {
    // First letter of first name + first letter of last name
    return (firstPart[0] + lastPart[0]).toUpperCase()
  }
  // Just first two letters of single name/email
  return name.substring(0, 2).toUpperCase()
})

// Get display name
const displayName = computed(() => {
  if (!props.user) return ''
  return props.user.full_name || props.user.name || props.user.email
})

// Check if user has a profile picture and it hasn't errored
const showProfilePicture = computed(() => {
  return props.user?.picture_url && props.user.picture_url.length > 0 && !imageError.value
})

const handleImageError = () => {
  imageError.value = true
}

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const closeDropdown = () => {
  isOpen.value = false
}

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    closeDropdown()
  }
}

const goToAccountSettings = () => {
  closeDropdown()
  router.push('/account/settings')
}

const switchOrganization = () => {
  closeDropdown()
  router.push('/organization')
}

const handleLogout = () => {
  closeDropdown()
  emit('logout')
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="dropdownRef" class="relative">
    <!-- Profile Button -->
    <button
      @click="toggleDropdown"
      class="flex items-center gap-2 p-1 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
    >
      <!-- Avatar Circle -->
      <div class="w-9 h-9 rounded-full flex items-center justify-center overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold text-sm">
        <img
          v-if="showProfilePicture"
          :src="user?.picture_url"
          :alt="displayName"
          class="w-full h-full object-cover"
          referrerpolicy="no-referrer"
          @error="handleImageError"
        />
        <span v-else>{{ initials }}</span>
      </div>
    </button>

    <!-- Dropdown Menu -->
    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-show="isOpen"
        class="absolute right-0 mt-2 w-64 bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 py-2 z-50"
      >
        <!-- User Info Header -->
        <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-700">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full flex items-center justify-center overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
              <img
                v-if="showProfilePicture"
                :src="user?.picture_url"
                :alt="displayName"
                class="w-full h-full object-cover"
                referrerpolicy="no-referrer"
                @error="handleImageError"
              />
              <span v-else>{{ initials }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-900 dark:text-white truncate">
                {{ displayName }}
              </p>
              <p class="text-xs text-slate-500 dark:text-slate-400 truncate">
                {{ user?.email }}
              </p>
            </div>
          </div>
        </div>

        <!-- Menu Items -->
        <div class="py-1">
          <!-- Account Settings -->
          <button
            @click="goToAccountSettings"
            class="w-full flex items-center gap-3 px-4 py-2.5 text-left text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
          >
            <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span class="text-sm font-medium">{{ t('profile.accountSettings') }}</span>
          </button>

          <!-- Switch Organization -->
          <button
            @click="switchOrganization"
            class="w-full flex items-center gap-3 px-4 py-2.5 text-left text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
          >
            <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <span class="text-sm font-medium">{{ t('profile.switchOrganization') }}</span>
          </button>
        </div>

        <!-- Logout -->
        <div class="border-t border-slate-200 dark:border-slate-700 pt-1 mt-1">
          <button
            @click="handleLogout"
            class="w-full flex items-center gap-3 px-4 py-2.5 text-left text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span class="text-sm font-medium">{{ t('nav.logout') }}</span>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>
