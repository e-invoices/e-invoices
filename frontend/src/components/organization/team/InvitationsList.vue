<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { OrganizationRole, InvitationResponse } from '@/types/organization.ts'

defineProps<{
  invitations: InvitationResponse[]
  loading: boolean
}>()

const emit = defineEmits<{
  copy: [invitation: InvitationResponse]
  deactivate: [invitation: InvitationResponse]
}>()

const { t } = useI18n()

// Format date
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Check if invitation is expired
const isExpired = (dateStr: string) => {
  return new Date(dateStr) < new Date()
}

// Get role badge class
const getRoleBadgeClass = (role: OrganizationRole) => {
  const classes: Record<string, string> = {
    owner: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
    admin: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    accountant: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    member: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    viewer: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
  }
  return classes[role] || classes.member
}
</script>

<template>
  <div>
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>

    <div v-else>
      <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">
        {{ t('settings.manageTeam.pendingInvitations') }}
      </h3>

      <!-- Empty State -->
      <div v-if="invitations.length === 0" class="text-center py-12 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
        <svg class="w-12 h-12 mx-auto text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <p class="text-slate-600 dark:text-slate-400">
          {{ t('settings.manageTeam.noInvitations') }}
        </p>
        <p class="text-sm text-slate-500 dark:text-slate-500 mt-1">
          {{ t('settings.manageTeam.noInvitationsDesc') }}
        </p>
      </div>

      <!-- Invitations List -->
      <div v-else class="space-y-3">
        <div
          v-for="invitation in invitations"
          :key="invitation.id"
          :class="[
            'p-4 rounded-xl border transition-all',
            !invitation.is_active || isExpired(invitation.expires_at)
              ? 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 opacity-60'
              : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700'
          ]"
        >
          <div class="flex items-center justify-between flex-wrap gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 mb-2">
                <span class="font-mono text-sm bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">
                  {{ invitation.code }}
                </span>
                <span :class="['text-xs px-2 py-1 rounded-full', getRoleBadgeClass(invitation.role)]">
                  {{ t(`organization.roles.${invitation.role}`) }}
                </span>
                <span v-if="!invitation.is_active" class="text-xs px-2 py-1 rounded-full bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300">
                  {{ t('settings.manageTeam.deactivated') }}
                </span>
                <span v-else-if="isExpired(invitation.expires_at)" class="text-xs px-2 py-1 rounded-full bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300">
                  {{ t('settings.manageTeam.expired') }}
                </span>
              </div>
              <div class="text-sm text-slate-600 dark:text-slate-400 space-y-1">
                <p v-if="invitation.target_email">
                  <span class="text-slate-500">{{ t('settings.manageTeam.sentTo') }}:</span>
                  {{ invitation.target_email }}
                </p>
                <p>
                  <span class="text-slate-500">{{ t('settings.manageTeam.expiresAt') }}:</span>
                  {{ formatDate(invitation.expires_at) }}
                </p>
                <p v-if="invitation.max_uses">
                  <span class="text-slate-500">{{ t('settings.manageTeam.uses') }}:</span>
                  {{ invitation.use_count }} / {{ invitation.max_uses }}
                </p>
              </div>
            </div>

            <div v-if="invitation.is_active && !isExpired(invitation.expires_at)" class="flex gap-2">
              <button
                @click="emit('copy', invitation)"
                class="px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                {{ t('settings.manageTeam.copyLink') }}
              </button>
              <button
                @click="emit('deactivate', invitation)"
                class="px-3 py-2 text-sm text-red-600 dark:text-red-400 border border-red-300 dark:border-red-700 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                {{ t('settings.manageTeam.deactivate') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
