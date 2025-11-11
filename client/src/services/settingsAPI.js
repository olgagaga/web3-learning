import api from './api'

export const settingsAPI = {
  // Profile
  updateProfile: (data) => api.put('/settings/profile', data),

  // Password
  changePassword: (data) => api.post('/settings/password', data),

  // Preferences
  getPreferences: () => api.get('/settings/preferences'),
  updatePreferences: (data) => api.put('/settings/preferences', data),

  // Account
  exportData: () => api.get('/settings/export'),
  deleteAccount: () => api.delete('/settings/account'),
}

export default settingsAPI
