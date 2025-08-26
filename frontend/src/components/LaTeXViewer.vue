<template>
  <div class="latex-viewer-container">
    <div v-if="loading" class="latex-loading">
      <div class="text-center py-8">
        <div class="animate-spin w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full mx-auto mb-2"></div>
        <p class="text-sm text-gray-600">Loading LaTeX source...</p>
      </div>
    </div>
    
    <div v-else-if="error" class="latex-error">
      <div class="text-center py-8 text-red-600">
        <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-5-2h10l-5-2 5-2H7l5 2z"></path>
        </svg>
        <p class="text-sm mb-2">{{ error }}</p>
        <button @click="retryLoad" class="text-sm text-primary-600 hover:text-primary-800 underline">
          Try Again
        </button>
      </div>
    </div>
    
    <div v-else class="latex-viewer">
      <!-- Header with copy button -->
      <div class="latex-header">
        <span class="text-sm text-gray-600">LaTeX Source</span>
        <div class="flex items-center space-x-2">
          <span v-if="copied" class="text-sm text-green-600">Copied!</span>
          <button 
            @click="copyToClipboard" 
            class="text-sm text-primary-600 hover:text-primary-800 underline flex items-center"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
            Copy to Clipboard
          </button>
        </div>
      </div>
      
      <!-- LaTeX content area -->
      <div class="latex-content">
        <pre class="latex-code"><code ref="codeElement" v-html="highlightedContent"></code></pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
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

// State
const loading = ref(true)
const error = ref(null)
const latexContent = ref('')
const copied = ref(false)
const codeElement = ref(null)

// Computed
const latexUrl = computed(() => getApiUrl(`/view/${props.jobId}/${props.fileType}/tex`))

// Basic LaTeX syntax highlighting
const highlightedContent = computed(() => {
  if (!latexContent.value) return ''
  
  let highlighted = latexContent.value
    // Escape HTML first
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Commands
    .replace(/\\([a-zA-Z]+)/g, '<span class="latex-command">\\$1</span>')
    // Environments
    .replace(/\\(begin|end)\{([^}]+)\}/g, '<span class="latex-environment">\\$1{<span class="latex-env-name">$2</span>}</span>')
    // Comments
    .replace(/(%.*$)/gm, '<span class="latex-comment">$1</span>')
    // Braces
    .replace(/([{}])/g, '<span class="latex-brace">$1</span>')
    // Math mode
    .replace(/\$([^$]+)\$/g, '<span class="latex-math">$$1$</span>')
    // Optional arguments
    .replace(/(\[.*?\])/g, '<span class="latex-optional">$1</span>')
  
  // Add line numbers
  const lines = highlighted.split('\n')
  const numberedLines = lines.map((line, index) => 
    `<span class="line-number">${(index + 1).toString().padStart(3, ' ')}</span>${line}`
  )
  
  return numberedLines.join('\n')
})

// Methods
const loadLatexContent = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await fetch(latexUrl.value)
    if (!response.ok) {
      throw new Error(`Failed to load LaTeX source: ${response.statusText}`)
    }
    
    const content = await response.text()
    latexContent.value = content
  } catch (err) {
    console.error('LaTeX loading error:', err)
    error.value = err.message || 'Failed to load LaTeX source'
  } finally {
    loading.value = false
  }
}

const copyToClipboard = async () => {
  if (!latexContent.value) return
  
  try {
    await navigator.clipboard.writeText(latexContent.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = latexContent.value
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }
}

const retryLoad = () => {
  loadLatexContent()
}

// Lifecycle
onMounted(() => {
  if (props.jobId && props.fileType) {
    loadLatexContent()
  }
})
</script>

<style scoped>
.latex-viewer-container {
  width: 100%;
  height: 700px;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #f9fafb;
  display: flex;
  flex-direction: column;
}

.latex-loading,
.latex-error {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.latex-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.latex-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e5e7eb;
  border-radius: 0.5rem 0.5rem 0 0;
  flex-shrink: 0;
}

.latex-content {
  flex: 1;
  overflow: auto;
  background-color: white;
}

.latex-code {
  margin: 0;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: transparent;
  color: #1f2937;
}

/* Line numbers */
:deep(.line-number) {
  display: inline-block;
  width: 40px;
  color: #9ca3af;
  user-select: none;
  margin-right: 16px;
  text-align: right;
  border-right: 1px solid #e5e7eb;
  padding-right: 8px;
}

/* Syntax highlighting */
:deep(.latex-command) {
  color: #059669;
  font-weight: 600;
}

:deep(.latex-environment) {
  color: #dc2626;
  font-weight: 600;
}

:deep(.latex-env-name) {
  color: #7c2d12;
  font-weight: 600;
}

:deep(.latex-comment) {
  color: #6b7280;
  font-style: italic;
}

:deep(.latex-brace) {
  color: #4338ca;
  font-weight: 600;
}

:deep(.latex-math) {
  color: #b45309;
  background-color: #fef3c7;
  padding: 1px 2px;
  border-radius: 2px;
}

:deep(.latex-optional) {
  color: #7c3aed;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .latex-viewer-container {
    height: 500px;
  }
  
  .latex-code {
    font-size: 11px;
    padding: 12px;
  }
  
  :deep(.line-number) {
    width: 30px;
    margin-right: 8px;
    font-size: 10px;
  }
}

/* Scrollbar styling */
.latex-content::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.latex-content::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.latex-content::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.latex-content::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>