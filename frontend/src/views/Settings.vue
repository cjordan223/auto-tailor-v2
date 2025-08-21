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
              <span
                :class="geminiStatus.available ? 'text-success-600' : 'text-error-600'"
                class="text-sm font-medium"
              >
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
                <input
                  v-model="apiKeys.gemini"
                  :type="showApiKeys.gemini ? 'text' : 'password'"
                  class="flex-1 p-3 border border-gray-300 rounded-lg focus-ring"
                  placeholder="Enter your Gemini API key"
                />
                <button
                  @click="toggleApiKeyVisibility('gemini')"
                  class="btn btn-secondary"
                >
                  {{ showApiKeys.gemini ? '🙈' : '👁️' }}
                </button>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" class="text-primary-600 hover:underline">Google AI Studio</a>
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
              <span
                :class="openaiStatus.available ? 'text-success-600' : 'text-error-600'"
                class="text-sm font-medium"
              >
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
                <input
                  v-model="apiKeys.openai"
                  :type="showApiKeys.openai ? 'text' : 'password'"
                  class="flex-1 p-3 border border-gray-300 rounded-lg focus-ring"
                  placeholder="Enter your OpenAI API key"
                />
                <button
                  @click="toggleApiKeyVisibility('openai')"
                  class="btn btn-secondary"
                >
                  {{ showApiKeys.openai ? '🙈' : '👁️' }}
                </button>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" class="text-primary-600 hover:underline">OpenAI Platform</a>
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
              <span
                :class="ollamaStatus.available ? 'text-success-600' : 'text-warning-600'"
                class="text-sm font-medium"
              >
                {{ ollamaStatus.available ? '✓ Available' : '⚠️ Not Running' }}
              </span>
            </div>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Server URL
              </label>
              <input
                v-model="ollamaUrl"
                type="url"
                class="w-full p-3 border border-gray-300 rounded-lg focus-ring"
                placeholder="http://localhost:11434"
              />
              <p class="text-xs text-gray-500 mt-1">
                Install Ollama from <a href="https://ollama.ai" target="_blank" class="text-primary-600 hover:underline">ollama.ai</a>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="mt-6 flex justify-end">
        <button
          @click="saveSettings"
          :disabled="saving"
          class="btn btn-primary"
        >
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
          <select
            v-model="defaultProvider"
            class="w-full p-3 border border-gray-300 rounded-lg focus-ring"
          >
            <option value="gemini">Google Gemini (Recommended)</option>
            <option value="openai">OpenAI</option>
            <option value="ollama">Ollama (Local)</option>
          </select>
        </div>

        <!-- Auto-download Results -->
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-medium text-gray-900">Auto-download Results</h3>
            <p class="text-sm text-gray-600">Automatically download files when processing completes</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input
              v-model="autoDownload"
              type="checkbox"
              class="sr-only peer"
            />
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
          </label>
        </div>

        <!-- Clear History -->
        <div class="flex items-center justify-between py-4 border-t border-gray-200">
          <div>
            <h3 class="font-medium text-gray-900">Clear Processing History</h3>
            <p class="text-sm text-gray-600">Remove all previous job history and temporary files</p>
          </div>
          <button
            @click="clearHistory"
            class="btn btn-secondary text-error-600 hover:bg-error-50"
          >
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAPI } from '../composables/useAPI.js'

const { getProviders } = useAPI()

// State
const saving = ref(false)
const backendStatus = ref(false)

// API Keys
const apiKeys = ref({
  gemini: '',
  openai: ''
})

const showApiKeys = ref({
  gemini: false,
  openai: false
})

// Provider Status
const geminiStatus = ref({ available: false })
const openaiStatus = ref({ available: false })
const ollamaStatus = ref({ available: false })

// Settings
const ollamaUrl = ref('http://localhost:11434')
const defaultProvider = ref('gemini')
const autoDownload = ref(false)

// Methods
const toggleApiKeyVisibility = (provider) => {
  showApiKeys.value[provider] = !showApiKeys.value[provider]
}

const saveSettings = async () => {
  try {
    saving.value = true
    
    // In a real app, this would save to localStorage or send to backend
    localStorage.setItem('tex-tailor-settings', JSON.stringify({
      apiKeys: apiKeys.value,
      ollamaUrl: ollamaUrl.value,
      defaultProvider: defaultProvider.value,
      autoDownload: autoDownload.value
    }))
    
    // Show success message
    alert('Settings saved successfully!')
    
  } catch (error) {
    alert('Failed to save settings: ' + error.message)
  } finally {
    saving.value = false
  }
}

const loadSettings = () => {
  try {
    const saved = localStorage.getItem('tex-tailor-settings')
    if (saved) {
      const settings = JSON.parse(saved)
      apiKeys.value = settings.apiKeys || { gemini: '', openai: '' }
      ollamaUrl.value = settings.ollamaUrl || 'http://localhost:11434'
      defaultProvider.value = settings.defaultProvider || 'gemini'
      autoDownload.value = settings.autoDownload || false
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
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

// Lifecycle
onMounted(() => {
  loadSettings()
  checkProviderStatus()
})
</script>