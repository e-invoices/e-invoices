<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

const { t, locale } = useI18n()

const navItems = computed(() => [
  { label: t('nav.upload'), path: '/app/upload' },
  { label: t('nav.preview'), path: '/app/preview' },
])

const toggleLanguage = () => {
  locale.value = locale.value === 'mk' ? 'en' : 'mk'
}
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="header-left">
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
      </div>

      <button @click="toggleLanguage" class="lang-btn">
        {{ locale === 'mk' ? 'EN' : 'MK' }}
      </button>
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

.header-left {
  display: flex;
  align-items: center;
  gap: 2rem;
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

.lang-btn {
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem 1rem;
  transition: all 0.2s;
}

.lang-btn:hover {
  color: #0f172a;
  border-color: #cbd5e1;
  background: #f8fafc;
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
