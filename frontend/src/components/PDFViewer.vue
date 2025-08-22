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
        <p class="text-sm mb-2">{{ error }}</p>
        <p class="text-xs text-gray-500 mb-3">Falling back to browser PDF viewer</p>
        <div class="space-y-2">
          <button @click="fallbackToIframe" class="text-sm text-primary-600 hover:text-primary-800 underline block">
            Use Browser Viewer
          </button>
          <button @click="openInNewTab" class="text-sm text-primary-600 hover:text-primary-800 underline block">
            Open in New Tab
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="pdf-viewer">
      <!-- Direct PDF link with preview -->
      <div class="pdf-preview-container">
        <div class="pdf-preview-header">
          <span class="text-sm text-gray-600">PDF Preview</span>
          <a 
            :href="pdfUrl" 
            target="_blank" 
            class="text-sm text-primary-600 hover:text-primary-800 underline"
          >
            Open in New Tab
          </a>
        </div>
        <div class="pdf-preview-content">
          <!-- Try object element first, fallback to iframe -->
          <object 
            ref="pdfFrame"
            :data="pdfUrl"
            type="application/pdf"
            class="pdf-iframe"
            @load="onLoad"
            @error="onError"
            title="PDF Viewer"
          >
            <iframe 
              :src="pdfUrl"
              class="pdf-iframe"
              @load="onLoad"
              @error="onError"
              title="PDF Viewer Fallback"
            ></iframe>
          </object>
        </div>
      </div>
      
      <!-- Fallback message for unsupported browsers -->
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
  console.log('PDF iframe load event fired')
  clearTimeout(loadTimeout)
  loading.value = false
  error.value = null
  showFallback.value = false
}

const onError = () => {
  console.log('PDF iframe error event fired')
  handlePDFError('PDF failed to load')
}

const checkPDFLoadStatus = () => {
  // For PDFs, we can't reliably check iframe content due to cross-origin restrictions
  // But we can assume it loaded if the iframe exists and no error occurred
  if (pdfFrame.value && loading.value) {
    console.log('PDF iframe exists, assuming it loaded successfully')
    onLoad()
  }
}

const handlePDFError = (message) => {
  console.log('PDF error:', message)
  loading.value = false
  error.value = message || 'PDF loading failed'
  clearTimeout(loadTimeout)
}



const fallbackToIframe = () => {
  error.value = null
  showFallback.value = false
  loading.value = true
  
  // Clear any existing timeout
  clearTimeout(loadTimeout)
  
  // Force reload by changing src
  if (pdfFrame.value) {
    const currentSrc = pdfFrame.value.src
    pdfFrame.value.src = ''
    setTimeout(() => {
      pdfFrame.value.src = currentSrc
    }, 100)
  }
  
  // Set timeout for loading
  loadTimeout = setTimeout(() => {
    if (loading.value) {
      loading.value = false
      showFallback.value = true
    }
  }, 10000) // 10 second timeout
}

const openInNewTab = () => {
  window.open(pdfUrl.value, '_blank')
}

const initializePDF = () => {
  console.log('Initializing PDF viewer for:', props.jobId, props.fileType)
  console.log('PDF URL:', pdfUrl.value)
  
  // Clear any existing timeout
  clearTimeout(loadTimeout)
  
  loading.value = true
  error.value = null
  showFallback.value = false
  
  // For PDFs, we'll assume they load successfully after a short delay
  // since many browsers don't fire proper load events for embedded PDFs
  setTimeout(() => {
    if (loading.value) {
      console.log('Assuming PDF loaded successfully (2 second assumption)')
      onLoad()
    }
  }, 2000)
  
  // Set a longer timeout for actual failure
  loadTimeout = setTimeout(() => {
    if (loading.value) {
      console.log('PDF loading timed out after 15 seconds')
      handlePDFError('PDF loading timed out')
    }
  }, 15000) // Increased back to 15 seconds for slow networks
}

// Lifecycle
onMounted(() => {
  if (props.jobId && props.fileType) {
    // Small delay to ensure component is fully mounted
    setTimeout(() => {
      initializePDF()
    }, 100)
  }
})

onBeforeUnmount(() => {
  clearTimeout(loadTimeout)
})
</script>

<style scoped>
.pdf-viewer-container {
  width: 100%;
  height: 700px;
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

.pdf-preview-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.pdf-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e5e7eb;
  border-radius: 0.5rem 0.5rem 0 0;
}

.pdf-preview-content {
  flex: 1;
  position: relative;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .pdf-viewer-container {
    height: 500px;
  }
}
</style>