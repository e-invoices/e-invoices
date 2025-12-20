<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { organizationApi, type OrganizationWithRole } from '@/api/v1/organization.ts'
import { authApi } from '@/api/v1/auth.ts'
import { useAuth } from '@/composables/useAuth.ts'
import JoinOrganizationModal from '@/components/organization/JoinOrganizationModal.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const { currentUser } = useAuth()

const organizations = ref<OrganizationWithRole[]>([])
const loading = ref(true)
const switching = ref(false)
const error = ref('')
const showJoinModal = ref(false)
const initialJoinCode = ref('')

const userName = computed(() => {
  return currentUser.value?.full_name || currentUser.value?.email || 'Корисник'
})

const hasOrganizations = computed(() => organizations.value.length > 0)

const loadOrganizations = async () => {
  try {
    loading.value = true
    error.value = ''
    const response = await organizationApi.getMyOrganizations()
    organizations.value = response.organizations
  } catch (err) {
    error.value = (err as Error).message || 'Не може да се вчитаат организациите.'
  } finally {
    loading.value = false
  }
}

const selectOrganization = async (org: OrganizationWithRole) => {
  try {
    switching.value = true
    error.value = ''

    // Call switch-organization to get token with org context
    const response = await authApi.switchOrganization({ organization_id: org.id })

    // Store new tokens
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    localStorage.setItem('selected_organization_id', org.id.toString())

    router.push('/organization/overview')
  } catch (err) {
    error.value = (err as Error).message || 'Не може да се смени организацијата.'
    switching.value = false
  }
}

const createNewOrganization = () => {
  router.push('/organization/create')
}

const openJoinModal = (codeOrEvent?: string | PointerEvent | Event) => {
  if (typeof codeOrEvent === 'string') {
    initialJoinCode.value = codeOrEvent
  } else {
    initialJoinCode.value = ''
  }
  showJoinModal.value = true
}

const handleJoinSuccess = async () => {
  showJoinModal.value = false
  initialJoinCode.value = ''
  // Clear the join query param from URL
  if (route.query.join) {
    router.replace({ query: {} })
  }
  // Reload organizations to get the newly joined one
  await loadOrganizations()
  // If there's only one organization now, auto-select it
  if (organizations.value.length === 1 && organizations.value[0]) {
    await selectOrganization(organizations.value[0])
  }
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
  // Check for join code in URL query params - redirect to JoinPage
  const joinCode = route.query.join as string
  if (joinCode) {
    router.replace(`/organization/join?code=${joinCode}`)
    return
  }

  loadOrganizations()
})
</script>

<template>
  <div class="bg-gray-50 dark:bg-slate-950">
    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 py-8 sm:py-12">
      <!-- Welcome Section -->
      <div class="text-center mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-2">
          👋 {{ t('organization.select.welcome', { name: userName }) }}
        </h1>
        <p class="text-slate-600 dark:text-slate-400">
          {{ t('organization.select.subtitle') }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 mb-6">
        <p class="text-red-600 dark:text-red-400">{{ error }}</p>
        <button
          @click="loadOrganizations"
          class="mt-2 text-sm text-red-600 dark:text-red-400 underline"
        >
          {{ t('common.retry') }}
        </button>
      </div>

      <!-- Content -->
      <div v-else>
        <!-- Organizations List -->
        <div v-if="hasOrganizations" class="mb-8">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            {{ t('organization.select.yourOrganizations') }}
          </h2>
          <div class="space-y-3">
            <button
              v-for="org in organizations"
              :key="org.id"
              @click="selectOrganization(org)"
              class="w-full bg-white dark:bg-slate-800 rounded-xl p-4 sm:p-5 shadow-sm border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md transition-all duration-200 text-left group"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-1">
                    <h3 class="font-semibold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      {{ org.company_name }}
                    </h3>
                    <span
                      :class="getRoleBadgeClass(org.role)"
                      class="px-2 py-0.5 text-xs font-medium rounded-full"
                    >
                      {{ getRoleLabel(org.role) }}
                    </span>
                  </div>
                  <p class="text-sm text-slate-500 dark:text-slate-400">
                    {{ org.registration_name }}
                  </p>
                  <p class="text-sm text-slate-400 dark:text-slate-500 mt-1">
                    ЕДБ: {{ org.edb }}
                  </p>
                </div>
                <div class="text-slate-400 dark:text-slate-500 group-hover:text-blue-500 transition-colors">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- No Organizations Message -->
        <div v-else class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6 mb-8 text-center">
          <div class="text-4xl mb-3">🏢</div>
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            {{ t('organization.select.noOrganizations') }}
          </h3>
          <p class="text-slate-600 dark:text-slate-400 text-sm">
            {{ t('organization.select.noOrganizationsDesc') }}
          </p>
        </div>

        <!-- Action Buttons -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Create Organization -->
          <button
            @click="createNewOrganization"
            class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border-2 border-dashed border-slate-300 dark:border-slate-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-200 group"
          >
            <div class="flex flex-col items-center text-center">
              <div class="w-14 h-14 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <h3 class="font-semibold text-slate-900 dark:text-white mb-1">
                {{ t('organization.select.createNew') }}
              </h3>
              <p class="text-sm text-slate-500 dark:text-slate-400">
                {{ t('organization.select.createNewDesc') }}
              </p>
            </div>
          </button>

          <!-- Join Organization -->
          <button
            @click="openJoinModal"
            class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border-2 border-dashed border-slate-300 dark:border-slate-600 hover:border-green-400 dark:hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20 transition-all duration-200 group"
          >
            <div class="flex flex-col items-center text-center">
              <div class="w-14 h-14 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
              <h3 class="font-semibold text-slate-900 dark:text-white mb-1">
                {{ t('organization.select.joinExisting') }}
              </h3>
              <p class="text-sm text-slate-500 dark:text-slate-400">
                {{ t('organization.select.joinExistingDesc') }}
              </p>
            </div>
          </button>
        </div>

        <!-- Help Section -->
        <div class="mt-8 bg-slate-100 dark:bg-slate-800/50 rounded-xl p-4 sm:p-5">
          <div class="flex items-start gap-3">
            <div class="text-xl">💡</div>
            <div>
              <h4 class="font-medium text-slate-900 dark:text-white mb-1">
                {{ t('organization.select.helpTitle') }}
              </h4>
              <p class="text-sm text-slate-600 dark:text-slate-400">
                {{ t('organization.select.helpDesc') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Join Organization Modal -->
    <JoinOrganizationModal
      :show="showJoinModal"
      :initial-code="initialJoinCode"
      @close="showJoinModal = false"
      @success="handleJoinSuccess"
    />
  </div>
</template>
