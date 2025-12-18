<script setup lang="ts">
import { RouterView } from 'vue-router'
import PublicNavbar from '@/components/app/PublicNavbar.vue'
import AppFooter from '@/components/app/AppFooter.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 font-sans text-slate-800 dark:text-slate-200">
    <PublicNavbar />

    <!-- Main Content -->
    <main class="flex-1 flex flex-col">
      <RouterView />
    </main>

    <AppFooter />
  </div>
</template>
