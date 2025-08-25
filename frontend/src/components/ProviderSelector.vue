<template>
  <div class="card">
    <h3 class="text-lg font-semibold text-gray-900 mb-6">AI Provider Configuration</h3>

    <!-- Provider Selection -->
    <div class="grid md:grid-cols-3 gap-4 mb-6">
      <div v-for="provider in providers" :key="provider.id"
        class="relative cursor-pointer rounded-lg border p-4 hover:shadow-md transition-all" :class="{
          'border-primary-600 bg-primary-50': selectedProvider === provider.id,
          'border-gray-200': selectedProvider !== provider.id
        }" @click="selectProvider(provider.id)">
        <div class="flex items-center">
          <input type="radio" :value="provider.id" v-model="selectedProvider"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300" />
          <div class="ml-3">
            <div class="text-sm font-medium text-gray-900 flex items-center">
              <span class="mr-2">{{ provider.icon }}</span>
              {{ provider.name }}
              <span v-if="provider.recommended"
                class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success-100 text-success-800">
                Recommended
              </span>
              <span v-if="provider.apiKeyRequired"
                :class="hasApiKey(provider.id) ? 'text-success-600' : 'text-warning-600'" class="ml-2">
                {{ hasApiKey(provider.id) ? '✓' : '⚠' }}
              </span>
            </div>
            <div class="text-xs text-gray-500 mt-1">{{ provider.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Selection -->
    <div v-if="selectedProvider && availableModels.length > 1" class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-3">
        Model Selection
      </label>
      <div class="relative model-dropdown">
        <button @click="showModelDropdown = !showModelDropdown"
          class="w-full p-4 border border-gray-300 rounded-lg bg-white text-left hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input type="radio" :value="currentModel.id" v-model="selectedModel"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300" />
              <div class="ml-3">
                <div class="text-sm font-medium text-gray-900 flex items-center">
                  {{ currentModel.name }}
                  <span v-if="currentModel.recommended"
                    class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success-100 text-success-800">
                    Recommended
                  </span>
                </div>
                <div class="text-xs text-gray-600 mt-1">{{ currentModel.description }}</div>
                <div class="text-xs text-gray-500 mt-1">
                  <span class="font-medium">Rate Limits:</span> {{ currentModel.rateLimits }}
                </div>
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <div class="flex flex-col items-end text-xs text-gray-500">
                <div class="flex items-center space-x-2">
                  <span class="font-medium">Quality:</span>
                  <span :class="getQualityClass(currentModel.quality)">{{ currentModel.quality }}</span>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="font-medium">Speed:</span>
                  <span :class="getSpeedClass(currentModel.speed)">{{ currentModel.speed }}</span>
                </div>
              </div>
              <svg class="w-5 h-5 text-gray-400 transition-transform" :class="{ 'rotate-180': showModelDropdown }"
                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </button>

        <!-- Dropdown Menu -->
        <div v-if="showModelDropdown"
          class="model-dropdown absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          <div v-for="model in availableModels" :key="model.id"
            class="cursor-pointer p-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
            :class="{ 'bg-primary-50': selectedModel === model.id }" @click="selectModel(model.id)">
            <div class="flex items-start justify-between">
              <div class="flex items-center">
                <input type="radio" :value="model.id" v-model="selectedModel"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300" />
                <div class="ml-3">
                  <div class="text-sm font-medium text-gray-900 flex items-center">
                    {{ model.name }}
                    <span v-if="model.recommended"
                      class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success-100 text-success-800">
                      Recommended
                    </span>
                  </div>
                  <div class="text-xs text-gray-600 mt-1">{{ model.description }}</div>
                  <div class="text-xs text-gray-500 mt-1">
                    <span class="font-medium">Rate Limits:</span> {{ model.rateLimits }}
                  </div>
                </div>
              </div>
              <div class="flex flex-col items-end text-xs text-gray-500">
                <div class="flex items-center space-x-2">
                  <span class="font-medium">Quality:</span>
                  <span :class="getQualityClass(model.quality)">{{ model.quality }}</span>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="font-medium">Speed:</span>
                  <span :class="getSpeedClass(model.speed)">{{ model.speed }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Personality Selection -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-3">
        Writing Personality
      </label>
      <div class="grid md:grid-cols-2 gap-3">
        <div v-for="personality in personalities" :key="personality.id"
          class="relative cursor-pointer rounded-lg border p-3 hover:shadow-md transition-all" :class="{
            'border-primary-600 bg-primary-50': selectedPersonality === personality.id,
            'border-gray-200': selectedPersonality !== personality.id
          }" @click="selectPersonality(personality.id)">
          <div class="flex items-start">
            <input type="radio" :value="personality.id" v-model="selectedPersonality"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 mt-0.5" />
            <div class="ml-3 flex-1">
              <div class="text-sm font-medium text-gray-900 flex items-center">
                <span class="mr-2">{{ personality.icon }}</span>
                {{ personality.name }}
                <span v-if="personality.id === 'career_savvy_colleague'"
                  class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success-100 text-success-800">
                  Default
                </span>
              </div>
              <div class="text-xs text-gray-500 mt-1">{{ personality.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Provider Info -->
    <div v-if="selectedProvider" class="mt-6 p-4 bg-gray-50 rounded-lg">
      <h4 class="text-sm font-medium text-gray-900 mb-2">Provider Information</h4>
      <div class="text-sm text-gray-600 space-y-1">
        <p><span class="font-medium">Quality:</span> {{ currentModel.quality }}</p>
        <p><span class="font-medium">Speed:</span> {{ currentModel.speed }}</p>
        <p><span class="font-medium">Cost:</span> {{ currentProvider.cost }}</p>
        <p v-if="currentProvider.apiKeyRequired"
          :class="hasApiKey(currentProvider.id) ? 'text-success-600' : 'text-warning-600'">
          <span class="font-medium">{{ hasApiKey(currentProvider.id) ? '✅ API Key Configured' : '⚠️ API Key Required'
            }}</span>
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useSettings } from '../composables/useSettings.js'

const props = defineProps({
  provider: String,
  model: String,
  personality: String
})

const emit = defineEmits(['update:provider', 'update:model', 'update:personality', 'update'])
const { hasApiKey } = useSettings()

// State
const selectedProvider = ref(props.provider || 'gemini')
const selectedModel = ref(props.model || 'gemini-2.5-flash-lite')
const selectedPersonality = ref(props.personality || 'career_savvy_colleague')
const showModelDropdown = ref(false)

// Personality configurations
const personalities = ref([
  {
    id: 'career_savvy_colleague',
    name: 'Career-Savvy Colleague',
    description: 'Trusted peer providing collaborative, grounded advice',
    icon: '🤝'
  },
  {
    id: 'direct_and_confident',
    name: 'Direct & Confident',
    description: 'Authoritative, results-focused with measurable outcomes',
    icon: '💪'
  },
  {
    id: 'enthusiastic_innovator',
    name: 'Enthusiastic Innovator',
    description: 'Forward-thinking, passionate about cutting-edge solutions',
    icon: '🚀'
  },
  {
    id: 'calm_mentor',
    name: 'Calm Mentor',
    description: 'Wise, experienced guide with stable professionalism',
    icon: '🧘'
  },
  {
    id: 'engaging_storyteller',
    name: 'Engaging Storyteller',
    description: 'Witty, narrative-driven approach to showcase experience',
    icon: '📖'
  },
  {
    id: 'meticulous_analyst',
    name: 'Meticulous Analyst',
    description: 'Data-driven, systematic approach with evidence-based claims',
    icon: '📊'
  },
  {
    id: 'ambitious_go_getter',
    name: 'Ambitious Go-Getter',
    description: 'High-energy, achievement-focused with urgency for results',
    icon: '⚡'
  }
])

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
      {
        id: 'gemini-2.5-flash-lite',
        name: 'Gemini 2.5 Flash-Lite',
        description: 'Fast and efficient - perfect balance of speed and quality for everyday use',
        recommended: true,
        quality: 'Good',
        speed: 'Very Fast',
        rateLimits: '15 RPM, 1,000 RPD (Free) / 4,000 RPM (Paid)'
      },
      {
        id: 'gemini-2.5-flash',
        name: 'Gemini 2.5 Flash',
        description: 'Standard production model with excellent performance',
        recommended: false,
        quality: 'High',
        speed: 'Fast',
        rateLimits: '10 RPM, 250 RPD (Free) / 1,000+ RPM (Paid)'
      },
      {
        id: 'gemini-2.5-pro',
        name: 'Gemini 2.5 Pro',
        description: 'Highest quality analysis - best for final review before submitting',
        recommended: false,
        quality: 'Highest',
        speed: 'Medium',
        rateLimits: '5 RPM, 100 RPD (Free) / 150+ RPM (Paid)'
      },
      {
        id: 'gemini-1.5-flash',
        name: 'Gemini 1.5 Flash',
        description: 'Proven stable model - current default choice',
        recommended: false,
        quality: 'High',
        speed: 'Fast',
        rateLimits: '15 RPM, 1,500 RPD (Free) / 1,000+ RPM (Paid)'
      },
      {
        id: 'gemini-1.5-pro-latest',
        name: 'Gemini 1.5 Pro',
        description: 'High-quality tasks with detailed analysis',
        recommended: false,
        quality: 'Highest',
        speed: 'Medium',
        rateLimits: '2 RPM, 50 RPD (Free) / 150+ RPM (Paid)'
      }
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
      {
        id: 'gpt-4o-mini',
        name: 'GPT-4o Mini',
        description: 'Fast and cost-effective',
        recommended: true,
        quality: 'High',
        speed: 'Fast',
        rateLimits: '3,000 RPM (Paid)'
      },
      {
        id: 'gpt-4o',
        name: 'GPT-4o',
        description: 'Highest quality with advanced reasoning',
        recommended: false,
        quality: 'Highest',
        speed: 'Medium',
        rateLimits: '500 RPM (Paid)'
      }
    ]
  },
  {
    id: 'mistral',
    name: 'Mistral',
    icon: '🌪️',
    description: 'High quality, competitive pricing',
    recommended: false,
    quality: 'High',
    speed: 'Fast',
    cost: 'Medium',
    apiKeyRequired: true,
    apiKeyEnv: 'MISTRAL_API_KEY',
    models: [
      {
        id: 'mistral-large-latest',
        name: 'Mistral Large',
        description: 'Latest high-performance model',
        recommended: true,
        quality: 'High',
        speed: 'Fast',
        rateLimits: '1 RPS (60 RPM), 500K TPM, 1B tokens/month (Free)'
      },
      {
        id: 'mistral-medium-latest',
        name: 'Mistral Medium',
        description: 'Balanced performance and cost',
        recommended: false,
        quality: 'Good',
        speed: 'Fast',
        rateLimits: '1 RPS (60 RPM), 500K TPM, 1B tokens/month (Free)'
      },
      {
        id: 'mistral-small-latest',
        name: 'Mistral Small',
        description: 'Fast and cost-effective',
        recommended: false,
        quality: 'Good',
        speed: 'Very Fast',
        rateLimits: '1 RPS (60 RPM), 500K TPM, 1B tokens/month (Free)'
      }
    ]
  },
  {
    id: 'groq',
    name: 'Groq',
    icon: '⚡',
    description: 'Ultra-fast inference, competitive pricing',
    recommended: false,
    quality: 'High',
    speed: 'Ultra Fast',
    cost: 'Medium',
    apiKeyRequired: true,
    apiKeyEnv: 'GROQ_API_KEY',
    models: [
      {
        id: 'llama-3.3-70b-versatile',
        name: 'Llama 3.3 70B Versatile',
        description: 'High-quality model with ultra-fast inference',
        recommended: true,
        quality: 'High',
        speed: 'Ultra Fast',
        rateLimits: '30 RPM, 14.4K RPD, 40K TPM (Free)'
      },
      {
        id: 'llama-3.1-8b-versatile',
        name: 'Llama 3.1 8B Versatile',
        description: 'Fast and efficient for most tasks',
        recommended: false,
        quality: 'Good',
        speed: 'Ultra Fast',
        rateLimits: '30 RPM, 14.4K RPD, 40K TPM (Free)'
      },
      {
        id: 'mixtral-8x7b-32768',
        name: 'Mixtral 8x7B',
        description: 'High-quality mixture of experts model',
        recommended: false,
        quality: 'High',
        speed: 'Fast',
        rateLimits: '30 RPM, 14.4K RPD, 40K TPM (Free)'
      }
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
      {
        id: 'phi3:mini',
        name: 'Phi-3 Mini (3.8B)',
        description: 'Fastest and most lightweight model, suitable for simple tasks.',
        recommended: false,
        quality: 'Good',
        speed: 'Very Fast',
        rateLimits: 'No limits (local)'
      },
      {
        id: 'llama3:8b',
        name: 'Llama 3.1 (8B)',
        description: 'Excellent balance of performance and speed. Recommended for most users.',
        recommended: true,
        quality: 'High',
        speed: 'Fast',
        rateLimits: 'No limits (local)'
      },
      {
        id: 'llama3.1:70b',
        name: 'Llama 3.1 (70B)',
        description: 'Highest quality local model, requires significant resources.',
        recommended: false,
        quality: 'Highest',
        speed: 'Slow',
        rateLimits: 'No limits (local)'
      }
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

const currentModel = computed(() => {
  return availableModels.value.find(m => m.id === selectedModel.value) || availableModels.value[0]
})

// Watch for changes and emit
watch([selectedProvider, selectedModel, selectedPersonality], ([newProvider, newModel, newPersonality]) => {
  emit('update:provider', newProvider)
  emit('update:model', newModel)
  emit('update:personality', newPersonality)
  emit('update', newProvider, newModel, newPersonality)
}, { immediate: true })

// Update model when provider changes
watch(selectedProvider, (newProvider) => {
  const provider = providers.value.find(p => p.id === newProvider)
  if (provider && provider.models.length > 0) {
    // Select recommended model if available, otherwise first model
    const recommendedModel = provider.models.find(m => m.recommended)
    selectedModel.value = recommendedModel ? recommendedModel.id : provider.models[0].id
  }
})

// Methods
const selectProvider = (providerId) => {
  selectedProvider.value = providerId
}

const selectModel = (modelId) => {
  selectedModel.value = modelId
  showModelDropdown.value = false
}

const selectPersonality = (personalityId) => {
  selectedPersonality.value = personalityId
}

// Click outside handler to close dropdown
const handleClickOutside = (event) => {
  const dropdown = event.target.closest('.model-dropdown')
  if (!dropdown) {
    showModelDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const getQualityClass = (quality) => {
  const classes = {
    'Good': 'text-blue-600',
    'High': 'text-green-600',
    'Highest': 'text-purple-600',
    'Variable': 'text-gray-600'
  }
  return classes[quality] || 'text-gray-600'
}

const getSpeedClass = (speed) => {
  const classes = {
    'Very Fast': 'text-green-600',
    'Fast': 'text-blue-600',
    'Medium': 'text-yellow-600',
    'Slow': 'text-red-600',
    'Variable': 'text-gray-600'
  }
  return classes[speed] || 'text-gray-600'
}
</script>