import { create } from 'zustand'

// Helper to load from localStorage
const loadAuthFromStorage = () => {
  try {
    const stored = localStorage.getItem('auth-storage')
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (e) {
    console.error('Failed to load auth from storage:', e)
  }
  return { user: null, token: null, isAuthenticated: false }
}

// Helper to save to localStorage
const saveAuthToStorage = (state) => {
  try {
    localStorage.setItem('auth-storage', JSON.stringify({
      user: state.user,
      token: state.token,
      isAuthenticated: state.isAuthenticated,
    }))
  } catch (e) {
    console.error('Failed to save auth to storage:', e)
  }
}

export const useAuthStore = create((set) => ({
  ...loadAuthFromStorage(),

  login: (user, token) => {
    const newState = { user, token, isAuthenticated: true }
    set(newState)
    saveAuthToStorage(newState)
  },

  logout: () => {
    const newState = { user: null, token: null, isAuthenticated: false }
    set(newState)
    saveAuthToStorage(newState)
  },

  updateUser: (user) => {
    set((state) => {
      const newState = { ...state, user }
      saveAuthToStorage(newState)
      return { user }
    })
  },
}))
