<template>
  <div class="unified-input-container">
    <div ref="dropzoneRef" class="unified-input glassmorphism" :class="{
      'drag-active': isDragActive,
      'has-content': hasContent,
      'glow-active': isActive
    }" @click="handleClick">
      <!-- File upload icon -->
      <div class="upload-icon" @click.stop="triggerFileInput" v-if="!hasContent">
        <svg class="icon-paperclip" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
        </svg>
      </div>

      <!-- Main text area -->
      <textarea ref="textareaRef" v-model="textContent" :placeholder="placeholder" class="main-textarea"
        :class="{ 'with-file': uploadedFile }" @focus="handleFocus" @blur="handleBlur" @input="handleTextInput"
        @paste="handlePaste" />

      <!-- File chip display -->
      <div v-if="uploadedFile" class="file-chip">
        <div class="file-info">
          <svg class="file-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <span class="file-name">{{ uploadedFile.name }}</span>
          <span class="file-size">({{ formatFileSize(uploadedFile.size) }})</span>
        </div>
        <button @click.stop="removeFile" class="remove-file-btn">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Drop overlay -->
      <div v-if="isDragActive" class="drop-overlay">
        <div class="drop-content">
          <svg class="drop-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="drop-text">Drop your file here</p>
        </div>
      </div>
    </div>

    <!-- Hidden file input -->
    <input ref="fileInputRef" type="file" :accept="accept" @change="handleFileSelect" style="display: none;" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  placeholder: {
    type: String,
    default: 'Paste your job description here or drag and drop a file...'
  },
  accept: {
    type: String,
    default: '.txt,.pdf,.doc,.docx'
  },
  maxFileSize: {
    type: Number,
    default: 10 * 1024 * 1024 // 10MB
  }
})

const emit = defineEmits(['file-uploaded', 'text-changed', 'content-changed'])

// Refs
const dropzoneRef = ref(null)
const textareaRef = ref(null)
const fileInputRef = ref(null)

// State
const textContent = ref('')
const uploadedFile = ref(null)
const isDragActive = ref(false)
const isActive = ref(false)
const dragCounter = ref(0)

// Computed
const hasContent = computed(() => textContent.value.trim() || uploadedFile.value)

// Methods
const handleClick = () => {
  if (!hasContent.value) {
    textareaRef.value?.focus()
  }
}

const handleFocus = () => {
  isActive.value = true
}

const handleBlur = () => {
  isActive.value = false
}

const handleTextInput = () => {
  if (uploadedFile.value && textContent.value.trim()) {
    // Clear file when user starts typing
    uploadedFile.value = null
    emit('file-uploaded', null)
  }
  emit('text-changed', textContent.value)
  emit('content-changed', { text: textContent.value, file: uploadedFile.value })
}

const handlePaste = async (event) => {
  const items = event.clipboardData.items
  for (let item of items) {
    if (item.kind === 'file') {
      event.preventDefault()
      const file = item.getAsFile()
      await validateAndSetFile(file)
      break
    }
  }
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (file) {
    await validateAndSetFile(file)
  }
}

const validateAndSetFile = async (file) => {
  // Validate file type
  const acceptedExtensions = props.accept.split(',').map(ext => ext.trim().toLowerCase())
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase()

  if (!acceptedExtensions.includes(fileExtension)) {
    alert(`File type not supported. Please upload: ${props.accept}`)
    return
  }

  // Validate file size
  if (file.size > props.maxFileSize) {
    alert(`File size must be less than ${Math.round(props.maxFileSize / (1024 * 1024))}MB`)
    return
  }

  // If there's text content, clear it
  if (textContent.value.trim()) {
    textContent.value = ''
    emit('text-changed', '')
  }

  uploadedFile.value = file
  emit('file-uploaded', file)
  emit('content-changed', { text: textContent.value, file: file })
}

const removeFile = () => {
  uploadedFile.value = null
  fileInputRef.value.value = ''
  emit('file-uploaded', null)
  emit('content-changed', { text: textContent.value, file: null })
  textareaRef.value?.focus()
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Drag and drop handlers
const handleDragEnter = (e) => {
  e.preventDefault()
  dragCounter.value++
  if (e.dataTransfer.types.includes('Files')) {
    isDragActive.value = true
  }
}

const handleDragLeave = (e) => {
  e.preventDefault()
  dragCounter.value--
  if (dragCounter.value === 0) {
    isDragActive.value = false
  }
}

const handleDragOver = (e) => {
  e.preventDefault()
}

const handleDrop = async (e) => {
  e.preventDefault()
  isDragActive.value = false
  dragCounter.value = 0

  const files = e.dataTransfer.files
  if (files.length > 0) {
    await validateAndSetFile(files[0])
  }
}

// Lifecycle
onMounted(() => {
  const element = dropzoneRef.value
  if (element) {
    element.addEventListener('dragenter', handleDragEnter)
    element.addEventListener('dragleave', handleDragLeave)
    element.addEventListener('dragover', handleDragOver)
    element.addEventListener('drop', handleDrop)
  }
})

onUnmounted(() => {
  const element = dropzoneRef.value
  if (element) {
    element.removeEventListener('dragenter', handleDragEnter)
    element.removeEventListener('dragleave', handleDragLeave)
    element.removeEventListener('dragover', handleDragOver)
    element.removeEventListener('drop', handleDrop)
  }
})
</script>

<style scoped>
.unified-input-container {
  @apply relative w-full max-w-4xl mx-auto;
}

.unified-input {
  @apply relative w-full h-full rounded-2xl border-2 border-gray-200/50 transition-all duration-300 ease-in-out cursor-text overflow-hidden;
  backdrop-filter: blur(10px);
  background: rgba(15, 23, 42, 0.6);
  border: 2px solid rgba(34, 197, 94, 0.1);
  min-height: 400px !important;
  height: 400px !important;
}

.glassmorphism {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(34, 197, 94, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.unified-input:hover {
  border-color: rgba(34, 197, 94, 0.2);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
}

.unified-input.glow-active,
.unified-input.drag-active {
  border-color: rgba(34, 197, 94, 0.4);
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.1), 0 12px 40px rgba(34, 197, 94, 0.3);
  background: rgba(15, 23, 42, 0.8);
}

.upload-icon {
  @apply absolute top-4 right-4 p-2 rounded-lg bg-white/60 hover:bg-white/80 cursor-pointer transition-all duration-200;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.upload-icon:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
}

.icon-paperclip {
  @apply w-5 h-5 text-green-400;
}

.main-textarea {
  @apply w-full h-full p-4 bg-transparent border-none outline-none resize-none text-gray-900 placeholder-gray-500 text-base leading-relaxed;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  min-height: 400px !important;
  height: 400px !important;
  background: rgba(15, 23, 42, 0.6) !important;
  color: #e2e8f0 !important;
}

.main-textarea:focus {
  background: rgba(15, 23, 42, 0.8) !important;
  color: #f1f5f9 !important;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

.main-textarea::placeholder {
  color: #64748b !important;
}

.main-textarea.with-file {
  @apply pt-16;
}

.file-chip {
  @apply absolute top-4 left-4 flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200;
  background: rgba(34, 197, 94, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.file-info {
  @apply flex items-center space-x-2;
}

.file-icon {
  @apply w-4 h-4 text-green-400;
}

.file-name {
  @apply text-green-100 font-medium;
}

.file-size {
  @apply text-green-200;
}

.remove-file-btn {
  @apply p-1 rounded hover:bg-red-900/20 text-red-400 hover:text-red-300 transition-colors duration-200;
}

.remove-file-btn svg {
  @apply w-4 h-4;
}

.drop-overlay {
  @apply absolute inset-0 flex items-center justify-center;
  background: rgba(34, 197, 94, 0.1);
  backdrop-filter: blur(15px);
}

.drop-content {
  @apply text-center text-green-400;
}

.drop-icon {
  @apply w-12 h-12 mx-auto mb-3;
}

.drop-text {
  @apply text-lg font-medium;
}

/* Light mode support */
body.light-mode .unified-input {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(34, 197, 94, 0.2);
}

body.light-mode .main-textarea {
  background: rgba(255, 255, 255, 0.9) !important;
  color: #1e293b !important;
}

body.light-mode .main-textarea:focus {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #1e293b !important;
}

body.light-mode .main-textarea::placeholder {
  color: #6b7280 !important;
}

body.light-mode .upload-icon {
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(34, 197, 94, 0.3);
}

body.light-mode .icon-paperclip {
  color: #22c55e;
}

body.light-mode .file-chip {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
}

body.light-mode .file-name {
  color: #1e293b;
}

body.light-mode .file-size {
  color: #4b5563;
}
</style>