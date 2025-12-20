<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import LanguageFlag from './LanguageFlag.vue'

const { locale } = useI18n()

const dropdownOpen = ref(false)

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
  dropdownOpen.value = false
}

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
}

// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.language-switcher')) {
    dropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="relative language-switcher">
    <button
      @click="toggleDropdown"
      class="flex items-center justify-center hover:opacity-80 transition-opacity cursor-pointer border-none bg-transparent p-0"
    >
      <LanguageFlag :code="currentLanguage.code" size="xl" />
    </button>

    <!-- Dropdown Menu -->
    <div
      v-show="dropdownOpen"
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
</template>
