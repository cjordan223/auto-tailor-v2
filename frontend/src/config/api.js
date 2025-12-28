// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || window.location.origin,
  // Always use relative path for API since backend serves the frontend
  API_BASE_URL: '/api',
  TIMEOUT: 300000 // 5 minutes
}

// Helper functions
export const getApiUrl = (endpoint) => {
  return `${API_CONFIG.API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`
}

export const getFullUrl = (path) => {
  return `${API_CONFIG.BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}