<script setup lang="ts">
defineProps<{
  code: string
  size?: 'sm' | 'md' | 'lg'
}>()

// Map language codes to country codes for flags
const flagCodes: Record<string, string> = {
  mk: 'mk', // Macedonia
  en: 'gb', // United Kingdom
  sq: 'al', // Albania
}
</script>

<template>
  <span
    class="inline-flex items-center justify-center rounded-full overflow-hidden bg-slate-200 dark:bg-slate-700 flex-shrink-0"
    :class="{
      'w-5 h-5': size === 'sm',
      'w-6 h-6': size === 'md' || !size,
      'w-8 h-8': size === 'lg'
    }"
  >
    <img
      v-if="flagCodes[code]"
      :src="`https://flagcdn.com/w80/${flagCodes[code]}.png`"
      :alt="code"
      class="w-full h-full object-cover"
    />
    <!-- Fallback -->
    <span v-else class="text-xs font-bold text-slate-500 dark:text-slate-400">
      {{ code.toUpperCase() }}
    </span>
  </span>
</template>
