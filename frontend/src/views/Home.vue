<template>
  <div class="flex flex-col h-full space-y-6">
    <!-- Header -->
    <div class="text-center flex-shrink-0">
      <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
        AI-Powered Resume Customization
      </h1>
      <p class="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto">
        Upload a job description to get a perfectly tailored resume and cover letter using our pre-configured baseline template.
      </p>
    </div>

    <!-- Main Workflow -->
    <div class="max-w-4xl mx-auto flex-1 flex flex-col relative">
      <!-- Step Indicator -->
      <div class="mb-8">
        <div class="flex items-center justify-center space-x-4">
          <div class="flex items-center">
            <div class="flex items-center justify-center w-8 h-8 rounded-full" 
                 :class="step >= 1 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'">
              1
            </div>
            <span class="ml-2 text-sm font-medium text-gray-900">Job Description</span>
          </div>
          
          <div class="w-16 h-1 bg-gray-200 rounded" 
               :class="step >= 2 ? 'bg-primary-600' : 'bg-gray-200'"></div>
          
          <div class="flex items-center">
            <div class="flex items-center justify-center w-8 h-8 rounded-full"
                 :class="step >= 2 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'">
              2
            </div>
            <span class="ml-2 text-sm font-medium text-gray-900">Configure & Generate</span>
          </div>
        </div>
      </div>

      <!-- Step 1: Job Description Upload -->
      <div v-if="step === 1" class="flex-1 flex flex-col">
        <div class="max-w-2xl mx-auto flex-1 flex flex-col">
          <div class="flex-1">
            <FileUpload
              title="Job Description"
              description="Upload or paste the job description"
              accept=".txt,.pdf,.doc,.docx"
              icon="💼"
              @file-selected="handleJobUpload"
              @text-input="handleJobText"
              :file="jobFile"
              :allow-text-input="true"
            />
            
            <!-- Baseline Resume Info -->
            <div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-blue-800">
                    Using Pre-configured Baseline Resume
                  </h3>
                  <div class="mt-2 text-sm text-blue-700">
                    <p>Your resume will be customized using our baseline template with LLM markers. This ensures consistent formatting and optimal AI processing.</p>
                    <p class="mt-1 text-xs text-blue-600">
                      <em>Custom LaTeX template upload is planned for future releases.</em>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 2: Configuration -->
      <div v-if="step === 2" class="flex-1">
        <ProviderSelector
          v-model:provider="selectedProvider"
          v-model:model="selectedModel"
          @update="handleProviderUpdate"
        />
      </div>

      <!-- Step 3: Processing -->
      <div v-if="step === 3" class="flex-1">
        <ProcessingStatus
          :status="processingStatus"
          :progress="processingProgress"
          :error="processingError"
          :step="processingStep"
          :detail="processingDetail"
          :provider="processingProvider"
        />
      </div>

      <!-- Navigation Buttons - Positioned on sides -->
      <button
        v-if="step > 1"
        @click="previousStep"
        class="btn btn-secondary absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-8 md:-translate-x-16 hidden md:block"
      >
        Previous
      </button>
      
      <button
        v-if="step < 3"
        @click="nextStep"
        :disabled="!canProceed"
        class="btn btn-primary absolute right-0 top-1/2 transform -translate-y-1/2 translate-x-8 md:translate-x-16 hidden md:block"
        :class="{ 'opacity-50 cursor-not-allowed': !canProceed }"
      >
        {{ step === 2 ? 'Generate Resume' : 'Next' }}
      </button>
      
      <!-- Mobile Navigation Buttons - Bottom for small screens -->
      <div class="flex justify-between mt-8 md:hidden">
        <button
          v-if="step > 1"
          @click="previousStep"
          class="btn btn-secondary"
        >
          Previous
        </button>
        <div></div>
        
        <button
          v-if="step < 3"
          @click="nextStep"
          :disabled="!canProceed"
          class="btn btn-primary"
          :class="{ 'opacity-50 cursor-not-allowed': !canProceed }"
        >
          {{ step === 2 ? 'Generate Resume' : 'Next' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import FileUpload from '../components/FileUpload.vue'
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

    processingStatus.value = 'completed'
    processingProgress.value = 100

    // Navigate to results
    setTimeout(() => {
      router.push(`/results/${result.jobId}`)
    }, 1000)

  } catch (error) {
    processingStatus.value = 'error'
    processingError.value = error.message
  }
}
</script>