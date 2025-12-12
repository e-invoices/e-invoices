export interface UploadResponse {
  id: string
  filename: string
  processedAt: string
  previewJson: Record<string, unknown>
  previewXml: string
}

