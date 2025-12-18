<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { organizationApi } from '@/api/v1/organization.ts'
import type { OrganizationWithRole } from '@/types/organization.ts'

const { t } = useI18n()
const router = useRouter()

const organizationData = ref<OrganizationWithRole | null>(null)
const loading = ref(true)
const showWelcomeBanner = ref(false)

// Computed properties for type-safe template access
const organization = computed(() => organizationData.value)
const orgCompanyName = computed(() => organizationData.value?.company_name ?? '')
const orgRegistrationName = computed(() => organizationData.value?.registration_name ?? '')
const orgRole = computed(() => organizationData.value?.role ?? 'member')
const orgEdb = computed(() => organizationData.value?.edb ?? '')
const orgEmbs = computed(() => organizationData.value?.embs ?? '')
const orgVatRegistered = computed(() => organizationData.value?.vat_registered ?? false)
const orgAddress = computed(() => organizationData.value?.address ?? '')
const orgContactPerson = computed(() => organizationData.value?.contact_person ?? '')
const orgContactEmail = computed(() => organizationData.value?.contact_email ?? '')
const orgContactPhone = computed(() => organizationData.value?.contact_phone ?? '')

const loadOrganization = async () => {
  const orgId = localStorage.getItem('selected_organization_id')
  if (!orgId) {
    await router.push('/app/organizations')
    return
  }

  // Check if this is the first time viewing this organization (show welcome banner)
  const welcomeShownKey = `welcome_shown_org_${orgId}`
  if (!localStorage.getItem(welcomeShownKey)) {
    showWelcomeBanner.value = true
    localStorage.setItem(welcomeShownKey, 'true')
  }

  try {
    loading.value = true
    organizationData.value = await organizationApi.getOrganization(parseInt(orgId))
  } catch {
    // If organization not found, redirect to selection
    await router.push('/app/organizations')
  } finally {
    loading.value = false
  }
}

const dismissWelcomeBanner = () => {
  showWelcomeBanner.value = false
}

const getRoleBadgeClass = (role: string) => {
  const classes: Record<string, string> = {
    owner: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
    admin: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    accountant: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    member: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    viewer: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
  }
  return classes[role] || classes.member
}

const getRoleLabel = (role: string) => {
  const labels: Record<string, string> = {
    owner: t('organization.roles.owner'),
    admin: t('organization.roles.admin'),
    accountant: t('organization.roles.accountant'),
    member: t('organization.roles.member'),
    viewer: t('organization.roles.viewer'),
  }
  return labels[role] || role
}

onMounted(() => {
  loadOrganization()
})
</script>

<template>
  <div class="bg-gray-50 dark:bg-slate-950 min-h-full">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-24">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
    </div>

    <!-- Main Content -->
    <div v-else class="max-w-6xl mx-auto px-4 py-8 sm:py-12">
      <!-- Success Banner (shown only once per organization) -->
      <div
        v-if="showWelcomeBanner"
        class="bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl p-6 sm:p-8 mb-8 text-white relative"
      >
        <button
          @click="dismissWelcomeBanner"
          class="absolute top-4 right-4 p-1 rounded-full hover:bg-white/20 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <div class="flex items-start gap-4">
          <div class="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold mb-2">
              {{ t('dashboard.successTitle') }}
            </h1>
            <p class="text-white/90 text-lg">
              {{ t('dashboard.successSubtitle') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Organization Info Card -->
      <div v-if="organization" class="bg-white dark:bg-slate-800 rounded-2xl shadow-lg p-6 sm:p-8 mb-8">
        <div class="flex items-start justify-between mb-6">
          <div>
            <div class="flex items-center gap-3 mb-2">
              <h2 class="text-xl font-bold text-slate-900 dark:text-white">
                {{ orgCompanyName }}
              </h2>
              <span
                :class="getRoleBadgeClass(orgRole)"
                class="px-2.5 py-1 text-xs font-medium rounded-full"
              >
                {{ getRoleLabel(orgRole) }}
              </span>
            </div>
            <p class="text-slate-500 dark:text-slate-400">
              {{ orgRegistrationName }}
            </p>
          </div>
          <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
            <p class="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">{{ t('dashboard.edb') }}</p>
            <p class="font-mono font-medium text-slate-900 dark:text-white">{{ orgEdb }}</p>
          </div>
          <div class="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
            <p class="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">{{ t('dashboard.embs') }}</p>
            <p class="font-mono font-medium text-slate-900 dark:text-white">{{ orgEmbs }}</p>
          </div>
          <div class="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
            <p class="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">{{ t('dashboard.vatStatus') }}</p>
            <p class="font-medium text-slate-900 dark:text-white">
              {{ orgVatRegistered ? t('dashboard.vatYes') : t('dashboard.vatNo') }}
            </p>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">{{ t('dashboard.address') }}</p>
              <p class="text-slate-900 dark:text-white">{{ orgAddress }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">{{ t('dashboard.contact') }}</p>
              <p class="text-slate-900 dark:text-white">{{ orgContactPerson }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ orgContactEmail }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ orgContactPhone }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
        {{ t('dashboard.quickActions') }}
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <!-- Create Invoice -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-5 shadow-sm border border-slate-200 dark:border-slate-700 opacity-60 cursor-not-allowed">
          <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center mb-3">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h4 class="font-semibold text-slate-900 dark:text-white mb-1">{{ t('dashboard.createInvoice') }}</h4>
          <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('dashboard.createInvoiceDesc') }}</p>
          <span class="inline-block mt-2 text-xs bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 px-2 py-1 rounded">
            {{ t('dashboard.comingSoon') }}
          </span>
        </div>

        <!-- View Invoices -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-5 shadow-sm border border-slate-200 dark:border-slate-700 opacity-60 cursor-not-allowed">
          <div class="w-10 h-10 bg-green-100 dark:bg-green-900/50 rounded-lg flex items-center justify-center mb-3">
            <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </div>
          <h4 class="font-semibold text-slate-900 dark:text-white mb-1">{{ t('dashboard.viewInvoices') }}</h4>
          <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('dashboard.viewInvoicesDesc') }}</p>
          <span class="inline-block mt-2 text-xs bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 px-2 py-1 rounded">
            {{ t('dashboard.comingSoon') }}
          </span>
        </div>

        <!-- Settings -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-5 shadow-sm border border-slate-200 dark:border-slate-700 opacity-60 cursor-not-allowed">
          <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/50 rounded-lg flex items-center justify-center mb-3">
            <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h4 class="font-semibold text-slate-900 dark:text-white mb-1">{{ t('dashboard.settings') }}</h4>
          <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('dashboard.settingsDesc') }}</p>
          <span class="inline-block mt-2 text-xs bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 px-2 py-1 rounded">
            {{ t('dashboard.comingSoon') }}
          </span>
        </div>
      </div>

      <!-- Info Banner -->
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-5 flex items-start gap-4">
        <div class="w-10 h-10 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h4 class="font-medium text-slate-900 dark:text-white mb-1">
            {{ t('dashboard.infoTitle') }}
          </h4>
          <p class="text-sm text-slate-600 dark:text-slate-400">
            {{ t('dashboard.infoDesc') }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
