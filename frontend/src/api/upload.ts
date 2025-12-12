import type { UploadResponse } from '@/types/upload'
import { API_BASE } from './client'

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const form = new FormData()
  form.append('file', file)

  const response = await fetch(`${API_BASE}/uploads`, {
    method: 'POST',
    body: form,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || 'Upload failed')
  }

  return response.json()
}
