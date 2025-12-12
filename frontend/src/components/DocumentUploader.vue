<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  label?: string
  hint?: string
  accept?: string
  buttonLabel?: string
  disabled?: boolean
}>()

const emit = defineEmits<{ (event: 'file-selected', file: File): void }>()

const dragActive = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)

const handleFiles = (files: FileList | null) => {
  if (!files || files.length === 0) return
  const file = files[0]
  if (!file) return
  emit('file-selected', file)
}

const onDrop = (event: DragEvent) => {
  event.preventDefault()
  dragActive.value = false
  handleFiles(event.dataTransfer?.files ?? null)
}

const onChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  handleFiles(target.files)
  target.value = ''
}

const onDragOver = (event: DragEvent) => {
  event.preventDefault()
  dragActive.value = true
}

const onDragLeave = () => {
  dragActive.value = false
}

const openFileDialog = () => {
  if (inputRef.value && !props.disabled) {
    inputRef.value.click()
  }
}
</script>

<template>
  <div class="document-uploader">
    <p class="label" v-if="props.label">{{ props.label }}</p>
    <div
      class="drop-zone"
      :class="{ 'drop-zone--active': dragActive }"
      @drop="onDrop"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @click="openFileDialog"
    >
      <input
        ref="inputRef"
        class="file-input"
        type="file"
        :accept="props.accept ?? '.json'"
        @change="onChange"
        :disabled="props.disabled"
      />
      <p class="hint">
        {{ props.hint ?? 'Drop a JSON document or click to browse.' }}
      </p>
      <button
        type="button"
        class="primary"
        :disabled="props.disabled"
      >
        {{ props.buttonLabel ?? 'Select File' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.document-uploader {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label {
  font-weight: 600;
  color: #0f172a;
}

.drop-zone {
  border: 1px solid #cbd5f5;
  border-radius: 0.75rem;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: background-color 0.2s ease;
  background: #f8fafc;
  color: #0f172a;
}

.drop-zone--active {
  background: #eef2ff;
}

.file-input {
  display: none;
}

.primary {
  border: 1px solid #cbd5f5;
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  background: #ffffff;
  color: #0f172a;
  font-weight: 600;
}

.primary:disabled {
  background: #f1f5f9;
  cursor: not-allowed;
}

.hint {
  margin: 0;
  color: #475569;
}
</style>
