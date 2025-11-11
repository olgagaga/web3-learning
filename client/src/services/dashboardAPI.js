import api from './api'

export const dashboardAPI = {
  // Get comprehensive dashboard stats
  getStats: () => api.get('/dashboard/stats'),

  // Get weekly summary
  getWeeklySummary: () => api.get('/dashboard/weekly'),
}

export default dashboardAPI
