import api from './api'

export const questsAPI = {
  // Get all active quests
  getAllQuests: () => api.get('/quests/'),

  // Get user's quests
  getMyQuests: () => api.get('/quests/my-quests'),

  // Get active quests
  getActiveQuests: () => api.get('/quests/active'),

  // Accept a quest
  acceptQuest: (questId) => api.post('/quests/accept', { quest_id: questId }),

  // Get quest statistics
  getStats: () => api.get('/quests/stats'),

  // Get user badges
  getBadges: () => api.get('/quests/badges'),

  // Get all available badges
  getAllBadges: () => api.get('/quests/badges/all'),

  // Get badge showcase
  getBadgeShowcase: () => api.get('/quests/badges/showcase'),

  // Get badge progress
  getBadgeProgress: (badgeId) => api.get(`/quests/badges/${badgeId}/progress`),

  // Get all badges progress
  getAllBadgesProgress: () => api.get('/quests/badges/progress/all'),
}

export default questsAPI
