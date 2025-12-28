import { ref, reactive, computed, watch, readonly } from 'vue'

// Global state for settings
const settings = reactive({
  apiKeys: {
    gemini: '',
    openai: '',
    mistral: '',
    groq: ''
  },
  ollamaUrl: 'http://192.168.1.22:11434',
  defaultProvider: 'ollama',
  autoDownload: false,
  pdfViewerType: 'pdfjs'
})

const isLoaded = ref(false)

export function useSettings() {
  // Load settings from localStorage on first use
  const loadSettings = () => {
    if (isLoaded.value) return settings
    
    try {
      const saved = localStorage.getItem('tex-tailor-settings')
      if (saved) {
        const parsed = JSON.parse(saved)
        
        // Merge with defaults to handle missing keys
        Object.assign(settings, {
          apiKeys: {
            gemini: parsed.apiKeys?.gemini || '',
            openai: parsed.apiKeys?.openai || '',
            mistral: parsed.apiKeys?.mistral || '',
            groq: parsed.apiKeys?.groq || ''
          },
          ollamaUrl: parsed.ollamaUrl || 'http://192.168.1.22:11434',
          defaultProvider: parsed.defaultProvider || 'ollama',
          autoDownload: parsed.autoDownload || false,
          pdfViewerType: parsed.pdfViewerType || 'pdfjs'
        })
      }
      isLoaded.value = true
    } catch (error) {
      console.error('Failed to load settings from localStorage:', error)
      isLoaded.value = true // Still mark as loaded to prevent retry loops
    }
    
    return settings
  }

  // Save settings to localStorage
  const saveSettings = () => {
    try {
      const toSave = {
        apiKeys: settings.apiKeys,
        ollamaUrl: settings.ollamaUrl,
        defaultProvider: settings.defaultProvider,
        autoDownload: settings.autoDownload,
        pdfViewerType: settings.pdfViewerType
      }
      localStorage.setItem('tex-tailor-settings', JSON.stringify(toSave))
      return true
    } catch (error) {
      console.error('Failed to save settings to localStorage:', error)
      return false
    }
  }

  // Auto-save when settings change
  watch(settings, () => {
    if (isLoaded.value) {
      saveSettings()
    }
  }, { deep: true })

  // Get API key for a specific provider
  const getApiKey = (provider) => {
    loadSettings()
    return settings.apiKeys[provider] || ''
  }

  // Set API key for a specific provider
  const setApiKey = (provider, key) => {
    loadSettings()
    settings.apiKeys[provider] = key
  }

  // Check if a provider has an API key
  const hasApiKey = (provider) => {
    const key = getApiKey(provider)
    return key && key.trim().length > 0
  }

  // Get all API keys (for sending to backend)
  const getAllApiKeys = () => {
    loadSettings()
    return {
      GEMINI_API_KEY: settings.apiKeys.gemini,
      OPENAI_API_KEY: settings.apiKeys.openai,
      MISTRAL_API_KEY: settings.apiKeys.mistral,
      GROQ_API_KEY: settings.apiKeys.groq,
      OLLAMA_BASE_URL: settings.ollamaUrl
    }
  }

  // Clear all settings
  const clearSettings = () => {
    try {
      localStorage.removeItem('tex-tailor-settings')
      
      // Reset to defaults
      Object.assign(settings, {
        apiKeys: { gemini: '', openai: '', mistral: '', groq: '' },
        ollamaUrl: 'http://192.168.1.22:11434',
        defaultProvider: 'ollama',
        autoDownload: false
      })
      
      return true
    } catch (error) {
      console.error('Failed to clear settings:', error)
      return false
    }
  }

  // Computed properties
  const availableProviders = computed(() => {
    loadSettings()
    return [
      {
        id: 'gemini',
        name: 'Google Gemini',
        hasKey: hasApiKey('gemini'),
        isDefault: settings.defaultProvider === 'gemini'
      },
      {
        id: 'openai',
        name: 'OpenAI',
        hasKey: hasApiKey('openai'),
        isDefault: settings.defaultProvider === 'openai'
      },
      {
        id: 'mistral',
        name: 'Mistral',
        hasKey: hasApiKey('mistral'),
        isDefault: settings.defaultProvider === 'mistral'
      },
      {
        id: 'groq',
        name: 'Groq',
        hasKey: hasApiKey('groq'),
        isDefault: settings.defaultProvider === 'groq'
      },
      {
        id: 'ollama',
        name: 'Ollama (Local)',
        hasKey: true, // Always available if running
        isDefault: settings.defaultProvider === 'ollama'
      }
    ]
  })

  // Initialize settings on first call
  loadSettings()

  return {
    settings: readonly(settings),
    loadSettings,
    saveSettings,
    getApiKey,
    setApiKey,
    hasApiKey,
    getAllApiKeys,
    clearSettings,
    availableProviders
  }
}

// Export a singleton instance for global use
const settingsInstance = useSettings()
export const globalSettings = settingsInstance
