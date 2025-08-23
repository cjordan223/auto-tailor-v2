<template>
  <div class="card">
    <h3 class="text-lg font-semibold text-gray-900 mb-6">AI Provider Configuration</h3>
    
    <!-- Provider Selection -->
    <div class="grid md:grid-cols-3 gap-4 mb-6">
      <div
        v-for="provider in providers"
        :key="provider.id"
        class="relative cursor-pointer rounded-lg border p-4 hover:shadow-md transition-all"
        :class="{
          'border-primary-600 bg-primary-50': selectedProvider === provider.id,
          'border-gray-200': selectedProvider !== provider.id
        }"
        @click="selectProvider(provider.id)"
      >
        <div class="flex items-center">
          <input
            type="radio"
            :value="provider.id"
            v-model="selectedProvider"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
          />
          <div class="ml-3">
            <div class="text-sm font-medium text-gray-900 flex items-center">
              <span class="mr-2">{{ provider.icon }}</span>
              {{ provider.name }}
              <span
                v-if="provider.recommended"
                class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success-100 text-success-800"
              >
                Recommended
              </span>
              <span
                v-if="provider.apiKeyRequired"
                :class="hasApiKey(provider.id) ? 'text-success-600' : 'text-warning-600'"
                class="ml-2"
              >
                {{ hasApiKey(provider.id) ? '✓' : '⚠' }}
              </span>
            </div>
            <div class="text-xs text-gray-500 mt-1">{{ provider.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Selection -->
    <div v-if="selectedProvider">
      <label class="block text-sm font-medium text-gray-700 mb-3">
        Model Selection
      </label>
      <select
        v-model="selectedModel"
        class="w-full p-3 border border-gray-300 rounded-lg focus-ring"
      >
        <option
          v-for="model in availableModels"
          :key="model.id"
          :value="model.id"
        >
          {{ model.name }} - {{ model.description }}
        </option>
      </select>
    </div>

    <!-- Provider Info -->
    <div v-if="selectedProvider" class="mt-6 p-4 bg-gray-50 rounded-lg">
      <h4 class="text-sm font-medium text-gray-900 mb-2">Provider Information</h4>
      <div class="text-sm text-gray-600 space-y-1">
        <p><span class="font-medium">Quality:</span> {{ currentProvider.quality }}</p>
        <p><span class="font-medium">Speed:</span> {{ currentProvider.speed }}</p>
        <p><span class="font-medium">Cost:</span> {{ currentProvider.cost }}</p>
        <p v-if="currentProvider.apiKeyRequired" :class="hasApiKey(currentProvider.id) ? 'text-success-600' : 'text-warning-600'">
          <span class="font-medium">{{ hasApiKey(currentProvider.id) ? '✅ API Key Configured' : '⚠️ API Key Required' }}</span>
          <span v-if="!hasApiKey(currentProvider.id)">: {{ currentProvider.apiKeyEnv }}</span>
        </p>
        <p v-if="currentProvider.apiKeyRequired && !hasApiKey(currentProvider.id)" class="text-sm">
          <router-link to="/settings" class="text-primary-600 hover:underline">
            Configure API key in Settings →
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useSettings } from '../composables/useSettings.js'

const props = defineProps({
  provider: String,
  model: String
})

const emit = defineEmits(['update:provider', 'update:model', 'update'])
const { hasApiKey } = useSettings()

// State
const selectedProvider = ref(props.provider || 'gemini')
const selectedModel = ref(props.model || 'gemini-1.5-flash')

// Provider configurations
const providers = ref([
  {
    id: 'gemini',
    name: 'Google Gemini',
    icon: '🧠',
    description: 'Best balance of speed, quality, and cost',
    recommended: true,
    quality: 'High',
    speed: 'Fast',
    cost: 'Low',
    apiKeyRequired: true,
    apiKeyEnv: 'GEMINI_API_KEY',
    models: [
      { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', description: 'Fast and efficient (Recommended)' },
      { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', description: 'Higher quality, slower' },
      { id: 'gemini-1.0-pro', name: 'Gemini 1.0 Pro', description: 'High rate limits (60 RPM), good for testing' }
    ]
  },
  {
    id: 'openai',
    name: 'OpenAI',
    icon: '🤖',
    description: 'Highest quality, premium pricing',
    recommended: false,
    quality: 'Highest',
    speed: 'Medium',
    cost: 'High',
    apiKeyRequired: true,
    apiKeyEnv: 'OPENAI_API_KEY',
    models: [
      { id: 'gpt-4o-mini', name: 'GPT-4o Mini', description: 'Fast and cost-effective' },
      { id: 'gpt-4o', name: 'GPT-4o', description: 'Highest quality' }
    ]
  },
  {
    id: 'ollama',
    name: 'Ollama (Local)',
    icon: '🏠',
    description: 'Free local models, requires setup',
    recommended: false,
    quality: 'Variable',
    speed: 'Variable',
    cost: 'Free',
    apiKeyRequired: false,
    apiKeyEnv: null,
    models: [
      { id: 'qwen2.5:14b-instruct', name: 'Qwen2.5 14B', description: 'Good quality, requires powerful hardware' },
      { id: 'llama3.1:8b', name: 'Llama 3.1 8B', description: 'Lighter model, faster inference' }
    ]
  }
])

// Computed
const currentProvider = computed(() => {
  return providers.value.find(p => p.id === selectedProvider.value)
})

const availableModels = computed(() => {
  return currentProvider.value?.models || []
})

// Watch for changes and emit
watch([selectedProvider, selectedModel], ([newProvider, newModel]) => {
  emit('update:provider', newProvider)
  emit('update:model', newModel)
  emit('update', newProvider, newModel)
}, { immediate: true })

// Update model when provider changes
watch(selectedProvider, (newProvider) => {
  const provider = providers.value.find(p => p.id === newProvider)
  if (provider && provider.models.length > 0) {
    selectedModel.value = provider.models[0].id
  }
})

// Methods
const selectProvider = (providerId) => {
  selectedProvider.value = providerId
}
</script>