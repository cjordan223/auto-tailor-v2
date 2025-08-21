<template>
  <div class="card card-hover">
    <div class="text-center mb-4">
      <div class="text-4xl mb-2">{{ icon }}</div>
      <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
      <p class="text-sm text-gray-600">{{ description }}</p>
    </div>

    <!-- File Upload Zone -->
    <div
      ref="dropZone"
      class="upload-zone p-4 md:p-6 text-center cursor-pointer"
      :class="{
        'dragover': isDragOver,
        'error': uploadError
      }"
      @click="triggerFileInput"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <div v-if="!file && !uploadError">
        <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" stroke="currentColor" fill="none" viewBox="0 0 48 48">
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <p class="text-gray-600 mb-2">
          <span class="font-medium text-primary-600">Click to upload</span> or drag and drop
        </p>
        <p class="text-xs text-gray-500">{{ accept }}</p>
      </div>

      <div v-else-if="file && !uploadError" class="text-success-600">
        <svg class="mx-auto h-12 w-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <p class="font-medium">{{ file.name }}</p>
        <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
        <button
          @click.stop="removeFile"
          class="mt-2 text-xs text-error-600 hover:text-error-700"
        >
          Remove
        </button>
      </div>

      <div v-else-if="uploadError" class="text-error-600">
        <svg class="mx-auto h-12 w-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <p class="font-medium">Upload Error</p>
        <p class="text-xs">{{ uploadError }}</p>
        <button
          @click.stop="clearError"
          class="mt-2 text-xs text-primary-600 hover:text-primary-700"
        >
          Try Again
        </button>
      </div>
    </div>

    <!-- Text Input (for job descriptions) -->
    <div v-if="allowTextInput" class="mt-4">
      <div class="text-center text-gray-500 text-sm mb-3">
        <span class="bg-gray-50 px-2">OR</span>
      </div>
      <textarea
        v-model="textInput"
        placeholder="Paste job description here..."
        class="w-full h-24 md:h-32 p-3 border border-gray-300 rounded-lg focus-ring resize-none"
        @input="handleTextInput"
      ></textarea>
    </div>

    <!-- Hidden file input -->
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      class="hidden"
      @change="handleFileSelect"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  title: String,
  description: String,
  accept: String,
  icon: String,
  file: Object,
  allowTextInput: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['file-selected', 'text-input'])

// State
const dropZone = ref(null)
const fileInput = ref(null)
const isDragOver = ref(false)
const uploadError = ref(null)
const textInput = ref('')

// Watch for external file changes
watch(() => props.file, (newFile) => {
  if (!newFile) {
    textInput.value = ''
  }
})

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndEmitFile(file)
  }
}

const handleDragOver = (event) => {
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndEmitFile(file)
  }
}

const validateAndEmitFile = (file) => {
  uploadError.value = null
  
  // Check file type
  const acceptedTypes = props.accept.split(',').map(type => type.trim())
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
  
  if (!acceptedTypes.includes(fileExtension) && !acceptedTypes.includes(file.type)) {
    uploadError.value = `File type not supported. Please upload: ${props.accept}`
    return
  }
  
  // Check file size (10MB limit)
  if (file.size > 10 * 1024 * 1024) {
    uploadError.value = 'File size must be less than 10MB'
    return
  }
  
  emit('file-selected', file)
  textInput.value = '' // Clear text input when file is selected
}

const handleTextInput = () => {
  emit('text-input', textInput.value)
}

const removeFile = () => {
  emit('file-selected', null)
  fileInput.value.value = ''
}

const clearError = () => {
  uploadError.value = null
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>