<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

const navItems = [
  { label: 'Upload', path: '/upload' },
  { label: 'Preview', path: '/preview' },
]
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <div>
        <p class="eyebrow">E-Invoices</p>
        <h1>Document Workbench</h1>
      </div>
      <nav class="main-nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          active-class="nav-link--active"
        >
          {{ item.label }}
        </RouterLink>
      </nav>
    </header>

    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: #f8fafc;
  color: #0f172a;
  padding: 2rem;
  box-sizing: border-box;
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  background: #ffffff;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 15px 40px rgba(15, 23, 42, 0.05);
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-size: 0.75rem;
  color: rgba(15, 23, 42, 0.6);
}

.main-nav {
  display: flex;
  gap: 0.75rem;
}

.nav-link {
  color: #0f172a;
  text-decoration: none;
  padding: 0.45rem 1rem;
  border-radius: 999px;
  border: 1px solid rgba(15, 23, 42, 0.15);
  font-weight: 600;
  background: #ffffff;
  transition: background 0.2s ease, border 0.2s ease;
}

.nav-link:hover {
  border-color: rgba(15, 23, 42, 0.3);
}

.nav-link--active {
  background: #e2e8f0;
  border-color: rgba(15, 23, 42, 0.3);
}

.app-main {
  margin-top: 2rem;
  background: #ffffff;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 15px 40px rgba(15, 23, 42, 0.05);
}

@media (max-width: 640px) {
  .app-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .main-nav {
    flex-wrap: wrap;
  }
}
</style>
