<template>
  <div class="max-w-4xl mx-auto space-y-8">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
      <p class="text-gray-600">Configure AI providers and application preferences.</p>
    </div>

    <!-- Provider Configuration -->
    <div class="card">
      <h2 class="text-xl font-semibold text-gray-900 mb-6">AI Provider Configuration</h2>

      <div class="space-y-6">
        <!-- Gemini Settings -->
        <div class="border border-gray-200 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <span class="text-2xl">🧠</span>
              <div>
                <h3 class="font-medium text-gray-900">Google Gemini</h3>
                <p class="text-sm text-gray-600">Fast and efficient AI processing</p>
              </div>
            </div>
            <div class="flex items-center">
              <span :class="geminiStatus.available ? 'text-success-600' : 'text-error-600'" class="text-sm font-medium">
                {{ geminiStatus.available ? '✓ Available' : '✗ Not Available' }}
              </span>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <div class="flex space-x-2">
                <input v-model="apiKeys.gemini" :type="showApiKeys.gemini ? 'text' : 'password'"
                  class="flex-1 p-3 border border-gray-300 rounded-lg focus-ring"
                  placeholder="Enter your Gemini API key" />
                <button @click="toggleApiKeyVisibility('gemini')" class="btn btn-secondary">
                  {{ showApiKeys.gemini ? '🙈' : '👁️' }}
                </button>
                <button @click="testApiKey('gemini')" :disabled="!apiKeys.gemini || validating.gemini"
                  class="btn btn-primary">
                  {{ validating.gemini ? '⏳' : '🧪' }}
                </button>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank"
                  class="text-primary-600 hover:underline">Google AI Studio</a>
              </p>
            </div>
          </div>
        </div>

        <!-- OpenAI Settings -->
        <div class="border border-gray-200 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <span class="text-2xl">🤖</span>
              <div>
                <h3 class="font-medium text-gray-900">OpenAI</h3>
                <p class="text-sm text-gray-600">High-quality AI processing</p>
              </div>
            </div>
            <div class="flex items-center">
              <span :class="openaiStatus.available ? 'text-success-600' : 'text-error-600'" class="text-sm font-medium">
                {{ openaiStatus.available ? '✓ Available' : '✗ Not Available' }}
              </span>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <div class="flex space-x-2">
                <input v-model="apiKeys.openai" :type="showApiKeys.openai ? 'text' : 'password'"
                  class="flex-1 p-3 border border-gray-300 rounded-lg focus-ring"
                  placeholder="Enter your OpenAI API key" />
                <button @click="toggleApiKeyVisibility('openai')" class="btn btn-secondary">
                  {{ showApiKeys.openai ? '🙈' : '👁️' }}
                </button>
                <button @click="testApiKey('openai')" :disabled="!apiKeys.openai || validating.openai"
                  class="btn btn-primary">
                  {{ validating.openai ? '⏳' : '🧪' }}
                </button>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank"
                  class="text-primary-600 hover:underline">OpenAI Platform</a>
              </p>
            </div>
          </div>
        </div>

        <!-- Ollama Settings -->
        <div class="border border-gray-200 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <span class="text-2xl">🏠</span>
              <div>
                <h3 class="font-medium text-gray-900">Ollama (Local)</h3>
                <p class="text-sm text-gray-600">Free local AI models</p>
              </div>
            </div>
            <div class="flex items-center">
              <span :class="ollamaStatus.available ? 'text-success-600' : 'text-warning-600'"
                class="text-sm font-medium">
                {{ ollamaStatus.available ? '✓ Available' : '⚠️ Not Running' }}
              </span>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Server URL
              </label>
              <div class="flex space-x-2">
                <input v-model="ollamaUrl" type="url" class="flex-1 p-3 border border-gray-300 rounded-lg focus-ring"
                  placeholder="http://localhost:11434" />
                <button @click="testApiKey('ollama')" :disabled="!ollamaUrl || validating.ollama"
                  class="btn btn-primary">
                  {{ validating.ollama ? '⏳' : '🧪' }}
                </button>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                Install Ollama from <a href="https://ollama.ai" target="_blank"
                  class="text-primary-600 hover:underline">ollama.ai</a>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="mt-6 flex justify-end">
        <button @click="saveSettings" :disabled="saving" class="btn btn-primary">
          <span v-if="saving">Saving...</span>
          <span v-else>Save Settings</span>
        </button>
      </div>
    </div>

    <!-- Application Preferences -->
    <div class="card">
      <h2 class="text-xl font-semibold text-gray-900 mb-6">Application Preferences</h2>

      <div class="space-y-6">
        <!-- Default Provider -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Default AI Provider
          </label>
          <select v-model="defaultProvider" class="w-full p-3 border border-gray-300 rounded-lg focus-ring">
            <option value="gemini">Google Gemini (Recommended)</option>
            <option value="openai">OpenAI</option>
            <option value="ollama">Ollama (Local)</option>
          </select>
        </div>

        <!-- PDF Viewer Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            PDF Viewer Type
          </label>
          <select v-model="pdfViewerType" class="w-full p-3 border border-gray-300 rounded-lg focus-ring">
            <option value="pdfjs">PDF.js (Clean, Interactive)</option>
            <option value="iframe">Clean iframe (Simple, Fast)</option>
            <option value="browser">Browser Default (Full Controls)</option>
          </select>
          <p class="text-xs text-gray-500 mt-1">
            Choose how PDFs are displayed in the results page
          </p>
        </div>

        <!-- Auto-download Results -->
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-medium text-gray-900">Auto-download Results</h3>
            <p class="text-sm text-gray-600">Automatically download files when processing completes</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input v-model="autoDownload" type="checkbox" class="sr-only peer" />
            <div
              class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600">
            </div>
          </label>
        </div>

        <!-- Clear History -->
        <div class="flex items-center justify-between py-4 border-t border-gray-200">
          <div>
            <h3 class="font-medium text-gray-900">Clear Processing History</h3>
            <p class="text-sm text-gray-600">Remove all previous job history and temporary files</p>
          </div>
          <button @click="clearHistory" class="btn btn-secondary text-error-600 hover:bg-error-50">
            Clear History
          </button>
        </div>
      </div>
    </div>

    <!-- System Information -->
    <div class="card">
      <h2 class="text-xl font-semibold text-gray-900 mb-6">System Information</h2>

      <div class="grid md:grid-cols-2 gap-6">
        <div>
          <h3 class="font-medium text-gray-900 mb-2">Frontend Version</h3>
          <p class="text-sm text-gray-600">v1.0.0</p>
        </div>
        <div>
          <h3 class="font-medium text-gray-900 mb-2">Backend Status</h3>
          <p class="text-sm" :class="backendStatus ? 'text-success-600' : 'text-error-600'">
            {{ backendStatus ? '✓ Connected' : '✗ Disconnected' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Current Run Log -->
    <div class="card">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-gray-900">Current Run Log</h2>
        <button @click="refreshWorkflowLog" :disabled="loadingLog" class="btn btn-secondary">
          {{ loadingLog ? '⏳' : '🔄' }} Refresh
        </button>
      </div>

      <div v-if="loadingLog" class="text-center py-8">
        <div class="text-gray-500">Loading current run log...</div>
      </div>

      <div v-else-if="workflowLog" class="space-y-4">
        <div class="flex items-center justify-between text-sm text-gray-600">
          <span>Last updated: {{ formatDate(workflowLog.lastModified) }}</span>
          <button @click="clearWorkflowLog" class="text-error-600 hover:text-error-700">
            Clear Log
          </button>
        </div>

        <div class="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
          <pre class="text-sm text-gray-700 whitespace-pre-wrap font-mono">{{ workflowLog.log }}</pre>
        </div>
      </div>

      <div v-else class="text-center py-8 text-gray-500">
        No current run log found. Start a resume generation to see workflow data.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAPI } from '../composables/useAPI.js'
import { useSettings } from '../composables/useSettings.js'
import { API_CONFIG } from '../config/api.js'

const { getProviders, validateApiKey } = useAPI()
const { settings, saveSettings: saveSettingsToStorage } = useSettings()

// API Configuration
const API_BASE_URL = API_CONFIG.API_BASE_URL

// State
const saving = ref(false)
const backendStatus = ref(false)

// UI State
const showApiKeys = ref({
  gemini: false,
  openai: false
})

const validating = ref({
  gemini: false,
  openai: false,
  ollama: false
})

const validationResults = ref({
  gemini: null,
  openai: null,
  ollama: null
})

// Provider Status
const geminiStatus = ref({ available: false })
const openaiStatus = ref({ available: false })
const ollamaStatus = ref({ available: false })

// Workflow Log
const workflowLog = ref(null)
const loadingLog = ref(false)

// Settings (reactive references to the global settings)
const apiKeys = settings.apiKeys
const ollamaUrl = ref(settings.ollamaUrl)
const defaultProvider = ref(settings.defaultProvider)
const autoDownload = ref(settings.autoDownload)
const pdfViewerType = ref(settings.pdfViewerType || 'pdfjs')

// Methods
const toggleApiKeyVisibility = (provider) => {
  showApiKeys.value[provider] = !showApiKeys.value[provider]
}

const saveSettings = async () => {
  try {
    saving.value = true

    // Update settings object
    settings.ollamaUrl = ollamaUrl.value
    settings.defaultProvider = defaultProvider.value
    settings.autoDownload = autoDownload.value
    settings.pdfViewerType = pdfViewerType.value

    // Save to localStorage (happens automatically via useSettings watcher)
    const success = saveSettingsToStorage()

    if (success) {
      alert('Settings saved successfully!')
    } else {
      throw new Error('Failed to save to localStorage')
    }

  } catch (error) {
    alert('Failed to save settings: ' + error.message)
  } finally {
    saving.value = false
  }
}

const checkProviderStatus = async () => {
  try {
    const data = await getProviders()
    const providers = data.providers || []

    geminiStatus.value = providers.find(p => p.id === 'gemini') || { available: false }
    openaiStatus.value = providers.find(p => p.id === 'openai') || { available: false }
    ollamaStatus.value = providers.find(p => p.id === 'ollama') || { available: false }

    backendStatus.value = true
  } catch (error) {
    console.error('Failed to check provider status:', error)
    backendStatus.value = false
  }
}

const testApiKey = async (provider) => {
  try {
    validating.value[provider] = true
    validationResults.value[provider] = null

    const apiKey = provider === 'ollama' ? null : apiKeys.value[provider]
    const result = await validateApiKey(provider, apiKey, provider === 'ollama' ? ollamaUrl.value : null)

    validationResults.value[provider] = result

    if (result.valid) {
      alert(`✅ ${provider.toUpperCase()} ${provider === 'ollama' ? 'server' : 'API key'} is valid!`)
    } else {
      alert(`❌ ${provider.toUpperCase()} validation failed: ${result.error}`)
    }

  } catch (error) {
    alert(`❌ Failed to test ${provider}: ${error.message}`)
  } finally {
    validating.value[provider] = false
  }
}

const clearHistory = async () => {
  if (confirm('Are you sure you want to clear all processing history? This cannot be undone.')) {
    try {
      // In a real app, this would call an API to clear history
      localStorage.removeItem('tex-tailor-history')
      alert('History cleared successfully!')
    } catch (error) {
      alert('Failed to clear history: ' + error.message)
    }
  }
}

const refreshWorkflowLog = async () => {
  try {
    loadingLog.value = true
    const response = await fetch(`${API_BASE_URL}/process/log`)
    const data = await response.json()

    if (data.success) {
      workflowLog.value = data
    } else {
      throw new Error(data.error || 'Failed to fetch workflow log')
    }
  } catch (error) {
    console.error('Failed to fetch workflow log:', error)
    alert('Failed to fetch workflow log: ' + error.message)
  } finally {
    loadingLog.value = false
  }
}

const clearWorkflowLog = async () => {
  if (confirm('Are you sure you want to clear the workflow log? This cannot be undone.')) {
    try {
      const response = await fetch(`${API_BASE_URL}/process/log`, {
        method: 'DELETE'
      })
      const data = await response.json()

      if (data.success) {
        workflowLog.value = null
        alert('Workflow log cleared!')
      } else {
        throw new Error(data.error || 'Failed to clear workflow log')
      }
    } catch (error) {
      console.error('Failed to clear workflow log:', error)
      alert('Failed to clear workflow log: ' + error.message)
    }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

// Lifecycle
onMounted(() => {
  // Sync local refs with global settings
  ollamaUrl.value = settings.ollamaUrl
  defaultProvider.value = settings.defaultProvider
  autoDownload.value = settings.autoDownload
  pdfViewerType.value = settings.pdfViewerType || 'pdfjs'

  checkProviderStatus()
  refreshWorkflowLog()
})
</script>