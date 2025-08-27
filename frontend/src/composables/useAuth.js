import { ref, computed, watch } from 'vue'
import axios from 'axios'
import { API_CONFIG } from '../config/api.js'

// Global authentication state
const token = ref(localStorage.getItem('auth_token') || null)
const user = ref(JSON.parse(localStorage.getItem('auth_user') || 'null'))
const isLoading = ref(false)

// Create axios instance for auth requests
const authApi = axios.create({
  baseURL: API_CONFIG.API_BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
})

export function useAuth() {
  // Computed properties
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  
  // Watch for token changes and update localStorage
  watch(token, (newToken) => {
    if (newToken) {
      localStorage.setItem('auth_token', newToken)
    } else {
      localStorage.removeItem('auth_token')
    }
  })
  
  // Watch for user changes and update localStorage
  watch(user, (newUser) => {
    if (newUser) {
      localStorage.setItem('auth_user', JSON.stringify(newUser))
    } else {
      localStorage.removeItem('auth_user')
    }
  })
  
  /**
   * Login user with email and password
   */
  const login = async (email, password) => {
    try {
      isLoading.value = true
      
      const response = await authApi.post('/auth/login', {
        email,
        password
      })
      
      const { token: authToken, user: authUser } = response.data
      
      // Set authentication state
      token.value = authToken
      user.value = authUser
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      const message = error.response?.data?.message || 'Login failed'
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Register new user (restricted to specific email)
   */
  const register = async (email, password) => {
    try {
      isLoading.value = true
      
      const response = await authApi.post('/auth/register', {
        email,
        password
      })
      
      const { token: authToken, user: authUser } = response.data
      
      // Set authentication state
      token.value = authToken
      user.value = authUser
      
      return { success: true }
    } catch (error) {
      console.error('Registration error:', error)
      let message = 'Registration failed'
      
      if (error.response?.data?.code === 'REGISTRATION_RESTRICTED') {
        message = 'Registration is currently restricted to authorized users only'
      } else if (error.response?.data?.message) {
        message = error.response.data.message
      }
      
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Logout user
   */
  const logout = () => {
    token.value = null
    user.value = null
    
    // Clear any cached data or state here if needed
    console.log('User logged out successfully')
  }
  
  /**
   * Check if current token is still valid
   */
  const validateToken = async () => {
    if (!token.value) {
      return false
    }
    
    try {
      // Make a test request to a protected endpoint
      const response = await authApi.get('/auth/me', {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })
      
      // Update user data if token is valid
      user.value = response.data.user
      return true
    } catch (error) {
      console.error('Token validation failed:', error)
      // Clear invalid token
      logout()
      return false
    }
  }
  
  /**
   * Get current authentication token
   */
  const getToken = () => token.value
  
  /**
   * Initialize auth state (check for existing valid token)
   */
  const initialize = async () => {
    if (token.value) {
      await validateToken()
    }
  }
  
  return {
    // State
    user: computed(() => user.value),
    isAuthenticated,
    isLoading: computed(() => isLoading.value),
    
    // Actions
    login,
    register,
    logout,
    validateToken,
    getToken,
    initialize
  }
}