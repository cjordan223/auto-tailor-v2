import axios from 'axios'
import { globalSettings } from './useSettings.js'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5 minutes for processing
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    
    // Handle rate limit errors specifically
    if (error.response?.status === 429) {
      const retryAfter = error.response?.headers['retry-after'] || 60
      error.message = `Rate limit exceeded. Please wait ${retryAfter} seconds before trying again.`
    }
    
    return Promise.reject(error)
  }
)

// Rate limiting state
const lastRequestTime = new Map()
const MIN_REQUEST_INTERVAL = 5000 // 5 seconds between requests

export function useAPI() {
  
  /**
   * Check if enough time has passed since the last request for rate limiting
   */
  const checkRateLimit = (endpoint) => {
    const now = Date.now()
    const lastTime = lastRequestTime.get(endpoint) || 0
    const timeSinceLastRequest = now - lastTime
    
    if (timeSinceLastRequest < MIN_REQUEST_INTERVAL) {
      const waitTime = MIN_REQUEST_INTERVAL - timeSinceLastRequest
      throw new Error(`Rate limit: Please wait ${Math.ceil(waitTime / 1000)} seconds before making another request`)
    }
    
    lastRequestTime.set(endpoint, now)
  }
  
  /**
   * Upload a file to the server
   */
  const uploadFile = async (file, type) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('type', type)
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    return response.data
  }

  /**
   * Process resume with AI
   */
  const processResume = async ({ jobDescription, provider, model, personality }) => {
    try {
      // Check rate limiting before making the request
      checkRateLimit('process')
      const formData = new FormData()
      
      // Add job description (file or text)
      if (typeof jobDescription === 'string') {
        formData.append('jobDescriptionText', jobDescription)
      } else if (jobDescription) {
        formData.append('jobDescription', jobDescription)
      }
      
      // Add configuration
      formData.append('provider', provider)
      formData.append('model', model)
      formData.append('personality', personality)
      
      // Add API keys from settings
      const apiKeys = globalSettings.getAllApiKeys()
      formData.append('apiKeys', JSON.stringify(apiKeys))
      
      const response = await api.post('/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to process resume')
    }
  }

  /**
   * Check processing status
   */
  const checkStatus = async (jobId) => {
    try {
      const response = await api.get(`/status/${jobId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to check status')
    }
  }

  /**
   * Download generated files
   */
  const downloadFile = async (jobId, fileType) => {
    try {
      const response = await api.get(`/download/${jobId}/${fileType}`, {
        responseType: 'blob'
      })
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      // Get filename from response headers
      const contentDisposition = response.headers['content-disposition']
      let filename = `${fileType}.pdf`
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }
      
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      return { success: true, filename }
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to download file')
    }
  }

  /**
   * Download all files as a zip archive
   */
  const downloadAllAsZip = async (jobId) => {
    try {
      const response = await api.get(`/download/${jobId}/zip/all`, {
        responseType: 'blob'
      })
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      // Get filename from response headers
      const contentDisposition = response.headers['content-disposition']
      let filename = `tex-tailor-results-${jobId}.zip`
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }
      
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      return { success: true, filename }
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to download zip file')
    }
  }

  /**
   * Add skill to baseline skills JSON file
   */
  const addSkillToBaseline = async (jobId, skill, category = 'conversational_skills') => {
    try {
      const response = await api.post(`/results/${jobId}/add-skill`, {
        skill,
        category
      })
      
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to add skill to baseline')
    }
  }

  /**
   * Get PDF URL for viewing inline (no download)
   */
  const getPDFViewUrl = (jobId, fileType) => {
    return `/api/view/${jobId}/${fileType}`
  }

  /**
   * Get available providers and models
   */
  const getProviders = async () => {
    try {
      const response = await api.get('/providers')
      return response.data
    } catch (error) {
      console.error('Failed to fetch providers:', error)
      // Return default providers if API fails
      return {
        providers: [
          {
            id: 'gemini',
            name: 'Google Gemini',
            available: false,
            models: ['gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-flash', 'gemini-1.5-pro-latest']
          },
          {
            id: 'openai', 
            name: 'OpenAI',
            available: false,
            models: ['gpt-4o-mini', 'gpt-4o']
          },
          {
            id: 'ollama',
            name: 'Ollama (Local)',
            available: false,
            models: ['qwen2.5:14b-instruct', 'llama3:8b', 'phi3:mini', 'llama3.1:70b']
          }
        ]
      }
    }
  }

  /**
   * Get job results
   */
  const getResults = async (jobId) => {
    try {
      const response = await api.get(`/results/${jobId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to get results')
    }
  }

  /**
   * Get processing history
   */
  const getHistory = async () => {
    try {
      const response = await api.get('/history')
      return response.data
    } catch (error) {
      console.error('Failed to fetch history:', error)
      return { jobs: [] }
    }
  }

  /**
   * Validate API key for a specific provider
   */
  const validateApiKey = async (provider, apiKey, ollamaUrl = null) => {
    try {
      const response = await api.post('/validate', {
        provider,
        apiKey,
        ollamaUrl
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to validate API key')
    }
  }

  return {
    uploadFile,
    processResume,
    checkStatus,
    downloadFile,
    downloadAllAsZip,
    addSkillToBaseline,
    getPDFViewUrl,
    getProviders,
    getResults,
    getHistory,
    validateApiKey
  }
}