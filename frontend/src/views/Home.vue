<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="text-center mb-4">
      <h1 class="text-2xl md:text-3xl font-bold text-white mb-1 drop-shadow-lg">
        AI-Powered Resume Customization
      </h1>
      <p class="text-white/80 text-base">Configure your AI assistant and generate tailored resumes</p>
    </div>

    <!-- Processing View -->
    <div v-if="step === 3" class="flex-1">
      <ProcessingStatus :status="processingStatus" :progress="processingProgress" :error="processingError"
        :step="processingStep" :detail="processingDetail" :provider="processingProvider"
        @download-kit="handleDownloadKit" @open-resume="handleOpenResume" @open-cover-letter="handleOpenCoverLetter" />
    </div>

    <!-- Multi-Panel Layout -->
    <div v-else class="flex-1 max-w-7xl mx-auto w-full flex gap-4">
      <!-- Left Panel: Job Description -->
      <div class="w-1/2 flex flex-col">
        <div class="desktop-panel rounded-xl p-4 flex-1 flex flex-col">
          <div class="flex items-center mb-3">
            <div class="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center mr-2 shadow-md">
              <span class="text-white font-bold text-sm">1</span>
            </div>
            <h2 class="text-lg font-bold text-gray-900">Job Description</h2>
          </div>

          <div class="flex-1 min-h-0">
            <UnifiedInput placeholder="Paste your job description here or drag and drop a file..."
              accept=".txt,.pdf,.doc,.docx" @file-uploaded="handleJobUpload" @text-changed="handleJobText"
              @content-changed="handleContentChange" class="h-full" />
          </div>
        </div>
      </div>

      <!-- Right Panel: Configuration -->
      <div class="w-1/2 flex flex-col">
        <div class="desktop-panel rounded-xl p-4 flex-1 flex flex-col">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center">
              <div class="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center mr-2 shadow-md">
                <span class="text-white font-bold text-sm">2</span>
              </div>
              <h2 class="text-lg font-bold text-gray-900">AI Configuration</h2>
            </div>
          </div>

          <div class="flex-1 min-h-0 overflow-y-auto">
            <ModernProviderSelector v-model:provider="selectedProvider" v-model:model="selectedModel"
              v-model:personality="selectedPersonality" @update="handleProviderUpdate" />
          </div>
        </div>
      </div>
    </div>

    <!-- Generate Button - Always Visible -->
    <div v-if="step < 3" class="fixed bottom-6 right-6 z-50">
      <button @click="startProcessing" :disabled="!canProceed"
        class="generate-button text-white px-8 py-4 rounded-xl font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        :class="{ 'animate-pulse': canProceed }">
        <span class="flex items-center space-x-2">
          <span>✨</span>
          <span>Generate Resume</span>
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import UnifiedInput from '../components/UnifiedInput.vue'
import ModernProviderSelector from '../components/ModernProviderSelector.vue'
import ProcessingStatus from '../components/ProcessingStatus.vue'
import { useAPI } from '../composables/useAPI.js'
import { getFullUrl } from '../config/api.js'

const router = useRouter()
const { processResume, downloadAllAsZip } = useAPI()

// State
const step = ref(1)
const jobFile = ref(null)
const jobText = ref('')
const selectedProvider = ref('gemini')
const selectedModel = ref('gemini-2.5-flash-lite')
const selectedPersonality = ref('career_savvy_colleague')
const processingStatus = ref('idle')
const processingProgress = ref(0)
const processingError = ref(null)
const processingStep = ref('')
const processingDetail = ref('')
const processingProvider = ref('')
const currentJobId = ref(null)

// Computed - Updated for new single-view approach
const canProceed = computed(() => {
  return (jobFile.value || jobText.value) &&
    selectedProvider.value &&
    selectedModel.value &&
    selectedPersonality.value
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

const handleProviderUpdate = (provider, model, personality) => {
  selectedProvider.value = provider
  selectedModel.value = model
  selectedPersonality.value = personality
}

// Remove step navigation - no longer needed with single panel view

const startProcessing = async () => {
  try {
    processingStatus.value = 'processing'
    processingProgress.value = 0
    processingError.value = null

    const result = await processResume({
      jobDescription: jobText.value || jobFile.value,
      provider: selectedProvider.value,
      model: selectedModel.value,
      personality: selectedPersonality.value
    })

    currentJobId.value = result.jobId
    // Navigate directly to results page without setting completion status
    router.push(`/results/${result.jobId}`)

  } catch (error) {
    processingStatus.value = 'error'
    processingError.value = error.message

    // If it's a rate limit error, go back to step 2 so user can try again
    if (error.message.includes('Rate limit') || error.message.includes('Please wait')) {
      step.value = 2
    }
  }
}

// Event handlers for ProcessingStatus CTAs
const handleDownloadKit = async () => {
  if (currentJobId.value) {
    try {
      await downloadAllAsZip(currentJobId.value)
    } catch (error) {
      alert(`Failed to download zip file: ${error.message}`)
    }
  }
}

const handleOpenResume = () => {
  if (currentJobId.value) {
    // Open resume PDF in new tab
    window.open(getFullUrl(`/api/view/${currentJobId.value}/resume`), '_blank')
  }
}

const handleOpenCoverLetter = () => {
  if (currentJobId.value) {
    // Open cover letter PDF in new tab  
    window.open(getFullUrl(`/api/view/${currentJobId.value}/cover-letter`), '_blank')
  }
}
</script>