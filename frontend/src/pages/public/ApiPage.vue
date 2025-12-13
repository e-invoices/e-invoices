<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="page-container">
    <div class="container">
      <h1>{{ t('api.title') }}</h1>
      <p>{{ t('api.description') }}</p>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  padding: 4rem 0;
}
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}
h1 {
  font-size: 2.5rem;
  color: #0f172a;
  margin-bottom: 1.5rem;
}
</style>
