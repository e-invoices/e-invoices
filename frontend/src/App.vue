<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/composables/useTheme'

const { setupAuthListeners } = useAuth()
const { initTheme } = useTheme()

onMounted(() => {
  setupAuthListeners()
  initTheme()
})
</script>

<template>
  <RouterView />
</template>

<style>
body {
  margin: 0;
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
</style>
