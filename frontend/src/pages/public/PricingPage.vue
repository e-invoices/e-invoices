<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-12 md:py-16 lg:py-20 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto">
      <h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-slate-900 mb-4 md:mb-6">
        {{ t('pricing.title') }}
      </h1>
      <p class="text-base sm:text-lg md:text-xl text-slate-600 leading-relaxed">
        {{ t('pricing.description') }}
      </p>
    </div>
  </div>
</template>
