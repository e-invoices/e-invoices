<script setup lang="ts">
import { ref } from 'vue'
import DocumentUploader from '@/components/DocumentUploader.vue'
import { uploadDocument } from '@/api/upload'

const uploadResult = ref<string>('')
const error = ref<string | null>(null)
const loading = ref(false)

const handleFile = async (file: File) => {
  loading.value = true
  error.value = null
  try {
    const payload = await uploadDocument(file)
    uploadResult.value = JSON.stringify(payload, null, 2)
    sessionStorage.setItem('latestUpload', JSON.stringify(payload))
  } catch (err) {
    error.value = (err instanceof Error && err.message) || 'Unable to upload document.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="upload-page">
    <header>
      <p class="eyebrow">Step 1</p>
      <h1>Upload JSON document</h1>
      <p class="lead">Drop a `.json` file or browse to select one. A preview is automatically stored for the next step.</p>
    </header>

    <DocumentUploader
      label="Upload a document"
      hint="JSON sanitized for invoice preview"
      button-label="Upload"
      :disabled="loading"
      @file-selected="handleFile"
    />

    <div class="status" v-if="loading">Uploading…</div>
    <p class="error" v-if="error">{{ error }}</p>
    <article class="result" v-if="uploadResult">
      <h2>Upload payload</h2>
      <pre>{{ uploadResult }}</pre>
    </article>
  </section>
</template>

<style scoped>
.upload-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 840px;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-size: 0.75rem;
  color: #475569;
}

.lead {
  margin: 0.35rem 0 0;
  color: #475569;
}

.status {
  font-weight: 600;
  color: #475569;
}

.error {
  color: #b91c1c;
}

.result {
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1rem;
  background: #ffffff;
  color: #0f172a;
}

.result pre {
  margin: 0.5rem 0 0;
  max-height: 320px;
  overflow: auto;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}
</style>
