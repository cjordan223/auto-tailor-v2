<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">
        AI-Powered Resume Customization
      </h1>
      <p class="text-xl text-gray-600 max-w-3xl mx-auto">
        Upload your resume template and job description to get a perfectly tailored resume and cover letter in seconds.
      </p>
    </div>

    <!-- Main Workflow -->
    <div class="max-w-4xl mx-auto">
      <!-- Step Indicator -->
      <div class="mb-8">
        <div class="flex items-center justify-center space-x-4">
          <div class="flex items-center">
            <div class="flex items-center justify-center w-8 h-8 rounded-full" 
                 :class="step >= 1 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'">
              1
            </div>
            <span class="ml-2 text-sm font-medium text-gray-900">Upload Files</span>
          </div>
          
          <div class="w-16 h-1 bg-gray-200 rounded" 
               :class="step >= 2 ? 'bg-primary-600' : 'bg-gray-200'"></div>
          
          <div class="flex items-center">
            <div class="flex items-center justify-center w-8 h-8 rounded-full"
                 :class="step >= 2 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'">
              2
            </div>
            <span class="ml-2 text-sm font-medium text-gray-900">Configure</span>
          </div>
          
          <div class="w-16 h-1 bg-gray-200 rounded"
               :class="step >= 3 ? 'bg-primary-600' : 'bg-gray-200'"></div>
          
          <div class="flex items-center">
            <div class="flex items-center justify-center w-8 h-8 rounded-full"
                 :class="step >= 3 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'">
              3
            </div>
            <span class="ml-2 text-sm font-medium text-gray-900">Generate</span>
          </div>
        </div>
      </div>

      <!-- Step 1: File Upload -->
      <div v-if="step === 1" class="grid md:grid-cols-2 gap-6 mb-8">
        <FileUpload
          title="Resume Template"
          description="Upload your LaTeX resume template"
          accept=".tex,.txt"
          icon="📄"
          @file-selected="handleResumeUpload"
          :file="resumeFile"
        />
        
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
      </div>

      <!-- Step 2: Configuration -->
      <div v-if="step === 2" class="mb-8">
        <ProviderSelector
          v-model:provider="selectedProvider"
          v-model:model="selectedModel"
          @update="handleProviderUpdate"
        />
      </div>

      <!-- Step 3: Processing -->
      <div v-if="step === 3" class="mb-8">
        <ProcessingStatus
          :status="processingStatus"
          :progress="processingProgress"
          :error="processingError"
        />
      </div>

      <!-- Navigation Buttons -->
      <div class="flex justify-between">
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
const resumeFile = ref(null)
const jobFile = ref(null) 
const jobText = ref('')
const selectedProvider = ref('gemini')
const selectedModel = ref('gemini-1.5-flash')
const processingStatus = ref('idle')
const processingProgress = ref(0)
const processingError = ref(null)

// Computed
const canProceed = computed(() => {
  if (step.value === 1) {
    return resumeFile.value && (jobFile.value || jobText.value)
  }
  if (step.value === 2) {
    return selectedProvider.value && selectedModel.value
  }
  return false
})

// Methods
const handleResumeUpload = (file) => {
  resumeFile.value = file
}

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
      resumeFile: resumeFile.value,
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