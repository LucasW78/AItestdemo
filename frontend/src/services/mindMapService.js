import api from './api'

export const mindMapService = {
  // Generate mind map
  async generateMindMap(data) {
    return api.post('/mindmaps/generate', data)
  },

  // List mind maps
  async listMindMaps(params = {}) {
    return api.get('/mindmaps', { params })
  },

  // Get mind map by ID
  async getMindMap(mindMapId) {
    return api.get(`/mindmaps/${mindMapId}`)
  },

  // Create mind map
  async createMindMap(data) {
    return api.post('/mindmaps', data)
  },

  // Update mind map
  async updateMindMap(mindMapId, data) {
    return api.put(`/mindmaps/${mindMapId}`, data)
  },

  // Delete mind map
  async deleteMindMap(mindMapId) {
    return api.delete(`/mindmaps/${mindMapId}`)
  },

  // Get generation status
  async getGenerationStatus(taskId) {
    return api.get(`/mindmaps/generation/${taskId}/status`)
  }
}