<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { organizationApi } from '@/api/v1/organization.ts'
import type { OrganizationWithRole } from '@/types/organization.ts'
import EditOrganization from '@/components/organization/EditOrganization.vue'

const { t } = useI18n()
const router = useRouter()

const organizationData = ref<OrganizationWithRole | null>(null)
const loading = ref(true)

// Computed properties
const organization = computed(() => organizationData.value)
const userRole = computed(() => organizationData.value?.role ?? 'member')
const canEditOrganization = computed(() =>
  ['owner', 'admin'].includes(userRole.value)
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

const handleOrganizationUpdated = (updated: OrganizationWithRole) => {
  organizationData.value = updated
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
          {{ t('settings.editOrganization.title') }}
        </h1>
        <p class="mt-2 text-slate-600 dark:text-slate-400">
          {{ t('settings.editOrganization.description') }}
        </p>
      </div>

      <!-- Content -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700">
        <EditOrganization
          :organization="organization"
          :can-edit="canEditOrganization"
          @updated="handleOrganizationUpdated"
        />
      </div>
    </div>
  </div>
</template>
