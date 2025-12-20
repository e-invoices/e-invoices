<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/composables/useTheme'

const { setupAuthListeners, checkSession } = useAuth()
const { initTheme } = useTheme()

onMounted(async () => {
  setupAuthListeners()
  initTheme()
  // Check for existing session on app load
  await checkSession()
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
