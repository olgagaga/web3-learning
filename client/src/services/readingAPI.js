import api from './api'

export const readingAPI = {
  getNextItem: (difficulty) => {
    const params = difficulty ? { difficulty } : {}
    return api.get('/reading/next', { params })
  },

  getItems: (difficulty) => {
    const params = difficulty ? { difficulty } : {}
    return api.get('/reading/items', { params })
  },

  getItem: (itemId) => api.get(`/reading/items/${itemId}`),

  submitAnswer: (questionId, userAnswer, timeSpentSeconds) =>
    api.post('/reading/submit', {
      question_id: questionId,
      user_answer: userAnswer,
      time_spent_seconds: timeSpentSeconds,
    }),

  getStats: () => api.get('/reading/stats'),
}
