<template>
  <div class="latex-editor-container">
    <!-- Loading State -->
    <div v-if="loading" class="latex-loading">
      <div class="text-center py-8">
        <div class="animate-spin w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full mx-auto mb-2"></div>
        <p class="text-sm text-gray-600">Loading LaTeX source...</p>
      </div>
    </div>
    
    <!-- Error State -->
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
    
    <!-- LaTeX Editor -->
    <div v-else class="latex-editor">
      <!-- Editor Toolbar -->
      <div class="latex-toolbar">
        <div class="flex items-center justify-between">
          <!-- Left side: Status and info -->
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">LaTeX Editor</span>
            <div class="flex items-center space-x-2">
              <div 
                class="w-2 h-2 rounded-full" 
                :class="statusIndicatorClass"
                :title="statusMessage"
              ></div>
              <span class="text-xs text-gray-500">{{ statusMessage }}</span>
            </div>
          </div>
          
          <!-- Right side: Action buttons -->
          <div class="flex items-center space-x-2">
            <span v-if="copied" class="text-sm text-green-600 animate-fade-in">Copied!</span>
            <button 
              @click="copyToClipboard" 
              class="editor-button"
              title="Copy to clipboard"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </button>
            <button 
              @click="saveChanges" 
              :disabled="!hasUnsavedChanges"
              class="editor-button"
              :class="{ 'opacity-50 cursor-not-allowed': !hasUnsavedChanges }"
              title="Save changes"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
            </button>
            <button 
              @click="revertChanges"
              :disabled="!hasUnsavedChanges"
              class="editor-button text-red-600 hover:text-red-700"
              :class="{ 'opacity-50 cursor-not-allowed': !hasUnsavedChanges }"
              title="Revert changes"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Monaco Editor -->
      <div class="editor-content">
        <VueMonacoEditor
          v-model:value="latexContent"
          language="latex"
          :options="editorOptions"
          :height="editorHeight"
          @mount="onEditorMount"
          @change="onContentChange"
          class="monaco-editor"
        />
      </div>
      
      <!-- Auto-save indicator -->
      <div v-if="autoSaveStatus" class="auto-save-indicator">
        <span class="text-xs text-gray-500">{{ autoSaveStatus }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'

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
  },
  height: {
    type: [String, Number],
    default: 700
  }
})

// Emits
const emit = defineEmits(['content-changed', 'save', 'revert'])

// State
const loading = ref(true)
const error = ref(null)
const latexContent = ref('')
const originalContent = ref('')
const copied = ref(false)
const autoSaveStatus = ref('')
const editor = ref(null)

// Auto-save functionality
let autoSaveTimeout = null
const AUTO_SAVE_DELAY = 30000 // 30 seconds

// Computed
const latexUrl = computed(() => `/api/view/${props.jobId}/${props.fileType}/tex`)
const editorHeight = computed(() => typeof props.height === 'number' ? `${props.height}px` : props.height)

const hasUnsavedChanges = computed(() => {
  return latexContent.value !== originalContent.value
})

const statusIndicatorClass = computed(() => {
  if (hasUnsavedChanges.value) {
    return 'bg-yellow-500' // Unsaved changes
  }
  return 'bg-green-500' // Saved
})

const statusMessage = computed(() => {
  if (hasUnsavedChanges.value) {
    return 'Unsaved changes'
  }
  return 'All changes saved'
})

// Monaco Editor configuration
const editorOptions = {
  theme: 'vs',
  fontSize: 14,
  fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
  lineNumbers: 'on',
  rulers: [80],
  wordWrap: 'on',
  scrollBeyondLastLine: false,
  automaticLayout: true,
  tabSize: 2,
  insertSpaces: true,
  detectIndentation: false,
  minimap: {
    enabled: false
  },
  scrollbar: {
    verticalScrollbarSize: 8,
    horizontalScrollbarSize: 8
  },
  overviewRulerLanes: 0,
  lineDecorationsWidth: 0,
  folding: true,
  renderWhitespace: 'boundary',
  bracketPairColorization: {
    enabled: true
  }
}

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
    originalContent.value = content
    
    console.log('LaTeX content loaded successfully')
  } catch (err) {
    console.error('LaTeX loading error:', err)
    error.value = err.message || 'Failed to load LaTeX source'
  } finally {
    loading.value = false
  }
}

const onEditorMount = (editorInstance) => {
  editor.value = editorInstance
  console.log('Monaco editor mounted')
  
  // Configure LaTeX language support
  configureLatexLanguage()
}

const configureLatexLanguage = () => {
  // This would be where we add LaTeX syntax highlighting if needed
  // Monaco has basic LaTeX support built-in
}

const onContentChange = () => {
  emit('content-changed', latexContent.value)
  scheduleAutoSave()
}

const scheduleAutoSave = () => {
  if (autoSaveTimeout) {
    clearTimeout(autoSaveTimeout)
  }
  
  autoSaveTimeout = setTimeout(() => {
    if (hasUnsavedChanges.value) {
      autoSave()
    }
  }, AUTO_SAVE_DELAY)
}

const autoSave = () => {
  autoSaveStatus.value = 'Auto-saving...'
  
  // Simulate auto-save (in Phase 2, this will be real)
  setTimeout(() => {
    autoSaveStatus.value = 'Auto-saved'
    setTimeout(() => {
      autoSaveStatus.value = ''
    }, 2000)
  }, 500)
}

const saveChanges = async () => {
  try {
    // Update original content to mark as saved
    originalContent.value = latexContent.value
    emit('save', latexContent.value)
    
    console.log('Changes saved')
  } catch (err) {
    console.error('Save error:', err)
    error.value = 'Failed to save changes'
  }
}

const revertChanges = () => {
  latexContent.value = originalContent.value
  emit('revert', originalContent.value)
  console.log('Changes reverted')
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

// Watch for prop changes
watch(() => props.jobId, () => {
  if (props.jobId) {
    loadLatexContent()
  }
})

watch(() => props.fileType, () => {
  if (props.fileType) {
    loadLatexContent()
  }
})

// Lifecycle
onMounted(() => {
  if (props.jobId && props.fileType) {
    loadLatexContent()
  }
})
</script>

<style scoped>
.latex-editor-container {
  width: 100%;
  height: v-bind(editorHeight);
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

.latex-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.latex-toolbar {
  flex-shrink: 0;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e5e7eb;
  border-radius: 0.5rem 0.5rem 0 0;
}

.editor-button {
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #d1d5db;
  background-color: white;
  color: #374151;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.editor-button:hover:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.editor-content {
  flex: 1;
  position: relative;
  background-color: white;
}

.monaco-editor {
  height: 100%;
  width: 100%;
}

.auto-save-indicator {
  position: absolute;
  bottom: 8px;
  right: 12px;
  padding: 2px 6px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 3px;
  font-size: 11px;
  pointer-events: none;
}

/* Animation for copied indicator */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .latex-editor-container {
    height: 500px;
  }
  
  .latex-toolbar {
    padding: 6px 8px;
  }
  
  .editor-button {
    padding: 3px 6px;
  }
}
</style>