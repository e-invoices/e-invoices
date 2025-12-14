<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'

const { t, locale } = useI18n()

const mobileMenuOpen = ref(false)

const navItems = computed(() => [
  { label: t('nav.upload'), path: '/app/upload' },
  { label: t('nav.preview'), path: '/app/preview' },
])

const toggleLanguage = () => {
  locale.value = locale.value === 'mk' ? 'en' : 'mk'
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900 p-4 md:p-6 lg:p-8 font-sans">
    <!-- Header -->
    <header class="bg-white rounded-xl md:rounded-2xl shadow-lg p-4 md:p-6">
      <div class="flex items-center justify-between gap-4">
        <!-- Left Section: Logo & Nav -->
        <div class="flex items-center gap-4 md:gap-8">
          <div>
            <p class="uppercase tracking-widest text-xs text-slate-500 mb-0.5">E-Invoices</p>
            <h1 class="text-lg md:text-xl font-bold text-slate-900 m-0">Document Workbench</h1>
          </div>

          <!-- Desktop Navigation -->
          <nav class="hidden sm:flex gap-2 md:gap-3">
            <RouterLink
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="min-w-[90px] text-center px-3 md:px-4 py-2 text-slate-900 font-semibold rounded-full border border-slate-200 bg-white hover:border-slate-300 transition-colors duration-200 no-underline text-sm whitespace-nowrap"
              active-class="!bg-slate-200 !border-slate-300"
            >
              {{ item.label }}
            </RouterLink>
          </nav>
        </div>

        <!-- Right Section -->
        <div class="flex items-center gap-2 md:gap-4">
          <button
            @click="toggleLanguage"
            class="hidden sm:block w-12 text-center px-3 md:px-4 py-2 border border-slate-200 rounded-lg font-semibold text-slate-500 hover:text-slate-900 hover:border-slate-300 hover:bg-slate-50 transition-all duration-200 bg-transparent cursor-pointer text-sm"
          >
            {{ locale === 'mk' ? 'EN' : 'MK' }}
          </button>

          <!-- Mobile Menu Button -->
          <button
            @click="toggleMobileMenu"
            class="sm:hidden p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors duration-200 bg-transparent border-none cursor-pointer"
          >
            <svg v-if="!mobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div
        v-show="mobileMenuOpen"
        class="sm:hidden mt-4 pt-4 border-t border-slate-100"
      >
        <nav class="flex flex-col gap-2">
          <RouterLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="px-3 py-2 text-slate-900 font-semibold rounded-lg hover:bg-slate-100 transition-colors duration-200 no-underline"
            active-class="bg-slate-200"
            @click="mobileMenuOpen = false"
          >
            {{ item.label }}
          </RouterLink>
        </nav>
        <button
          @click="toggleLanguage"
          class="mt-3 w-full px-3 py-2 text-left border border-slate-200 rounded-lg font-semibold text-slate-500 hover:text-slate-900 hover:bg-slate-50 transition-all duration-200 bg-transparent cursor-pointer"
        >
          {{ locale === 'mk' ? 'Switch to English' : 'Премини на Македонски' }}
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="mt-4 md:mt-6 lg:mt-8 bg-white rounded-xl md:rounded-2xl p-4 md:p-6 lg:p-8 shadow-lg">
      <RouterView />
    </main>
  </div>
</template>

