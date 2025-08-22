<template>
  <div class="pdf-viewer-container">
    <div v-if="loading" class="pdf-loading">
      <div class="text-center py-8">
        <div class="animate-spin w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full mx-auto mb-2"></div>
        <p class="text-sm text-gray-600">Loading PDF...</p>
      </div>
    </div>
    
    <div v-else-if="error" class="pdf-error">
      <div class="text-center py-8 text-red-600">
        <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-5-2h10l-5-2 5-2H7l5 2z"></path>
        </svg>
        <p class="text-sm">{{ error }}</p>
        <button @click="retry" class="mt-2 text-sm text-primary-600 hover:text-primary-800 underline">
          Try Again
        </button>
      </div>
    </div>
    
    <div v-else class="pdf-viewer">
      <!-- Primary method: iframe with object fallback -->
      <iframe 
        ref="pdfFrame"
        :src="pdfUrl"
        class="pdf-iframe"
        @load="onLoad"
        @error="onError"
      ></iframe>
      
      <!-- Fallback for browsers that don't support iframe PDF viewing -->
      <div v-if="showFallback" class="pdf-fallback">
        <div class="text-center py-8 bg-gray-50 rounded-lg">
          <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p class="text-gray-600 mb-3">PDF preview not supported in this browser</p>
          <a 
            :href="pdfUrl" 
            target="_blank" 
            class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
            </svg>
            Open PDF in New Tab
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

// Props
const props = defineProps({
  jobId: {
    type: String,
    required: true
  },
  fileType: {
    type: String,
    required: true,
    validator: (value) => ['resume', 'cover-letter'].includes(value)
  }
})

// State
const loading = ref(true)
const error = ref(null)
const showFallback = ref(false)
const pdfFrame = ref(null)
let loadTimeout = null

// Computed
const pdfUrl = computed(() => `/api/view/${props.jobId}/${props.fileType}`)

// Methods
const onLoad = () => {
  loading.value = false
  error.value = null
  showFallback.value = false
  clearTimeout(loadTimeout)
}

const onError = () => {
  loading.value = false
  error.value = 'Failed to load PDF'
  showFallback.value = true
  clearTimeout(loadTimeout)
}

const retry = () => {
  loading.value = true
  error.value = null
  showFallback.value = false
  
  // Reload the iframe
  if (pdfFrame.value) {
    pdfFrame.value.src = pdfUrl.value
  }
  
  // Set timeout for loading
  loadTimeout = setTimeout(() => {
    if (loading.value) {
      onError()
    }
  }, 10000) // 10 second timeout
}

// Lifecycle
onMounted(() => {
  // Set a timeout to show fallback if loading takes too long
  loadTimeout = setTimeout(() => {
    if (loading.value) {
      loading.value = false
      showFallback.value = true
    }
  }, 10000) // 10 second timeout
})

onBeforeUnmount(() => {
  clearTimeout(loadTimeout)
})
</script>

<style scoped>
.pdf-viewer-container {
  width: 100%;
  height: 400px;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #f9fafb;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background-color: white;
}

.pdf-loading,
.pdf-error,
.pdf-fallback {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pdf-viewer {
  height: 100%;
  position: relative;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .pdf-viewer-container {
    height: 300px;
  }
}
</style>