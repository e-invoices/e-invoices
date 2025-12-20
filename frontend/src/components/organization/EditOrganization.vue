<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { organizationApi } from '@/api/v1/organization.ts'
import type { OrganizationWithRole } from '@/types/organization.ts'

const props = defineProps<{
  organization: OrganizationWithRole | null
  canEdit: boolean
}>()

const emit = defineEmits<{
  updated: [organization: OrganizationWithRole]
}>()

const { t } = useI18n()

// Form state
const isEditing = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')

// Form data
const formData = ref({
  company_name: '',
  registration_name: '',
  vat_registered: true,
  address: '',
  contact_person: '',
  contact_email: '',
  contact_phone: '',
})

// Watch for organization changes to reset form
watch(() => props.organization, (org) => {
  if (org) {
    formData.value = {
      company_name: org.company_name,
      registration_name: org.registration_name,
      vat_registered: org.vat_registered,
      address: org.address,
      contact_person: org.contact_person,
      contact_email: org.contact_email,
      contact_phone: org.contact_phone,
    }
  }
}, { immediate: true })

const startEditing = () => {
  isEditing.value = true
  error.value = ''
  success.value = ''
}

const cancelEditing = () => {
  isEditing.value = false
  error.value = ''
  // Reset form data
  if (props.organization) {
    formData.value = {
      company_name: props.organization.company_name,
      registration_name: props.organization.registration_name,
      vat_registered: props.organization.vat_registered,
      address: props.organization.address,
      contact_person: props.organization.contact_person,
      contact_email: props.organization.contact_email,
      contact_phone: props.organization.contact_phone,
    }
  }
}

const saveChanges = async () => {
  if (!props.organization) return

  error.value = ''
  success.value = ''
  saving.value = true

  try {
    const updated = await organizationApi.updateOrganization(props.organization.id, formData.value)
    success.value = t('settings.editOrganization.updateSuccess')
    isEditing.value = false

    // Emit updated organization with role info preserved
    emit('updated', {
      ...updated,
      role: props.organization.role,
      joined_at: props.organization.joined_at,
    })
  } catch (err: unknown) {
    const errorResponse = err as { response?: { data?: { detail?: string } } }
    error.value = errorResponse.response?.data?.detail || t('settings.editOrganization.updateFailed')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="p-6 sm:p-8">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-slate-900 dark:text-white">
        {{ t('settings.editOrganization.title') }}
      </h2>
      <div v-if="canEdit && !isEditing">
        <button
          @click="startEditing"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
        >
          {{ t('common.edit') }}
        </button>
      </div>
      <div v-else-if="isEditing" class="flex gap-2">
        <button
          @click="cancelEditing"
          class="px-4 py-2 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors text-sm font-medium"
        >
          {{ t('common.cancel') }}
        </button>
        <button
          @click="saveChanges"
          :disabled="saving"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium disabled:opacity-50"
        >
          {{ saving ? t('common.loading') : t('common.save') }}
        </button>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="success" class="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-300">
      {{ success }}
    </div>
    <div v-if="error" class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300">
      {{ error }}
    </div>

    <!-- Not Allowed Message -->
    <div v-if="!canEdit" class="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg text-amber-700 dark:text-amber-300">
      {{ t('settings.editOrganization.noPermission') }}
    </div>

    <!-- Organization Details Form -->
    <div class="space-y-6">
      <!-- Company Info Section -->
      <div>
        <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">
          {{ t('settings.editOrganization.companyInfo') }}
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.companyName') }}
            </label>
            <input
              v-model="formData.company_name"
              type="text"
              :disabled="!isEditing"
              class="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white disabled:bg-slate-100 dark:disabled:bg-slate-800 disabled:text-slate-500 dark:disabled:text-slate-400"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.registrationName') }}
            </label>
            <input
              v-model="formData.registration_name"
              type="text"
              :disabled="!isEditing"
              class="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white disabled:bg-slate-100 dark:disabled:bg-slate-800 disabled:text-slate-500 dark:disabled:text-slate-400"
            />
          </div>
        </div>
      </div>

      <!-- Tax Info Section (Read-only) -->
      <div>
        <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">
          {{ t('settings.editOrganization.taxInfo') }}
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.edb') }}
            </label>
            <input
              :value="organization?.edb"
              type="text"
              disabled
              class="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
            />
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {{ t('settings.editOrganization.cannotChangeEdb') }}
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.embs') }}
            </label>
            <input
              :value="organization?.embs"
              type="text"
              disabled
              class="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
            />
          </div>
          <div class="flex items-center gap-3 pt-6">
            <input
              v-model="formData.vat_registered"
              type="checkbox"
              :disabled="!isEditing"
              class="w-5 h-5 rounded border-slate-300 dark:border-slate-600 text-blue-500 focus:ring-blue-500"
            />
            <label class="text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('organization.create.vatRegistered') }}
            </label>
          </div>
        </div>
      </div>

      <!-- Address Section -->
      <div>
        <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">
          {{ t('settings.editOrganization.addressInfo') }}
        </h3>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            {{ t('organization.create.address') }}
          </label>
          <textarea
            v-model="formData.address"
            :disabled="!isEditing"
            rows="2"
            class="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white disabled:bg-slate-100 dark:disabled:bg-slate-800 disabled:text-slate-500 dark:disabled:text-slate-400 resize-none"
          ></textarea>
        </div>
      </div>

      <!-- Contact Section -->
      <div>
        <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">
          {{ t('settings.editOrganization.contactInfo') }}
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.contactPerson') }}
            </label>
            <input
              v-model="formData.contact_person"
              type="text"
              :disabled="!isEditing"
              class="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white disabled:bg-slate-100 dark:disabled:bg-slate-800 disabled:text-slate-500 dark:disabled:text-slate-400"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.contactEmail') }}
            </label>
            <input
              v-model="formData.contact_email"
              type="email"
              :disabled="!isEditing"
              class="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white disabled:bg-slate-100 dark:disabled:bg-slate-800 disabled:text-slate-500 dark:disabled:text-slate-400"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.contactPhone') }}
            </label>
            <input
              v-model="formData.contact_phone"
              type="tel"
              :disabled="!isEditing"
              class="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white disabled:bg-slate-100 dark:disabled:bg-slate-800 disabled:text-slate-500 dark:disabled:text-slate-400"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
