<template>
  <div class="pdf-viewer-container">
    <div v-if="loading" class="pdf-loading">
      <div class="text-center py-8">
        <div class="animate-spin w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full mx-auto mb-2">
        </div>
        <p class="text-sm text-gray-600">Loading PDF...</p>
      </div>
    </div>

    <div v-else-if="error" class="pdf-error">
      <div class="text-center py-8 text-red-600">
        <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 9v2m0 4h.01m-5-2h10l-5-2 5-2H7l5 2z"></path>
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
          <div class="flex space-x-3">
            <button @click="openInModal" class="text-sm text-primary-600 hover:text-primary-800 underline">
              View in Modal
            </button>
            <a :href="pdfUrl" target="_blank" class="text-sm text-primary-600 hover:text-primary-800 underline">
              Open in New Tab
            </a>
          </div>
        </div>
        <div class="pdf-preview-content">
          <!-- Try object element first, fallback to iframe -->
          <object ref="pdfFrame" :data="pdfUrl" type="application/pdf" class="pdf-iframe" @load="onLoad"
            @error="onError" title="PDF Viewer">
            <iframe :src="pdfUrl" class="pdf-iframe" @load="onLoad" @error="onError"
              title="PDF Viewer Fallback"></iframe>
          </object>
        </div>
      </div>

      <!-- Fallback message for unsupported browsers -->
      <div v-if="showFallback" class="pdf-fallback">
        <div class="text-center py-8 bg-gray-50 rounded-lg">
          <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z">
            </path>
          </svg>
          <p class="text-gray-600 mb-3">PDF preview not supported in this browser</p>
          <a :href="pdfUrl" target="_blank"
            class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
            </svg>
            Open PDF in New Tab
          </a>
        </div>
      </div>
    </div>

    <!-- PDF Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto" @click="closeModal">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
        
        <!-- Modal panel -->
        <div class="relative inline-block w-full max-w-6xl p-6 my-8 text-left align-middle bg-white rounded-lg shadow-xl transform transition-all" @click.stop>
          <!-- Modal header -->
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ fileType === 'resume' ? 'Resume' : 'Cover Letter' }} PDF Preview
            </h3>
            <div class="flex space-x-3">
              <a :href="pdfUrl" target="_blank" class="text-sm text-primary-600 hover:text-primary-800 underline">
                Open in New Tab
              </a>
              <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Modal content -->
          <div class="pdf-modal-content">
            <object :data="pdfUrl" type="application/pdf" class="pdf-modal-iframe" title="PDF Modal Viewer">
              <iframe :src="pdfUrl" class="pdf-modal-iframe" title="PDF Modal Viewer Fallback"></iframe>
            </object>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { getApiUrl } from '../config/api.js'

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

// Emits
const emit = defineEmits(['refreshed'])

// State
const loading = ref(true)
const error = ref(null)
const showFallback = ref(false)
const pdfFrame = ref(null)
const showModal = ref(false)
let loadTimeout = null

// State for cache busting
const cacheBuster = ref(Date.now())
const refreshId = ref(0)

// Computed
const pdfUrl = computed(() => {
  const baseUrl = getApiUrl(`/view/${props.jobId}/${props.fileType}`)
  // Add comprehensive parameters to hide the sidebar by default in browser PDF viewers
  // These parameters work across different PDF viewers (Chrome, Firefox, Safari, etc.)
  const random = Math.random().toString(36).substring(7)
  return `${baseUrl}?t=${cacheBuster.value}&v=${Date.now()}&r=${refreshId.value}&cb=${random}#toolbar=1&navpanes=0&scrollbar=1&view=FitH&pagemode=none&statusbar=0&messages=0&viewrect=0,0,800,600`
})

// Methods
const onLoad = () => {
  console.log('PDF iframe load event fired')
  clearTimeout(loadTimeout)
  loading.value = false
  error.value = null
  showFallback.value = false
  emit('refreshed')

  // Check if the PDF actually loaded content
  setTimeout(() => {
    if (pdfFrame.value) {
      try {
        // Try to access iframe content to verify it loaded
        console.log('PDF iframe loaded successfully')
      } catch (err) {
        console.log('PDF iframe content check failed:', err.message)
      }
    }
  }, 100)
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

const openInModal = () => {
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

// Handle escape key to close modal
const handleKeydown = (event) => {
  if (event.key === 'Escape' && showModal.value) {
    closeModal()
  }
}

// Add/remove event listeners for modal
watch(showModal, (newValue) => {
  if (newValue) {
    document.addEventListener('keydown', handleKeydown)
    document.body.style.overflow = 'hidden' // Prevent body scroll
  } else {
    document.removeEventListener('keydown', handleKeydown)
    document.body.style.overflow = '' // Restore body scroll
  }
})

const forceRefresh = async () => {
  console.log('Forcing PDF refresh with enhanced cache busting...')
  loading.value = true
  error.value = null

  // Clear any existing timeout
  clearTimeout(loadTimeout)

  // Enhanced cache busting with multiple strategies
  cacheBuster.value = Date.now()
  refreshId.value++

  console.log('Enhanced PDF refresh:', {
    cacheBuster: cacheBuster.value,
    refreshId: refreshId.value,
    jobId: props.jobId,
    fileType: props.fileType
  })

  // Import the enhanced URL generation
  try {
    const { generatePdfUrl } = await import('../utils/pdf-utils.js')
    const enhancedUrl = generatePdfUrl(props.jobId, props.fileType, cacheBuster.value, refreshId.value)

    console.log('Generated enhanced PDF URL:', enhancedUrl)

    // More aggressive iframe reset
    if (pdfFrame.value) {
      // Method 1: Clear everything and wait longer
      pdfFrame.value.src = 'about:blank'
      pdfFrame.value.data = 'about:blank'

      // Force browser to forget cached content
      await new Promise(resolve => setTimeout(resolve, 300))

      // Method 2: Try to force a complete reload
      pdfFrame.value.src = enhancedUrl
      pdfFrame.value.data = enhancedUrl

      console.log('PDF iframe src updated with enhanced URL')
    }
  } catch (err) {
    console.warn('Failed to import PDF utils, using fallback URL generation:', err)
    // Fallback to original method if import fails
    const newUrl = pdfUrl.value
    if (pdfFrame.value) {
      pdfFrame.value.src = ''
      pdfFrame.value.data = ''
      setTimeout(() => {
        pdfFrame.value.src = newUrl
        pdfFrame.value.data = newUrl
      }, 300)
    }
  }

  // Set a reasonable timeout for PDF loading with better feedback
  loadTimeout = setTimeout(() => {
    if (loading.value) {
      console.log('PDF assumed loaded after timeout - this may indicate caching issues')
      onLoad()
    }
  }, 4000) // Slightly longer timeout for reliability
}

// Expose methods to parent (moved here after forceRefresh is declared)
defineExpose({
  forceRefresh
})

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

// Watchers
watch(() => props.jobId, () => {
  if (props.jobId && props.fileType) {
    console.log('Job ID changed, refreshing PDF viewer')
    forceRefresh()
  }
})

watch(() => props.fileType, () => {
  if (props.jobId && props.fileType) {
    console.log('File type changed, refreshing PDF viewer')
    forceRefresh()
  }
})

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
  // Clean up modal event listeners
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
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

/* Modal styles */
.pdf-modal-content {
  width: 100%;
  height: 80vh;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  overflow: hidden;
}

.pdf-modal-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background-color: white;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .pdf-viewer-container {
    height: 500px;
  }
  
  .pdf-modal-content {
    height: 70vh;
  }
}
</style>