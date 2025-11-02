import api from './api'

export const testCaseService = {
  // Generate test cases
  async generateTestCases(data) {
    return api.post('/testcases/generate', data)
  },

  // List test cases
  async listTestCases(params = {}) {
    return api.get('/testcases', { params })
  },

  // Get test case by ID
  async getTestCase(testCaseId) {
    return api.get(`/testcases/${testCaseId}`)
  },

  // Create test case
  async createTestCase(data) {
    return api.post('/testcases', data)
  },

  // Update test case
  async updateTestCase(testCaseId, data) {
    return api.put(`/testcases/${testCaseId}`, data)
  },

  // Delete test case
  async deleteTestCase(testCaseId) {
    return api.delete(`/testcases/${testCaseId}`)
  },

  // Get generation status
  async getGenerationStatus(taskId) {
    return api.get(`/testcases/generation/${taskId}/status`)
  }
}