<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="landing-page">
    <section class="hero">
      <div class="container hero-content">
        <div class="hero-text">
          <div class="eyebrow">{{ t('landing.eyebrow') }}</div>
          <h1 class="hero-title" style="white-space: pre-line">
            {{ t('landing.title') }}
          </h1>
          <p class="hero-description">
            {{ t('landing.description') }}
          </p>
          <p class="hero-subtext">
            {{ t('landing.subtext') }}
          </p>

          <div class="hero-actions">
            <a href="/register" class="btn btn-primary btn-lg">{{ t('landing.startFree') }}</a>
            <a href="/demo" class="btn btn-outline btn-lg">{{ t('landing.viewDemo') }}</a>
          </div>
        </div>

        <div class="hero-visual">
          <div class="image-card">
            <!-- Placeholder for the business person image -->
            <div class="image-placeholder">
              <img src="https://placehold.co/600x400/e2e8f0/1e293b?text=Business+Image" alt="Business Person" />
            </div>
            <div class="caption">
              {{ t('landing.imageCaption') }}
            </div>
          </div>

          <div class="stats-cards">
            <div class="stat-card">
              <div class="stat-label">{{ t('landing.stats.timeLabel') }}</div>
              <div class="stat-value">{{ t('landing.stats.timeValue') }}</div>
              <div class="stat-desc">{{ t('landing.stats.timeDesc') }}</div>
            </div>

            <div class="stat-card">
              <div class="stat-label">{{ t('landing.stats.complianceLabel') }}</div>
              <div class="stat-value">{{ t('landing.stats.complianceValue') }}</div>
              <div class="stat-desc">{{ t('landing.stats.complianceDesc') }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.hero {
  padding: 4rem 0;
  background: white;
  border-radius: 2rem;
  margin: 2rem auto;
  max-width: 1300px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.01);
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.eyebrow {
  color: #3b82f6;
  font-weight: 600;
  letter-spacing: 0.05em;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
  text-transform: uppercase;
}

.hero-title {
  font-size: 3rem;
  line-height: 1.1;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 1.5rem;
}

.hero-description {
  font-size: 1.125rem;
  color: #475569;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.hero-subtext {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.5;
  margin-bottom: 2.5rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 9999px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  display: inline-block;
}

.btn-lg {
  padding: 0.875rem 2rem;
  font-size: 1rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border: 1px solid #3b82f6;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-outline {
  border: 1px solid #e2e8f0;
  color: #0f172a;
  background: white;
}

.btn-outline:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.hero-visual {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.image-card {
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.image-placeholder img {
  width: 100%;
  height: auto;
  display: block;
}

.caption {
  padding: 0.75rem;
  text-align: center;
  font-size: 0.75rem;
  color: #64748b;
  background: #f8fafc;
}

.stats-cards {
  display: grid;
  gap: 1rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.stat-desc {
  font-size: 0.875rem;
  color: #64748b;
}

@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .hero-title {
    font-size: 2rem;
  }
}
</style>
