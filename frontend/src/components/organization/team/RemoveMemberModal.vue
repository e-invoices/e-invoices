<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TeamMember } from '@/types/organization.ts'

const props = defineProps<{
  show: boolean
  member: TeamMember | null
  loading: boolean
  error: string
}>()

const emit = defineEmits<{
  close: []
  confirm: []
}>()

const { t } = useI18n()

const memberName = computed(() => props.member?.full_name ?? '')
</script>

<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <!-- Backdrop -->
      <div
        class="absolute inset-0 bg-black/50"
        @click="emit('close')"
      ></div>

      <!-- Modal Content -->
      <div class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-xl max-w-md w-full p-6">
        <h3 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
          {{ t('settings.manageTeam.confirmRemove') }}
        </h3>

        <p class="text-slate-600 dark:text-slate-400 mb-6">
          {{ t('settings.manageTeam.confirmRemoveMessage', { name: memberName }) }}
        </p>

        <!-- Error -->
        <div v-if="error" class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300 text-sm">
          {{ error }}
        </div>

        <div class="flex gap-2">
          <button
            @click="emit('close')"
            class="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors font-medium"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            @click="emit('confirm')"
            :disabled="loading"
            class="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium disabled:opacity-50"
          >
            {{ loading ? t('common.loading') : t('settings.manageTeam.remove') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
