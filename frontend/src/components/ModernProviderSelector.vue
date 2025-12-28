<template>
  <div class="space-y-4 provider-selector-compact">
    <!-- AI Provider & Model Section -->
    <div class="space-y-3">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">AI Provider & Model</h3>

      <!-- Provider Dropdown -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">AI Provider</label>
        <select v-model="selectedProvider" @change="handleProviderChange"
          class="w-full p-3 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors">
          <option v-for="provider in providers" :key="provider.id" :value="provider.id">
            {{ provider.name }} {{ provider.recommended ? '(Recommended)' : '' }}
          </option>
        </select>
      </div>

      <!-- Model Dropdown -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">Model</label>
        <select v-model="selectedModel" @change="handleModelChange"
          class="w-full p-3 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors">
          <option v-for="model in currentProvider?.models" :key="model.id" :value="model.id"
            :disabled="model.warning === 'Broken'" :class="{ 'text-gray-400': model.warning === 'Broken' }">
            {{ model.name }}
            {{ model.recommended ? '(Recommended)' : '' }}
            {{ model.warning === 'Broken' ? '(Unavailable)' : '' }}
            {{ model.warning === 'Low Quality' ? '(Testing only)' : '' }}
            {{ model.warning === 'Quota Issues' ? '(Use sparingly)' : '' }}
          </option>
        </select>
        <!-- Model Description -->
        <div v-if="currentModel" class="text-xs text-gray-600 bg-gray-50 p-2 rounded">
          <p class="mb-1">{{ getCleanDescription(currentModel.description) }}</p>
          <div class="flex items-center space-x-4">
            <span class="flex items-center space-x-1">
              <div class="w-1.5 h-1.5 rounded-full" :class="getQualityColor(currentModel.quality)"></div>
              <span>{{ currentModel.quality }}</span>
            </span>
            <span class="flex items-center space-x-1">
              <div class="w-1.5 h-1.5 rounded-full" :class="getSpeedColor(currentModel.speed)"></div>
              <span>{{ currentModel.speed }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Writing Style Section -->
    <div class="space-y-3 pt-3 border-t border-gray-200">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">Writing Style</h3>

      <!-- Writing Style Dropdown -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">Personality</label>
        <select v-model="selectedPersonality" @change="handlePersonalityChange"
          class="w-full p-3 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors">
          <option v-for="personality in personalities" :key="personality.id" :value="personality.id">
            {{ personality.name }} {{ personality.id === 'career_savvy_colleague' ? '(Default)' : '' }}
          </option>
        </select>
        <!-- Personality Description -->
        <div v-if="currentPersonality" class="text-xs text-gray-600 bg-gray-50 p-2 rounded">
          {{ currentPersonality.description }}
        </div>
      </div>
    </div>

    <!-- API Key Status -->

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useSettings } from '../composables/useSettings.js'

const props = defineProps({
  provider: String,
  model: String,
  personality: String
})

const emit = defineEmits(['update:provider', 'update:model', 'update:personality', 'update'])
const { hasApiKey } = useSettings()

// State
const selectedProvider = ref(props.provider || 'ollama')
const selectedModel = ref(props.model || 'qwen2.5:14b-instruct')
const selectedPersonality = ref(props.personality || 'career_savvy_colleague')

// Personality configurations
const personalities = ref([
  {
    id: 'career_savvy_colleague',
    name: 'Career-Savvy Colleague',
    icon: '🛡️',
    description: 'Trusted peer providing collaborative, grounded advice.'
  },
  {
    id: 'direct_confident',
    name: 'Direct & Confident',
    icon: '💪',
    description: 'Authoritative, results-focused with measurable outcomes.'
  },
  {
    id: 'enthusiastic_innovator',
    name: 'Enthusiastic Innovator',
    icon: '🚀',
    description: 'Forward-thinking, passionate about cutting-edge solutions.'
  },
  {
    id: 'calm_mentor',
    name: 'Calm Mentor',
    icon: '🧑‍🏫',
    description: 'Wise, experienced guide with stable professionalism.'
  },
  {
    id: 'engaging_storyteller',
    name: 'Engaging Storyteller',
    icon: '📚',
    description: 'Witty, narrative-driven approach to showcase experience.'
  },
  {
    id: 'meticulous_analyst',
    name: 'Meticulous Analyst',
    icon: '📊',
    description: 'Data-driven, systematic approach with evidence-based claims.'
  },
  {
    id: 'ambitious_go_getter',
    name: 'Ambitious Go-Getter',
    icon: '⚡',
    description: 'High-energy, achievement-focused with urgency for results.'
  }
])

// Provider configurations
const providers = ref([
  {
    id: 'gemini',
    name: 'Google Gemini',
    icon: '🧠',
    description: 'Best balance of speed, quality, and cost.',
    recommended: true,
    apiKeyRequired: true,
    models: [
      {
        id: 'gemini-2.5-flash-lite',
        name: 'Gemini 2.5 Flash-Lite',
        description: 'Fast and efficient - perfect balance of speed and quality for everyday use.',
        recommended: true,
        quality: 'Good',
        speed: 'Very Fast'
      },
      {
        id: 'gemini-2.5-flash',
        name: 'Gemini 2.5 Flash',
        description: 'Does not generate any output. Use 2.5 Flash-Lite instead.',
        recommended: false,
        quality: 'Variable',
        speed: 'Fast',
        warning: 'Broken'
      },
      {
        id: 'gemini-2.5-pro',
        name: 'Gemini 2.5 Pro',
        description: '500 errors and API failures. Use 2.5 Flash-Lite instead.',
        recommended: false,
        quality: 'Variable',
        speed: 'Medium',
        warning: 'Broken'
      },
      {
        id: 'gemini-1.5-flash',
        name: 'Gemini 1.5 Flash',
        description: 'Lower quality output - use for testing only. Prefer 2.5 Flash-Lite.',
        recommended: false,
        quality: 'Good',
        speed: 'Fast',
        warning: 'Low Quality'
      },
      {
        id: 'gemini-1.5-pro',
        name: 'Gemini 1.5 Pro',
        description: '500 errors due to low quota limits. Use sparingly.',
        recommended: false,
        quality: 'Highest',
        speed: 'Medium',
        warning: 'Quota Issues'
      }
    ]
  },
  {
    id: 'openai',
    name: 'OpenAI',
    icon: '🤖',
    description: 'Highest quality, premium pricing',
    recommended: false,
    apiKeyRequired: true,
    models: [
      {
        id: 'gpt-4o',
        name: 'GPT-4o',
        description: 'Latest OpenAI model with excellent reasoning and creativity.',
        recommended: true,
        quality: 'Highest',
        speed: 'Fast'
      },
      {
        id: 'gpt-4o-mini',
        name: 'GPT-4o Mini',
        description: 'Fast and cost-effective with good quality.',
        recommended: false,
        quality: 'High',
        speed: 'Very Fast'
      }
    ]
  },
  {
    id: 'mistral',
    name: 'Mistral',
    icon: '🌪️',
    description: 'High quality, competitive pricing',
    recommended: false,
    apiKeyRequired: true,
    models: [
      {
        id: 'mistral-large-latest',
        name: 'Mistral Large',
        description: 'High-quality model with excellent reasoning.',
        recommended: true,
        quality: 'High',
        speed: 'Medium'
      },
      {
        id: 'mistral-medium-latest',
        name: 'Mistral Medium',
        description: 'Good balance of quality and speed.',
        recommended: false,
        quality: 'Good',
        speed: 'Fast'
      }
    ]
  },
  {
    id: 'groq',
    name: 'Groq',
    icon: '⚡',
    description: 'Ultra-fast inference, competitive pricing',
    recommended: false,
    apiKeyRequired: true,
    models: [
      {
        id: 'llama3-70b-8192',
        name: 'Llama 3.1 (70B)',
        description: 'Ultra-fast inference with good quality.',
        recommended: true,
        quality: 'High',
        speed: 'Ultra Fast'
      },
      {
        id: 'llama3-8b-8192',
        name: 'Llama 3.1 (8B)',
        description: 'Very fast with decent quality.',
        recommended: false,
        quality: 'Good',
        speed: 'Ultra Fast'
      }
    ]
  },
  {
    id: 'ollama',
    name: 'Ollama (Local)',
    icon: '🏠',
    description: 'Free local models, requires setup',
    recommended: false,
    apiKeyRequired: false,
    models: [
      {
        id: 'qwen2.5:14b-instruct',
        name: '🎯 Resume Editor (Custom)',
        description: 'SPECIALIZED MODEL - Custom trained for resume and cover letter tailoring. Best choice for job applications.',
        recommended: true,
        quality: 'Excellent',
        speed: 'Medium',
        badge: 'Specialized'
      },
      {
        id: 'qwen2.5:14b-instruct',
        name: 'Qwen 2.5 (14B)',
        description: 'Best general-purpose balance - excellent JSON parsing and company name recognition.',
        recommended: true,
        quality: 'High',
        speed: 'Fast'
      },
      {
        id: 'llama3:8b',
        name: 'Llama 3.1 (8B)',
        description: 'Good general capability but may struggle with JSON parsing and company names.',
        recommended: false,
        quality: 'Good',
        speed: 'Fast'
      }
    ]
  }
])

// Computed
const currentProvider = computed(() => {
  return providers.value.find(p => p.id === selectedProvider.value)
})

const currentModel = computed(() => {
  return currentProvider.value?.models.find(m => m.id === selectedModel.value)
})

const currentPersonality = computed(() => {
  return personalities.value.find(p => p.id === selectedPersonality.value)
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
    const recommendedModel = provider.models.find(m => m.recommended)
    selectedModel.value = recommendedModel ? recommendedModel.id : provider.models[0].id
  }
})

// Methods
const handleProviderChange = () => {
  // Model will be automatically updated via the watcher
}

const handleModelChange = () => {
  // Model change is handled by v-model
}

const handlePersonalityChange = () => {
  // Personality change is handled by v-model
}

const getQualityColor = (quality) => {
  const colors = {
    'Basic': 'bg-gray-400',
    'Good': 'bg-blue-500',
    'High': 'bg-green-500',
    'Excellent': 'bg-purple-500',
    'Highest': 'bg-purple-600',
    'Variable': 'bg-gray-500'
  }
  return colors[quality] || 'bg-gray-400'
}

const getSpeedColor = (speed) => {
  const colors = {
    'Very Fast': 'bg-green-500',
    'Ultra Fast': 'bg-emerald-500',
    'Fast': 'bg-blue-500',
    'Medium': 'bg-yellow-500',
    'Slow': 'bg-red-500',
    'Very Slow': 'bg-red-600',
    'Variable': 'bg-gray-500'
  }
  return colors[speed] || 'bg-gray-400'
}

const getCleanDescription = (description) => {
  // Remove warning prefixes and emojis for cleaner display
  return description.replace(/^(⚠️\s*|BROKEN\s*-\s*|❌\s*)/i, '').trim()
}
</script>