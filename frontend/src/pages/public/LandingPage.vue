<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useAuth } from '@/composables/useAuth'

const { t } = useI18n()
const { openRegister } = useAuth()
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <section class="py-8 md:py-16 px-4">
      <div class="max-w-7xl mx-auto bg-white rounded-2xl md:rounded-3xl shadow-lg p-6 md:p-12">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-center">
          <!-- Hero Text -->
          <div class="order-2 lg:order-1">
            <div class="text-blue-500 font-semibold tracking-wide text-sm mb-4 md:mb-6 uppercase min-h-[20px]">
              {{ t('landing.eyebrow') }}
            </div>
            <h1 class="text-3xl sm:text-4xl md:text-5xl font-extrabold text-slate-900 leading-tight mb-4 md:mb-6 whitespace-pre-line min-h-[120px] md:min-h-[180px]">
              {{ t('landing.title') }}
            </h1>
            <p class="text-base md:text-lg text-slate-600 leading-relaxed mb-3 md:mb-4 min-h-[72px] md:min-h-[56px]">
              {{ t('landing.description') }}
            </p>
            <p class="text-sm text-slate-500 leading-relaxed mb-6 md:mb-10 min-h-[48px]">
              {{ t('landing.subtext') }}
            </p>

            <div class="flex flex-col sm:flex-row gap-3 md:gap-4">
              <button
                @click="openRegister"
                class="min-w-[180px] inline-block text-center px-6 md:px-8 py-3 md:py-4 bg-blue-500 text-white font-semibold rounded-full shadow-lg shadow-blue-500/50 hover:bg-blue-600 hover:-translate-y-0.5 transition-all duration-200 whitespace-nowrap border-none cursor-pointer"
              >
                {{ t('landing.startFree') }}
              </button>
              <a
                href="/demo"
                class="min-w-[160px] inline-block text-center px-6 md:px-8 py-3 md:py-4 border border-slate-200 text-slate-900 font-semibold rounded-full bg-white hover:border-slate-300 hover:bg-slate-50 transition-all duration-200 whitespace-nowrap no-underline"
              >
                {{ t('landing.viewDemo') }}
              </a>
            </div>
          </div>

          <!-- Hero Visual -->
          <div class="order-1 lg:order-2 flex flex-col gap-4 md:gap-6">
            <div class="bg-white rounded-xl overflow-hidden shadow-md">
              <img
                src="https://placehold.co/600x400/e2e8f0/1e293b?text=Business+Image"
                alt="Business Person"
                class="w-full h-auto"
              />
              <div class="py-2 md:py-3 px-3 text-center text-xs text-slate-500 bg-slate-50 min-h-[40px] flex items-center justify-center">
                {{ t('landing.imageCaption') }}
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
              <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-slate-100 min-h-[140px]">
                <div class="text-sm text-slate-500 mb-2 min-h-[20px]">{{ t('landing.stats.timeLabel') }}</div>
                <div class="text-xl md:text-2xl font-bold text-slate-900 mb-2 min-h-[32px]">{{ t('landing.stats.timeValue') }}</div>
                <div class="text-sm text-slate-500 min-h-[40px]">{{ t('landing.stats.timeDesc') }}</div>
              </div>

              <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-slate-100 min-h-[140px]">
                <div class="text-sm text-slate-500 mb-2 min-h-[20px]">{{ t('landing.stats.complianceLabel') }}</div>
                <div class="text-xl md:text-2xl font-bold text-slate-900 mb-2 min-h-[32px]">{{ t('landing.stats.complianceValue') }}</div>
                <div class="text-sm text-slate-500 min-h-[40px]">{{ t('landing.stats.complianceDesc') }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Add any additional custom styles here */
</style>
