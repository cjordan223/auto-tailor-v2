<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Resume Generated Successfully!</h1>
      <p class="text-gray-600">Your customized resume and cover letter are ready for download.</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin mx-auto w-8 h-8 text-primary-600">
        <svg class="w-full h-full" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      <p class="text-gray-600 mt-4">Loading results...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <div class="text-error-600 mb-4">
        <svg class="mx-auto w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <h2 class="text-xl font-semibold text-gray-900 mb-2">Error Loading Results</h2>
      <p class="text-gray-600 mb-4">{{ error }}</p>
      <button @click="loadResults" class="btn btn-primary">Try Again</button>
    </div>

    <!-- Results Content -->
    <div v-else-if="results" class="space-y-8">
      <!-- Download Section -->
      <div class="card">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Download Files</h2>
        <div class="grid md:grid-cols-3 gap-4">
          <!-- Resume PDF -->
          <div class="text-center p-6 border border-gray-200 rounded-lg hover:shadow-md transition-all">
            <div class="text-4xl mb-3">📄</div>
            <h3 class="font-medium text-gray-900 mb-2">Resume PDF</h3>
            <p class="text-sm text-gray-600 mb-4">Your customized resume</p>
            <button
              @click="downloadFile('resume')"
              :disabled="downloading.resume"
              class="btn btn-primary w-full"
            >
              <span v-if="downloading.resume">Downloading...</span>
              <span v-else>Download Resume</span>
            </button>
          </div>

          <!-- Cover Letter PDF -->
          <div class="text-center p-6 border border-gray-200 rounded-lg hover:shadow-md transition-all">
            <div class="text-4xl mb-3">💌</div>
            <h3 class="font-medium text-gray-900 mb-2">Cover Letter PDF</h3>
            <p class="text-sm text-gray-600 mb-4">Your customized cover letter</p>
            <button
              @click="downloadFile('cover-letter')"
              :disabled="downloading.coverLetter"
              class="btn btn-primary w-full"
            >
              <span v-if="downloading.coverLetter">Downloading...</span>
              <span v-else>Download Cover Letter</span>
            </button>
          </div>

          <!-- Edits JSON -->
          <div class="text-center p-6 border border-gray-200 rounded-lg hover:shadow-md transition-all">
            <div class="text-4xl mb-3">📋</div>
            <h3 class="font-medium text-gray-900 mb-2">Edit Details</h3>
            <p class="text-sm text-gray-600 mb-4">JSON file with all changes</p>
            <button
              @click="downloadFile('edits')"
              :disabled="downloading.edits"
              class="btn btn-secondary w-full"
            >
              <span v-if="downloading.edits">Downloading...</span>
              <span v-else>Download Edits</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Suggested Additions -->
      <div v-if="results.suggestedAdditions?.length" class="card">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Suggested Additions</h2>
        <p class="text-gray-600 mb-4">
          These skills or keywords from the job description weren't found in your resume. Consider adding them if relevant:
        </p>
        <div class="space-y-3">
          <div
            v-for="(suggestion, index) in results.suggestedAdditions"
            :key="index"
            class="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg"
          >
            <div class="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
              {{ index + 1 }}
            </div>
            <div>
              <h4 class="font-medium text-gray-900">{{ suggestion.term }}</h4>
              <p class="text-sm text-gray-600">{{ suggestion.why }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Job Details -->
      <div class="card">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Generation Details</h2>
        <div class="grid md:grid-cols-2 gap-6">
          <div>
            <h3 class="font-medium text-gray-900 mb-2">Job ID</h3>
            <p class="text-sm text-gray-600 font-mono">{{ results.jobId }}</p>
          </div>
          <div>
            <h3 class="font-medium text-gray-900 mb-2">Generated</h3>
            <p class="text-sm text-gray-600">{{ formatDate(results.createdAt) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-center space-x-4">
      <router-link to="/" class="btn btn-secondary">
        Generate Another Resume
      </router-link>
      <button
        v-if="results"
        @click="downloadAll"
        :disabled="isDownloadingAll"
        class="btn btn-primary"
      >
        <span v-if="isDownloadingAll">Downloading All...</span>
        <span v-else>Download All Files</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAPI } from '../composables/useAPI.js'

const route = useRoute()
const { getResults, downloadFile: apiDownloadFile } = useAPI()

// Props
const props = defineProps({
  jobId: String
})

// State
const loading = ref(true)
const error = ref(null)
const results = ref(null)
const downloading = ref({
  resume: false,
  coverLetter: false,
  edits: false
})

// Computed
const jobId = computed(() => props.jobId || route.params.jobId)
const isDownloadingAll = computed(() => 
  Object.values(downloading.value).some(d => d)
)

// Methods
const loadResults = async () => {
  try {
    loading.value = true
    error.value = null
    
    const data = await getResults(jobId.value)
    results.value = data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const downloadFile = async (fileType) => {
  try {
    const downloadKey = fileType === 'cover-letter' ? 'coverLetter' : fileType
    downloading.value[downloadKey] = true
    
    await apiDownloadFile(jobId.value, fileType)
  } catch (err) {
    alert(`Failed to download file: ${err.message}`)
  } finally {
    const downloadKey = fileType === 'cover-letter' ? 'coverLetter' : fileType
    downloading.value[downloadKey] = false
  }
}

const downloadAll = async () => {
  const files = ['resume', 'cover-letter', 'edits']
  
  for (const fileType of files) {
    try {
      await downloadFile(fileType)
      // Small delay between downloads
      await new Promise(resolve => setTimeout(resolve, 500))
    } catch (err) {
      console.error(`Failed to download ${fileType}:`, err)
    }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  
  try {
    return new Date(dateString).toLocaleString()
  } catch (err) {
    return 'Unknown'
  }
}

// Lifecycle
onMounted(() => {
  if (jobId.value) {
    loadResults()
  } else {
    error.value = 'No job ID provided'
    loading.value = false
  }
})
</script>