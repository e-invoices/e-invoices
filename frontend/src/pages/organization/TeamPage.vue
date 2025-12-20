<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { organizationApi } from '@/api/v1/organization.ts'
import type { OrganizationWithRole } from '@/types/organization.ts'
import ManageTeam from '@/components/organization/ManageTeam.vue'

const { t } = useI18n()
const router = useRouter()

const organizationData = ref<OrganizationWithRole | null>(null)
const loading = ref(true)

// Computed properties
const organization = computed(() => organizationData.value)
const userRole = computed(() => organizationData.value?.role ?? 'member')
const canManageTeam = computed(() =>
  ['owner', 'admin', 'accountant'].includes(userRole.value)
)

const loadOrganization = async () => {
  const orgId = localStorage.getItem('selected_organization_id')
  if (!orgId) {
    await router.push('/organization')
    return
  }

  try {
    loading.value = true
    organizationData.value = await organizationApi.getOrganization(parseInt(orgId))
  } catch {
    await router.push('/organization')
  } finally {
    loading.value = false
  }
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
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">
          {{ t('settings.manageTeam.title') }}
        </h1>
        <p class="mt-2 text-slate-600 dark:text-slate-400">
          {{ t('settings.manageTeam.description') }}
        </p>
      </div>

      <!-- Content -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
        <ManageTeam
          :organization="organization"
          :user-role="userRole"
          :can-manage="canManageTeam"
        />
      </div>
    </div>
  </div>
</template>
