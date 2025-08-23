<template>
  <div class="flex flex-col h-full space-y-4">
    <!-- Header -->
    <div class="text-center flex-shrink-0 mb-4">
      <h1 class="text-3xl md:text-4xl font-bold text-white mb-3 drop-shadow-lg">
        AI-Powered Resume Customization
      </h1>

    </div>

    <!-- Main Workflow -->
    <div class="max-w-4xl mx-auto flex-1 flex flex-col relative">
      <!-- Step Indicator -->
      <div class="mb-6">
        <div class="flex items-center justify-center space-x-6">
          <div class="flex items-center space-x-2">
            <div
              class="step-indicator flex items-center justify-center w-10 h-10 rounded-xl font-bold text-base transition-all duration-300"
              :class="step >= 1 ? 'bg-gradient-to-br from-blue-500 to-blue-700 text-white shadow-xl animate-glow' : 'glassmorphism-card text-gray-500'">
              1
            </div>
          </div>

          <div class="w-16 h-1.5 rounded-full transition-all duration-500"
            :class="step >= 2 ? 'progress-bar' : 'bg-white/20'"></div>

          <div class="flex items-center space-x-2">
            <div
              class="step-indicator flex items-center justify-center w-10 h-10 rounded-xl font-bold text-base transition-all duration-300"
              :class="step >= 2 ? 'bg-gradient-to-br from-blue-500 to-blue-700 text-white shadow-xl animate-glow' : 'glassmorphism-card text-gray-500'">
              2
            </div>
            <span class="text-sm font-semibold text-white">Configure & Generate</span>
          </div>
        </div>
      </div>

      <!-- Step 1: Job Description Upload -->
      <div v-if="step === 1" class="flex-1 flex flex-col">
        <div class="max-w-4xl mx-auto flex-1 flex flex-col space-y-4">
          <!-- Job Description Input Header -->
          <div class="text-center">
            <h2 class="text-2xl font-bold text-white mb-2 drop-shadow-lg">Job Description</h2>
          </div>

          <!-- Unified Input Component - Exact dimensions -->
          <div class="flex-1 flex justify-center">
            <div class="w-[1300px] h-[546px] flex-shrink-0">
              <UnifiedInput placeholder="Paste your job description here or drag and drop a file..."
                accept=".txt,.pdf,.doc,.docx" @file-uploaded="handleJobUpload" @text-changed="handleJobText"
                @content-changed="handleContentChange" />
            </div>
          </div>
        </div>
      </div>

      <!-- Step 2: Configuration -->
      <div v-if="step === 2" class="flex-1">
        <ProviderSelector v-model:provider="selectedProvider" v-model:model="selectedModel"
          @update="handleProviderUpdate" />
      </div>

      <!-- Step 3: Processing -->
      <div v-if="step === 3" class="flex-1">
        <ProcessingStatus :status="processingStatus" :progress="processingProgress" :error="processingError"
          :step="processingStep" :detail="processingDetail" :provider="processingProvider" 
          @download-kit="handleDownloadKit" @open-resume="handleOpenResume" @open-cover-letter="handleOpenCoverLetter" />
      </div>

      <!-- Navigation Buttons - Fixed positioning to prevent layout shifts -->
      <div class="absolute bottom-0 left-0 right-0 flex justify-center pb-4">
        <div class="flex space-x-4">
          <button v-if="step > 1" @click="previousStep" class="btn btn-secondary">
            Previous
          </button>
          <button v-if="step < 3" @click="nextStep" :disabled="!canProceed" class="btn btn-primary"
            :class="{ 'opacity-50 cursor-not-allowed': !canProceed }">
            {{ step === 2 ? 'Generate Resume' : 'Next' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import UnifiedInput from '../components/UnifiedInput.vue'
import ProviderSelector from '../components/ProviderSelector.vue'
import ProcessingStatus from '../components/ProcessingStatus.vue'
import { useAPI } from '../composables/useAPI.js'

const router = useRouter()
const { processResume } = useAPI()

// State
const step = ref(1)
const jobFile = ref(null)
const jobText = ref('')
const selectedProvider = ref('gemini')
const selectedModel = ref('gemini-1.5-flash')
const processingStatus = ref('idle')
const processingProgress = ref(0)
const processingError = ref(null)
const processingStep = ref('')
const processingDetail = ref('')
const processingProvider = ref('')
const currentJobId = ref(null)

// Computed
const canProceed = computed(() => {
  if (step.value === 1) {
    return jobFile.value || jobText.value
  }
  if (step.value === 2) {
    return selectedProvider.value && selectedModel.value
  }
  return false
})

// Methods
const handleJobUpload = (file) => {
  jobFile.value = file
  jobText.value = '' // Clear text input when file is uploaded
}

const handleJobText = (text) => {
  jobText.value = text
  jobFile.value = null // Clear file when text is entered
}

const handleContentChange = ({ text, file }) => {
  jobText.value = text || ''
  jobFile.value = file
}

const handleProviderUpdate = (provider, model) => {
  selectedProvider.value = provider
  selectedModel.value = model
}

const previousStep = () => {
  if (step.value > 1) {
    step.value--
  }
}

const nextStep = async () => {
  if (step.value === 2) {
    // Start processing
    step.value = 3
    await startProcessing()
  } else if (step.value < 3) {
    step.value++
  }
}

const startProcessing = async () => {
  try {
    processingStatus.value = 'processing'
    processingProgress.value = 0
    processingError.value = null

    const result = await processResume({
      jobDescription: jobText.value || jobFile.value,
      provider: selectedProvider.value,
      model: selectedModel.value
    })

    currentJobId.value = result.jobId
    // Navigate directly to results page without setting completion status
    router.push(`/results/${result.jobId}`)

  } catch (error) {
    processingStatus.value = 'error'
    processingError.value = error.message
  }
}

// Event handlers for ProcessingStatus CTAs
const handleDownloadKit = () => {
  if (currentJobId.value) {
    // Navigate to results page which has download all functionality
    router.push(`/results/${currentJobId.value}`)
  }
}

const handleOpenResume = () => {
  if (currentJobId.value) {
    // Open resume PDF in new tab
    window.open(`/api/view/${currentJobId.value}/resume`, '_blank')
  }
}

const handleOpenCoverLetter = () => {
  if (currentJobId.value) {
    // Open cover letter PDF in new tab  
    window.open(`/api/view/${currentJobId.value}/cover-letter`, '_blank')
  }
}
</script>