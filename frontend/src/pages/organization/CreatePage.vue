<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { organizationApi, type OrganizationCreate } from '@/api/v1/organization.ts'
import { authApi } from '@/api/v1/auth.ts'
import { useAuth } from '@/composables/useAuth'

const { t } = useI18n()
const router = useRouter()
const { currentUser, checkSession } = useAuth()

const loading = ref(false)
const error = ref('')
const resendingVerification = ref(false)
const verificationEmailSent = ref(false)

// Check if user is verified
const isUserVerified = computed(() => currentUser.value?.is_verified ?? false)

// Resend verification email
const resendVerificationEmail = async () => {
  resendingVerification.value = true
  try {
    await authApi.resendVerification()
    verificationEmailSent.value = true
  } catch (err) {
    console.error('Failed to resend verification email:', err)
  } finally {
    resendingVerification.value = false
  }
}

onMounted(async () => {
  // Refresh user data to get latest verification status
  await checkSession()
})

const form = ref<OrganizationCreate>({
  company_name: '',
  registration_name: '',
  edb: '',
  embs: '',
  vat_registered: true,
  address: '',
  contact_person: '',
  contact_email: '',
  contact_phone: '',
})

// Field errors state
const fieldErrors = reactive<Record<string, string>>({
  company_name: '',
  registration_name: '',
  edb: '',
  embs: '',
  address: '',
  contact_person: '',
  contact_email: '',
  contact_phone: '',
})

// Track which fields have been validated (for animation)
const fieldTouched = reactive<Record<string, boolean>>({
  company_name: false,
  registration_name: false,
  edb: false,
  embs: false,
  address: false,
  contact_person: false,
  contact_email: false,
  contact_phone: false,
})

// Validate a single field
const validateField = (fieldName: string): boolean => {
  fieldTouched[fieldName] = true

  switch (fieldName) {
    case 'company_name':
      if (!form.value.company_name.trim()) {
        fieldErrors.company_name = 'companyNameRequired'
        return false
      }
      fieldErrors.company_name = ''
      return true

    case 'registration_name':
      if (!form.value.registration_name.trim()) {
        fieldErrors.registration_name = 'registrationNameRequired'
        return false
      }
      fieldErrors.registration_name = ''
      return true

    case 'edb':
      if (!form.value.edb.trim()) {
        fieldErrors.edb = 'edbRequired'
        return false
      }
      if (!/^\d{13}$/.test(form.value.edb)) {
        fieldErrors.edb = 'edbInvalid'
        return false
      }
      fieldErrors.edb = ''
      return true

    case 'embs':
      if (!form.value.embs.trim()) {
        fieldErrors.embs = 'embsRequired'
        return false
      }
      fieldErrors.embs = ''
      return true

    case 'address':
      if (!form.value.address.trim()) {
        fieldErrors.address = 'addressRequired'
        return false
      }
      fieldErrors.address = ''
      return true

    case 'contact_person':
      if (!form.value.contact_person.trim()) {
        fieldErrors.contact_person = 'contactPersonRequired'
        return false
      }
      fieldErrors.contact_person = ''
      return true

    case 'contact_email':
      if (!form.value.contact_email.trim()) {
        fieldErrors.contact_email = 'contactEmailRequired'
        return false
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.contact_email)) {
        fieldErrors.contact_email = 'contactEmailInvalid'
        return false
      }
      fieldErrors.contact_email = ''
      return true

    case 'contact_phone':
      if (!form.value.contact_phone.trim()) {
        fieldErrors.contact_phone = 'contactPhoneRequired'
        return false
      }
      fieldErrors.contact_phone = ''
      return true

    default:
      return true
  }
}

// Get translated error message
const getFieldError = (fieldName: string): string => {
  const errorKey = fieldErrors[fieldName]
  if (!errorKey) return ''
  return t(`organization.create.errors.${errorKey}`)
}

// Validate all fields
const validateAllFields = (): boolean => {
  const fields = ['company_name', 'registration_name', 'edb', 'embs', 'address', 'contact_person', 'contact_email', 'contact_phone']
  let isValid = true

  for (const field of fields) {
    if (!validateField(field)) {
      isValid = false
    }
  }

  return isValid
}

// Get input class based on error state
const getInputClass = (fieldName: string): string => {
  const baseClass = 'w-full px-4 py-3 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-300'

  if (fieldErrors[fieldName] && fieldTouched[fieldName]) {
    return `${baseClass} border-2 border-red-500 focus:ring-red-500 animate-shake`
  }

  return `${baseClass} border border-slate-300 dark:border-slate-600 focus:ring-blue-500`
}

const handleSubmit = async () => {
  error.value = ''

  // Validate all fields
  if (!validateAllFields()) {
    // Scroll to first error
    const firstErrorField = document.querySelector('.border-red-500')
    if (firstErrorField) {
      firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
    return
  }

  try {
    loading.value = true

    const organization = await organizationApi.createOrganization(form.value)

    // Switch to the new organization to get token with org context
    const switchResponse = await authApi.switchOrganization({ organization_id: organization.id })

    // Store new tokens and org ID
    localStorage.setItem('access_token', switchResponse.access_token)
    localStorage.setItem('refresh_token', switchResponse.refresh_token)
    localStorage.setItem('selected_organization_id', organization.id.toString())

    await router.push('/organization/overview')
  } catch (err) {
    error.value = (err as Error).message || t('organization.create.createFailed')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/organization')
}
</script>

<template>
  <div class="bg-gray-50 dark:bg-slate-950">
    <!-- Main Content -->
    <main class="max-w-3xl mx-auto px-4 py-8 sm:py-12">
      <!-- Back Button -->
      <button
        @click="goBack"
        class="mb-6 flex items-center gap-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span>{{ t('common.back') }}</span>
      </button>

      <!-- Email Verification Warning -->
      <div v-if="!isUserVerified" class="mb-6 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-2xl p-6">
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 bg-amber-100 dark:bg-amber-900/50 rounded-xl flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-amber-800 dark:text-amber-200 mb-1">
              {{ t('organization.create.verificationRequired') }}
            </h3>
            <p class="text-amber-700 dark:text-amber-300 mb-4">
              {{ t('organization.create.verificationMessage') }}
            </p>
            <div v-if="verificationEmailSent" class="mb-3 p-3 bg-green-100 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg">
              <p class="text-green-700 dark:text-green-300 text-sm">
                {{ t('organization.create.verificationEmailSent') }}
              </p>
            </div>
            <button
              type="button"
              @click="resendVerificationEmail"
              :disabled="resendingVerification || verificationEmailSent"
              class="px-4 py-2 bg-amber-600 hover:bg-amber-700 disabled:bg-amber-400 text-white font-medium rounded-lg transition-colors"
            >
              <span v-if="resendingVerification">{{ t('common.loading') }}</span>
              <span v-else-if="verificationEmailSent">{{ t('organization.create.emailSent') }}</span>
              <span v-else>{{ t('organization.create.resendEmail') }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Hero Section -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-lg p-6 sm:p-8 mb-6">
        <div class="flex items-start gap-4 mb-6">
          <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-xl flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-blue-600 dark:text-blue-400 font-medium mb-1">
              {{ t('organization.create.eyebrow') }}
            </p>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
              {{ t('organization.create.title') }}
            </h1>
            <p class="text-slate-600 dark:text-slate-400">
              {{ t('organization.create.subtitle') }}
            </p>
          </div>
        </div>

        <!-- Info Box -->
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 flex items-start gap-3">
          <svg class="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="text-sm">
            <p class="font-medium text-slate-900 dark:text-white mb-1">{{ t('organization.create.infoTitle') }}</p>
            <ul class="text-slate-600 dark:text-slate-400 space-y-1">
              <li>• {{ t('organization.create.infoItem1') }}</li>
              <li>• {{ t('organization.create.infoItem2') }}</li>
              <li>• {{ t('organization.create.infoItem3') }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="bg-white dark:bg-slate-800 rounded-2xl shadow-lg p-6 sm:p-8">
        <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-6">
          {{ t('organization.create.formTitle') }}
        </h2>

        <!-- Error Message -->
        <div v-if="error" class="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-lg mb-6">
          {{ error }}
        </div>

        <div class="space-y-5">
          <!-- Company Name -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.companyName') }} *
            </label>
            <input
              v-model="form.company_name"
              @blur="validateField('company_name')"
              type="text"
              :placeholder="t('organization.create.companyNamePlaceholder')"
              :class="getInputClass('company_name')"
            />
            <p v-if="fieldErrors.company_name" class="mt-1 text-sm text-red-500 dark:text-red-400 transition-opacity duration-300">
              {{ getFieldError('company_name') }}
            </p>
          </div>

          <!-- Registration Name -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.registrationName') }} *
            </label>
            <input
              v-model="form.registration_name"
              @blur="validateField('registration_name')"
              type="text"
              :placeholder="t('organization.create.registrationNamePlaceholder')"
              :class="getInputClass('registration_name')"
            />
            <p v-if="fieldErrors.registration_name" class="mt-1 text-sm text-red-500 dark:text-red-400 transition-opacity duration-300">
              {{ getFieldError('registration_name') }}
            </p>
          </div>

          <!-- EDB and EMBS -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                {{ t('organization.create.edb') }} *
              </label>
              <input
                v-model="form.edb"
                @blur="validateField('edb')"
                type="text"
                maxlength="13"
                :placeholder="t('organization.create.edbPlaceholder')"
                :class="getInputClass('edb')"
              />
              <p v-if="fieldErrors.edb" class="mt-1 text-sm text-red-500 dark:text-red-400 transition-opacity duration-300">
                {{ getFieldError('edb') }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                {{ t('organization.create.embs') }} *
              </label>
              <input
                v-model="form.embs"
                @blur="validateField('embs')"
                type="text"
                :placeholder="t('organization.create.embsPlaceholder')"
                :class="getInputClass('embs')"
              />
              <p v-if="fieldErrors.embs" class="mt-1 text-sm text-red-500 dark:text-red-400 transition-opacity duration-300">
                {{ getFieldError('embs') }}
              </p>
            </div>
          </div>

          <!-- VAT Registered -->
          <div class="flex items-center gap-3">
            <input
              v-model="form.vat_registered"
              type="checkbox"
              id="vatRegistered"
              class="w-5 h-5 text-blue-600 border-slate-300 dark:border-slate-600 rounded focus:ring-blue-500"
            />
            <label for="vatRegistered" class="text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('organization.create.vatRegistered') }}
            </label>
          </div>

          <!-- Address -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.address') }} *
            </label>
            <textarea
              v-model="form.address"
              @blur="validateField('address')"
              rows="2"
              :placeholder="t('organization.create.addressPlaceholder')"
              :class="getInputClass('address') + ' resize-none'"
            ></textarea>
            <p v-if="fieldErrors.address" class="mt-1 text-sm text-red-500 dark:text-red-400 transition-opacity duration-300">
              {{ getFieldError('address') }}
            </p>
          </div>

          <!-- Contact Person -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ t('organization.create.contactPerson') }} *
            </label>
            <input
              v-model="form.contact_person"
              @blur="validateField('contact_person')"
              type="text"
              :placeholder="t('organization.create.contactPersonPlaceholder')"
              :class="getInputClass('contact_person')"
            />
            <p v-if="fieldErrors.contact_person" class="mt-1 text-sm text-red-500 dark:text-red-400 transition-opacity duration-300">
              {{ getFieldError('contact_person') }}
            </p>
          </div>

          <!-- Contact Email and Phone -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                {{ t('organization.create.contactEmail') }} *
              </label>
              <input
                v-model="form.contact_email"
                @blur="validateField('contact_email')"
                type="email"
                :placeholder="t('organization.create.contactEmailPlaceholder')"
                :class="getInputClass('contact_email')"
              />
              <p v-if="fieldErrors.contact_email" class="mt-1 text-sm text-red-500 dark:text-red-400 transition-opacity duration-300">
                {{ getFieldError('contact_email') }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                {{ t('organization.create.contactPhone') }} *
              </label>
              <input
                v-model="form.contact_phone"
                @blur="validateField('contact_phone')"
                type="tel"
                :placeholder="t('organization.create.contactPhonePlaceholder')"
                :class="getInputClass('contact_phone')"
              />
              <p v-if="fieldErrors.contact_phone" class="mt-1 text-sm text-red-500 dark:text-red-400 transition-opacity duration-300">
                {{ getFieldError('contact_phone') }}
              </p>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="mt-8 flex flex-col sm:flex-row gap-3">
          <button
            type="button"
            @click="goBack"
            class="px-6 py-3 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 font-medium rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            type="submit"
            :disabled="loading || !isUserVerified"
            class="flex-1 py-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg shadow-lg shadow-blue-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ t('organization.create.creating') }}
            </span>
            <span v-else>{{ t('organization.create.createButton') }}</span>
          </button>
        </div>
      </form>

      <!-- Next Steps Info -->
      <div class="mt-6 bg-slate-100 dark:bg-slate-800/50 rounded-xl p-4 sm:p-5">
        <h3 class="font-medium text-slate-900 dark:text-white mb-2">
          {{ t('organization.create.nextStepsTitle') }}
        </h3>
        <ol class="text-sm text-slate-600 dark:text-slate-400 space-y-1.5 list-decimal list-inside">
          <li>{{ t('organization.create.nextStep1') }}</li>
          <li>{{ t('organization.create.nextStep2') }}</li>
          <li>{{ t('organization.create.nextStep3') }}</li>
        </ol>
      </div>
    </main>
  </div>
</template>

<style scoped>
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
  20%, 40%, 60%, 80% { transform: translateX(4px); }
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}
</style>
