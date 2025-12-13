<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

const { t, locale } = useI18n()

const menuItems = computed(() => [
  { label: t('nav.howItWorks'), path: '/how-it-works' },
  { label: t('nav.benefits'), path: '/benefits' },
  { label: t('nav.pricing'), path: '/pricing' },
])

const toggleLanguage = () => {
  locale.value = locale.value === 'mk' ? 'en' : 'mk'
}
</script>

<template>
  <div class="public-layout">
    <header class="public-header">
      <div class="container header-content">
        <div class="logo">
          <RouterLink to="/">e-Faktura</RouterLink>
        </div>

        <nav class="public-nav">
          <RouterLink
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="nav-link"
          >
            {{ item.label }}
          </RouterLink>
        </nav>

        <div class="right-section">
          <button @click="toggleLanguage" class="lang-btn">
            {{ locale === 'mk' ? 'EN' : 'MK' }}
          </button>
          <div class="auth-buttons">
            <a href="/login" class="btn btn-outline">{{ t('nav.login') }}</a>
            <a href="/register" class="btn btn-primary">{{ t('nav.register') }}</a>
          </div>
        </div>
      </div>
    </header>

    <main class="public-main">
      <RouterView />
    </main>

    <footer class="public-footer">
      <div class="container">
        <p>{{ t('footer.rights') }}</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.public-layout {
  min-height: 100vh;
  background: #f8fafc;
  font-family: 'Inter', sans-serif;
  color: #1e293b;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.public-header {
  background: white;
  padding: 1rem 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo a {
  font-weight: 700;
  font-size: 1.5rem;
  color: #0f172a;
  text-decoration: none;
}

.public-nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #0f172a;
}

.right-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.lang-btn {
  background: none;
  border: none;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.2s;
}

.lang-btn:hover {
  color: #0f172a;
}

.auth-buttons {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1.5rem;
  border-radius: 9999px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.btn-outline {
  border: 1px solid #e2e8f0;
  color: #0f172a;
}

.btn-outline:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border: 1px solid #3b82f6;
}

.btn-primary:hover {
  background: #2563eb;
}

.public-footer {
  background: white;
  padding: 2rem 0;
  margin-top: 4rem;
  border-top: 1px solid #e2e8f0;
  text-align: center;
  color: #64748b;
}
</style>
