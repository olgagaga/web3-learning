import api from './api'

export const writingAPI = {
  getPrompts: (difficulty) => {
    const params = difficulty ? { difficulty } : {}
    return api.get('/writing/prompts', { params })
  },

  getPrompt: (promptId) => api.get(`/writing/prompts/${promptId}`),

  submitEssay: (promptId, content, parentEssayId = null) =>
    api.post('/writing/submit', {
      prompt_id: promptId,
      content,
      parent_essay_id: parentEssayId,
    }),

  getEssays: (limit = 10) => api.get('/writing/essays', { params: { limit } }),

  getEssay: (essayId) => api.get(`/writing/essays/${essayId}`),

  getRevisions: (essayId) => api.get(`/writing/essays/${essayId}/revisions`),

  getStats: () => api.get('/writing/stats'),
}
