<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { OrganizationRole, TeamMember } from '@/types/organization.ts'

defineProps<{
  member: TeamMember
  isCurrentUser: boolean
  canChangeRole: boolean
  canRemove: boolean
}>()

const emit = defineEmits<{
  changeRole: [member: TeamMember]
  remove: [member: TeamMember]
}>()

const { t } = useI18n()

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

// Format joined date
const formatJoinedDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>

<template>
  <div
    :class="[
      'p-4 rounded-xl border flex items-center justify-between gap-4',
      isCurrentUser
        ? 'border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20'
        : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800'
    ]"
  >
    <div class="flex items-center gap-4 min-w-0">
      <!-- Avatar -->
      <img
        v-if="member.picture_url"
        :src="member.picture_url"
        :alt="member.full_name"
        class="w-10 h-10 rounded-full object-cover flex-shrink-0"
      />
      <div
        v-else
        class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium flex-shrink-0"
      >
        {{ member.full_name.charAt(0).toUpperCase() }}
      </div>

      <!-- Info -->
      <div class="min-w-0">
        <div class="flex items-center gap-2 flex-wrap">
          <span class="font-medium text-slate-900 dark:text-white truncate">
            {{ member.full_name }}
          </span>
          <span
            v-if="isCurrentUser"
            class="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-200"
          >
            {{ t('settings.manageTeam.thatsYou') }}
          </span>
          <span :class="['text-xs px-2 py-0.5 rounded-full', getRoleBadgeClass(member.role)]">
            {{ t(`organization.roles.${member.role}`) }}
          </span>
        </div>
        <p class="text-sm text-slate-500 dark:text-slate-400 truncate">
          {{ member.email }}
        </p>
        <p class="text-xs text-slate-400 dark:text-slate-500">
          {{ t('settings.manageTeam.joinedOn') }} {{ formatJoinedDate(member.joined_at) }}
        </p>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-2 flex-shrink-0">
      <!-- Change Role Button -->
      <button
        v-if="canChangeRole"
        @click="emit('changeRole', member)"
        class="px-3 py-2 text-sm text-blue-600 dark:text-blue-400 border border-blue-300 dark:border-blue-700 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
      >
        {{ t('settings.manageTeam.changeRole') }}
      </button>
      <!-- Remove Button -->
      <button
        v-if="canRemove"
        @click="emit('remove', member)"
        class="px-3 py-2 text-sm text-red-600 dark:text-red-400 border border-red-300 dark:border-red-700 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
      >
        {{ t('settings.manageTeam.remove') }}
      </button>
    </div>
  </div>
</template>
