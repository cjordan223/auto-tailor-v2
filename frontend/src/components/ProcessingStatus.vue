<template>
  <div class="card text-center">
    <!-- Status Icon -->
    <div class="mb-6">
      <div v-if="status === 'processing'" class="mx-auto w-16 h-16 text-primary-600">
        <svg class="animate-spin w-full h-full" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      
      <div v-else-if="status === 'completed'" class="mx-auto w-16 h-16 text-success-600">
        <svg class="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      
      <div v-else-if="status === 'error'" class="mx-auto w-16 h-16 text-error-600">
        <svg class="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      
      <div v-else class="mx-auto w-16 h-16 text-gray-400">
        <svg class="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
    </div>

    <!-- Status Text -->
    <div class="mb-6">
      <h3 class="text-xl font-semibold text-gray-900 mb-2">
        {{ statusText }}
      </h3>
      <p class="text-gray-600">
        {{ statusDescription }}
      </p>
    </div>

    <!-- Progress Bar -->
    <div v-if="status === 'processing'" class="mb-6">
      <div class="bg-gray-200 rounded-full h-2 mb-2">
        <div 
          class="bg-primary-600 h-2 rounded-full progress-bar"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
      <p class="text-sm text-gray-500">{{ progress }}% complete</p>
    </div>

    <!-- Processing Steps -->
    <div v-if="status === 'processing'" class="mb-6">
      <div class="space-y-2 text-left max-w-md mx-auto">
        <div 
          v-for="(step, index) in processingSteps"
          :key="index"
          class="flex items-center space-x-3"
          :class="{
            'text-primary-600': currentStep >= index,
            'text-gray-400': currentStep < index
          }"
        >
          <div class="flex-shrink-0">
            <svg v-if="currentStep > index" class="w-5 h-5 text-success-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <svg v-else-if="currentStep === index" class="w-5 h-5 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
            </svg>
            <div v-else class="w-5 h-5 rounded-full border-2 border-gray-300"></div>
          </div>
          <span class="text-sm">{{ step }}</span>
        </div>
      </div>
    </div>

    <!-- Error Details -->
    <div v-if="status === 'error' && error" class="mb-6 p-4 bg-error-50 rounded-lg text-left">
      <h4 class="text-sm font-medium text-error-800 mb-2">Error Details:</h4>
      <p class="text-sm text-error-700">{{ error }}</p>
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-center space-x-4">
      <button
        v-if="status === 'error'"
        @click="$emit('retry')"
        class="btn btn-primary"
      >
        Try Again
      </button>
      
      <button
        v-if="status === 'completed'"
        @click="$emit('view-results')"
        class="btn btn-success"
      >
        View Results
      </button>
      
      <button
        v-if="status === 'processing'"
        @click="$emit('cancel')"
        class="btn btn-secondary"
      >
        Cancel
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: 'idle' // idle, processing, completed, error
  },
  progress: {
    type: Number,
    default: 0
  },
  error: String
})

const emit = defineEmits(['retry', 'view-results', 'cancel'])

// Processing steps
const processingSteps = [
  'Uploading files...',
  'Extracting resume content...',
  'Analyzing job description...',
  'Generating AI recommendations...',
  'Applying changes to resume...',
  'Creating cover letter...',
  'Generating PDF files...'
]

// Current step based on progress
const currentStep = computed(() => {
  return Math.floor((props.progress / 100) * processingSteps.length)
})

// Status text and descriptions
const statusText = computed(() => {
  switch (props.status) {
    case 'processing':
      return 'Generating Your Resume...'
    case 'completed':
      return 'Resume Generated Successfully!'
    case 'error':
      return 'Generation Failed'
    default:
      return 'Ready to Process'
  }
})

const statusDescription = computed(() => {
  switch (props.status) {
    case 'processing':
      return 'AI is analyzing your job description and customizing your resume. This usually takes 30-60 seconds.'
    case 'completed':
      return 'Your tailored resume and cover letter are ready for download!'
    case 'error':
      return 'Something went wrong during processing. Please check the error details below.'
    default:
      return 'Click generate to start the AI customization process.'
  }
})
</script>