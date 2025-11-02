import api from './api'

export const documentService = {
  // Upload document
  async uploadDocument(file, onUploadProgress) {
    const formData = new FormData()
    formData.append('file', file)

    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress
    })
  },

  // List documents
  async listDocuments(params = {}) {
    return api.get('/documents', { params })
  },

  // Get document by ID
  async getDocument(documentId) {
    return api.get(`/documents/${documentId}`)
  },

  // Update document
  async updateDocument(documentId, data) {
    return api.put(`/documents/${documentId}`, data)
  },

  // Delete document
  async deleteDocument(documentId) {
    return api.delete(`/documents/${documentId}`)
  },

  // Process document for RAG
  async processDocument(documentId) {
    return api.post(`/documents/${documentId}/process`)
  },

  // Get document processing status
  async getDocumentStatus(documentId) {
    return api.get(`/documents/${documentId}/status`)
  }
}