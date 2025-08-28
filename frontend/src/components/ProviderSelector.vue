<template>
  <div class="card">
    <!-- Step Indicator -->
    <div class="mb-8">
      <!-- Progress Bar -->
      <div class="w-full bg-gray-200 rounded-full h-2 mb-6">
        <div class="bg-primary-600 h-2 rounded-full transition-all duration-500 ease-out"
          :style="{ width: `${((currentStep + 1) / steps.length) * 100}%` }"></div>
      </div>

      <div class="flex items-center justify-center space-x-4">
        <div v-for="(step, index) in steps" :key="step.id" class="flex items-center">
          <div
            class="flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-300 shadow-sm"
            :class="getStepClass(index)">
            <span v-if="currentStep > index" class="text-white text-sm font-medium">✓</span>
            <span v-else class="text-sm font-medium"
              :class="currentStep === index ? 'text-primary-600' : 'text-gray-500'">{{ index + 1 }}</span>
          </div>
          <span v-if="index < steps.length - 1" class="w-16 h-0.5 mx-2 transition-all duration-300"
            :class="currentStep > index ? 'bg-primary-600' : 'bg-gray-300'"></span>
        </div>
      </div>
      <div class="text-center mt-4">
        <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ currentStepTitle }}</h3>
        <p class="text-sm text-gray-500">{{ currentStepDescription }}</p>
      </div>
    </div>

    <!-- Step Content -->
    <div class="min-h-[400px] relative">
      <!-- Provider Selection Step -->
      <div v-if="currentStep === 0" class="step-content">
        <div class="grid gap-4">
          <div v-for="provider in providers" :key="provider.id"
            class="relative cursor-pointer rounded-xl border-2 p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] hover:border-primary-400"
            :class="{
              'border-primary-600 bg-primary-50 shadow-lg scale-[1.02]': selectedProvider === provider.id,
              'border-gray-200 hover:border-gray-300': selectedProvider !== provider.id
            }" @click="selectProvider(provider.id)">
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0">
                <div
                  class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center text-2xl">
                  {{ provider.icon }}
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2 mb-2">
                  <h4 class="text-lg font-semibold text-gray-900">{{ provider.name }}</h4>
                  <span v-if="provider.recommended"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
                    Recommended
                  </span>
                  <span v-if="provider.apiKeyRequired"
                    :class="hasApiKey(provider.id) ? 'text-success-600' : 'text-warning-600'" class="text-lg">
                    {{ hasApiKey(provider.id) ? '✓' : '⚠' }}
                  </span>
                </div>
                <p class="text-sm text-gray-600 mb-3">{{ provider.description }}</p>
                <div class="flex items-center space-x-4 text-xs text-gray-500">
                  <span class="flex items-center">
                    <span class="w-2 h-2 rounded-full bg-green-500 mr-1"></span>
                    {{ provider.quality }} Quality
                  </span>
                  <span class="flex items-center">
                    <span class="w-2 h-2 rounded-full bg-blue-500 mr-1"></span>
                    {{ provider.speed }} Speed
                  </span>
                  <span class="flex items-center">
                    <span class="w-2 h-2 rounded-full bg-purple-500 mr-1"></span>
                    {{ provider.cost }} Cost
                  </span>
                </div>
              </div>
              <div class="flex-shrink-0">
                <div class="w-6 h-6 rounded-full border-2 transition-all duration-200"
                  :class="selectedProvider === provider.id ? 'border-primary-600 bg-primary-600' : 'border-gray-300'">
                  <div v-if="selectedProvider === provider.id" class="w-2 h-2 bg-white rounded-full m-auto mt-1"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Model Selection Step -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="space-y-4">
          <div v-for="model in availableModels" :key="model.id"
            class="relative cursor-pointer rounded-xl border-2 p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] hover:border-primary-400"
            :class="{
              'border-primary-600 bg-primary-50 shadow-lg scale-[1.02]': selectedModel === model.id,
              'border-gray-200 hover:border-gray-300': selectedModel !== model.id
            }" @click="selectModel(model.id)">
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0">
                <div
                  class="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                  <span class="text-xl">🤖</span>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2 mb-2">
                  <h4 class="text-lg font-semibold text-gray-900">{{ model.name }}</h4>
                  <span v-if="model.badge === 'Specialized'"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    🎯 Specialized
                  </span>
                  <span v-else-if="model.recommended"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
                    Recommended
                  </span>
                  <span v-if="model.warning" :class="getWarningClass(model.warning)"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                    {{ getWarningIcon(model.warning) }} {{ model.warning }}
                  </span>
                </div>
                <p class="text-sm text-gray-600 mb-3">{{ model.description }}</p>
                <div class="grid grid-cols-2 gap-4 text-xs">
                  <div class="space-y-1">
                    <div class="flex items-center justify-between">
                      <span class="text-gray-500">Quality:</span>
                      <span :class="getQualityClass(model.quality)" class="font-medium">{{ model.quality }}</span>
                    </div>
                    <div class="flex items-center justify-between">
                      <span class="text-gray-500">Speed:</span>
                      <span :class="getSpeedClass(model.speed)" class="font-medium">{{ model.speed }}</span>
                    </div>
                  </div>
                  <div class="space-y-1">
                    <div class="text-gray-500">
                      <span class="font-medium">Rate Limits:</span>
                    </div>
                    <div class="text-xs text-gray-600">{{ model.rateLimits }}</div>
                  </div>
                </div>
              </div>
              <div class="flex-shrink-0">
                <div class="w-6 h-6 rounded-full border-2 transition-all duration-200"
                  :class="selectedModel === model.id ? 'border-primary-600 bg-primary-600' : 'border-gray-300'">
                  <div v-if="selectedModel === model.id" class="w-2 h-2 bg-white rounded-full m-auto mt-1"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Personality Selection Step -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="grid gap-4">
          <div v-for="personality in personalities" :key="personality.id"
            class="relative cursor-pointer rounded-xl border-2 p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] hover:border-primary-400"
            :class="{
              'border-primary-600 bg-primary-50 shadow-lg scale-[1.02]': selectedPersonality === personality.id,
              'border-gray-200 hover:border-gray-300': selectedPersonality !== personality.id
            }" @click="selectPersonality(personality.id)">
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0">
                <div
                  class="w-12 h-12 rounded-lg bg-gradient-to-br from-yellow-100 to-yellow-200 flex items-center justify-center text-2xl">
                  {{ personality.icon }}
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2 mb-2">
                  <h4 class="text-lg font-semibold text-gray-900">{{ personality.name }}</h4>
                  <span v-if="personality.id === 'career_savvy_colleague'"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
                    Default
                  </span>
                </div>
                <p class="text-sm text-gray-600">{{ personality.description }}</p>
              </div>
              <div class="flex-shrink-0">
                <div class="w-6 h-6 rounded-full border-2 transition-all duration-200"
                  :class="selectedPersonality === personality.id ? 'border-primary-600 bg-primary-600' : 'border-gray-300'">
                  <div v-if="selectedPersonality === personality.id" class="w-2 h-2 bg-white rounded-full m-auto mt-1">
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary Step -->
      <div v-if="currentStep === 3" class="step-content">
        <div class="bg-gradient-to-br from-primary-50 to-blue-50 rounded-xl p-8">
          <div class="text-center mb-6">
            <div class="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-white text-2xl">✓</span>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">Configuration Complete!</h3>
            <p class="text-gray-600">Your AI assistant is ready to help you create amazing resumes and cover letters.
            </p>
          </div>

          <div class="space-y-4">
            <div class="bg-white rounded-lg p-4 border border-gray-200">
              <div class="flex items-center space-x-3">
                <div
                  class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
                  {{ currentProvider.icon }}
                </div>
                <div>
                  <h4 class="font-medium text-gray-900">{{ currentProvider.name }}</h4>
                  <p class="text-sm text-gray-500">{{ currentModel.name }}</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-4 border border-gray-200">
              <div class="flex items-center space-x-3">
                <div
                  class="w-10 h-10 rounded-lg bg-gradient-to-br from-yellow-100 to-yellow-200 flex items-center justify-center">
                  {{ currentPersonality.icon }}
                </div>
                <div>
                  <h4 class="font-medium text-gray-900">{{ currentPersonality.name }}</h4>
                  <p class="text-sm text-gray-500">{{ currentPersonality.description }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Provider Info -->
          <div v-if="currentProvider.apiKeyRequired" class="mt-6 p-4 bg-white rounded-lg border border-gray-200">
            <h4 class="text-sm font-medium text-gray-900 mb-2">Provider Information</h4>
            <div class="text-sm text-gray-600 space-y-1">
              <p><span class="font-medium">Quality:</span> {{ currentModel.quality }}</p>
              <p><span class="font-medium">Speed:</span> {{ currentModel.speed }}</p>
              <p><span class="font-medium">Cost:</span> {{ currentProvider.cost }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
      <button v-if="currentStep > 0" @click="previousStep"
        class="px-6 py-3 text-gray-600 hover:text-gray-800 font-medium transition-all duration-200 hover:bg-gray-100 rounded-lg">
        ← Back
      </button>
      <div v-else></div>

      <button v-if="currentStep < steps.length - 1" @click="nextStep" :disabled="!canProceed"
        class="px-8 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl">
        {{ currentStep === steps.length - 2 ? 'Complete Setup' : 'Continue' }}
      </button>
      <div v-else></div>
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
const currentStep = ref(0)
const selectedProvider = ref(props.provider || 'gemini')
const selectedModel = ref(props.model || 'gemini-2.5-flash-lite')
const selectedPersonality = ref(props.personality || 'career_savvy_colleague')

// Steps configuration
const steps = ref([
  {
    id: 'provider',
    title: 'Choose Your AI Provider',
    description: 'Select the AI service that best fits your needs'
  },
  {
    id: 'model',
    title: 'Select Your Model',
    description: 'Choose the specific AI model for your tasks'
  },
  {
    id: 'personality',
    title: 'Pick Your Writing Style',
    description: 'Choose how your AI assistant should communicate'
  },
  {
    id: 'summary',
    title: 'Review & Complete',
    description: 'Review your configuration and get started'
  }
])

// Computed
const currentStepTitle = computed(() => steps.value[currentStep.value].title)
const currentStepDescription = computed(() => steps.value[currentStep.value].description)

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return selectedProvider.value
    case 1:
      return selectedModel.value
    case 2:
      return selectedPersonality.value
    default:
      return true
  }
})

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
        name: 'Gemini 2.5 Flash ❌',
        description: '⚠️ BROKEN - Does not generate any output. Use 2.5 Flash-Lite instead.',
        recommended: false,
        quality: 'Variable',
        speed: 'Fast',
        rateLimits: '10 RPM, 250 RPD (Free) / 1,000+ RPM (Paid)',
        warning: 'Broken'
      },
      {
        id: 'gemini-2.5-pro',
        name: 'Gemini 2.5 Pro ❌',
        description: '⚠️ BROKEN - 500 errors and API failures. Use 2.5 Flash-Lite instead.',
        recommended: false,
        quality: 'Variable',
        speed: 'Medium',
        rateLimits: '5 RPM, 100 RPD (Free) / 150+ RPM (Paid)',
        warning: 'Broken'
      },
      {
        id: 'gemini-1.5-flash',
        name: 'Gemini 1.5 Flash',
        description: '⚠️ Lower quality output - use for testing only. Prefer 2.5 Flash-Lite.',
        recommended: false,
        quality: 'Good',
        speed: 'Fast',
        rateLimits: '15 RPM, 1,500 RPD (Free) / 1,000+ RPM (Paid)',
        warning: 'Low Quality'
      },
      {
        id: 'gemini-1.5-pro-latest',
        name: 'Gemini 1.5 Pro',
        description: '⚠️ 500 errors due to low quota limits. Use sparingly.',
        recommended: false,
        quality: 'Highest',
        speed: 'Medium',
        rateLimits: '2 RPM, 50 RPD (Free) / 150+ RPM (Paid)',
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
        id: 'resume-editor:latest',
        name: '🎯 Resume Editor (Custom)',
        description: 'SPECIALIZED MODEL - Custom trained for resume and cover letter tailoring. Best choice for job applications.',
        recommended: true,
        quality: 'Excellent',
        speed: 'Medium',
        rateLimits: 'No limits (local)',
        badge: 'Specialized'
      },
      {
        id: 'qwen2.5:14b-instruct',
        name: 'Qwen 2.5 (14B)',
        description: 'Best general-purpose balance - excellent JSON parsing and company name recognition.',
        recommended: true,
        quality: 'High',
        speed: 'Fast',
        rateLimits: 'No limits (local)'
      },
      {
        id: 'llama3:8b',
        name: 'Llama 3.1 (8B)',
        description: 'Good general capability but may struggle with JSON parsing and company names.',
        recommended: false,
        quality: 'Good',
        speed: 'Fast',
        rateLimits: 'No limits (local)'
      },
      {
        id: 'mixtral:latest',
        name: 'Mixtral (Latest)',
        description: 'High-quality general model with excellent reasoning capabilities.',
        recommended: false,
        quality: 'High',
        speed: 'Medium',
        rateLimits: 'No limits (local)'
      },
      {
        id: 'phi3:mini',
        name: 'Phi-3 Mini (3.8B)',
        description: '⚠️ Limited capability - testing only. Struggles with complex JSON and company extraction.',
        recommended: false,
        quality: 'Basic',
        speed: 'Very Fast',
        rateLimits: 'No limits (local)'
      },
      {
        id: 'llama3.1:70b',
        name: 'Llama 3.1 (70B) ⚠️',
        description: 'BLOCKED - May freeze system due to resource requirements. Use quantized version if available.',
        recommended: false,
        quality: 'Highest',
        speed: 'Very Slow',
        rateLimits: 'No limits (local)',
        warning: true
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

const currentPersonality = computed(() => {
  return personalities.value.find(p => p.id === selectedPersonality.value) || personalities.value[0]
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
}

const selectPersonality = (personalityId) => {
  selectedPersonality.value = personalityId
}

const nextStep = () => {
  if (currentStep.value < steps.value.length - 1) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const getStepClass = (index) => {
  if (currentStep.value === index) {
    return 'bg-primary-600 border-primary-600'
  } else if (currentStep.value > index) {
    return 'bg-primary-600 border-primary-600'
  } else {
    return 'bg-white border-gray-300'
  }
}

// Auto-advance to next step when selection is made (with user preference)
const autoAdvance = ref(true) // Could be made configurable

watch(selectedProvider, (newProvider) => {
  if (newProvider && currentStep.value === 0 && autoAdvance.value) {
    // Auto-advance to model selection after a short delay
    setTimeout(() => {
      if (currentStep.value === 0) {
        nextStep()
      }
    }, 800) // Slightly longer delay for better UX
  }
})

watch(selectedModel, (newModel) => {
  if (newModel && currentStep.value === 1 && autoAdvance.value) {
    // Auto-advance to personality selection after a short delay
    setTimeout(() => {
      if (currentStep.value === 1) {
        nextStep()
      }
    }, 800)
  }
})

watch(selectedPersonality, (newPersonality) => {
  if (newPersonality && currentStep.value === 2 && autoAdvance.value) {
    // Auto-advance to summary after a short delay
    setTimeout(() => {
      if (currentStep.value === 2) {
        nextStep()
      }
    }, 800)
  }
})

const getQualityClass = (quality) => {
  const classes = {
    'Basic': 'text-gray-500',
    'Good': 'text-blue-600',
    'High': 'text-green-600',
    'Excellent': 'text-purple-700',
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
    'Very Slow': 'text-red-700',
    'Variable': 'text-gray-600'
  }
  return classes[speed] || 'text-gray-600'
}

const getWarningClass = (warningType) => {
  const classes = {
    'Broken': 'bg-red-100 text-red-800',
    'Low Quality': 'bg-yellow-100 text-yellow-800',
    'Quota Issues': 'bg-orange-100 text-orange-800',
    'Blocked': 'bg-red-100 text-red-800'
  }
  return classes[warningType] || 'bg-red-100 text-red-800'
}

const getWarningIcon = (warningType) => {
  const icons = {
    'Broken': '❌',
    'Low Quality': '⚠️',
    'Quota Issues': '⚠️',
    'Blocked': '🚫'
  }
  return icons[warningType] || '⚠️'
}
</script>

<style scoped>
.step-content {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>