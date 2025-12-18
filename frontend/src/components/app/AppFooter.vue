<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <footer class="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 mt-12 md:mt-16">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8 text-center">
      <p class="text-slate-500 dark:text-slate-400 text-sm md:text-base">{{ t('footer.rights') }}</p>
    </div>
  </footer>
</template>
