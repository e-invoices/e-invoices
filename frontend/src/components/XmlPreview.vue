<script setup lang="ts">
const props = defineProps<{
  title: string
  content: string
  description?: string
  height?: string
}>()
</script>

<template>
  <article class="xml-preview" role="region" :aria-label="props.title">
    <header class="preview-header">
      <h2>{{ props.title }}</h2>
      <p v-if="props.description">{{ props.description }}</p>
    </header>
    <pre class="preview-body" :style="{ minHeight: props.height ?? '220px' }">
      <code>{{ props.content }}</code>
    </pre>
  </article>
</template>

<style scoped>
.xml-preview {
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 1rem;
  background: #ffffff;
  color: #0f172a;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

.preview-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.preview-header p {
  margin: 0.25rem 0 0;
  color: #475569;
}

.preview-body {
  margin: 0.75rem 0 0;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.875rem;
}
</style>
