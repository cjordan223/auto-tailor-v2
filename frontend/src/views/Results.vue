<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ headerTitle }}</h1>
      <p class="text-gray-600">{{ headerSubtitle }}</p>
    </div>

    <!-- Loading/Processing State -->
    <div v-if="loading || isProcessing" class="py-6">
      <ProcessingStatus
        :status="isProcessing ? 'processing' : 'idle'"
        :progress="statusProgress"
        :error="null"
        :step="statusData?.step"
        :detail="statusData?.detail"
        :provider="statusData?.provider"
      />
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
    <div v-else-if="results && isCompleted" class="space-y-8">

      <!-- Document Previews and Downloads -->
      <div class="space-y-8">
        <!-- Resume Section -->
        <div class="card">
          <h3 class="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <span class="text-2xl mr-3">📄</span>
            Resume
          </h3>
          
          <!-- Two-column layout for LaTeX and PDF -->
          <div class="grid lg:grid-cols-2 gap-6 mb-6">
            <!-- LaTeX Source Column -->
            <div class="space-y-4">
              <h4 class="text-md font-medium text-gray-800 flex items-center">
                <span class="text-lg mr-2">📝</span>
                LaTeX Source
              </h4>
              <LaTeXViewer :job-id="jobId" file-type="resume" />
            </div>
            
            <!-- PDF Preview Column -->
            <div class="space-y-4">
              <h4 class="text-md font-medium text-gray-800 flex items-center">
                <span class="text-lg mr-2">📋</span>
                PDF Preview
              </h4>
              <PDFViewer :job-id="jobId" file-type="resume" />
            </div>
          </div>
          
          <button
            @click="downloadFile('resume')"
            :disabled="downloading.resume"
            class="btn btn-primary w-full"
          >
            <span v-if="downloading.resume">Downloading...</span>
            <span v-else>Download Resume PDF</span>
          </button>
        </div>

        <!-- Cover Letter Section -->
        <div class="card">
          <h3 class="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <span class="text-2xl mr-3">💌</span>
            Cover Letter
          </h3>
          
          <!-- Two-column layout for LaTeX and PDF -->
          <div class="grid lg:grid-cols-2 gap-6 mb-6">
            <!-- LaTeX Source Column -->
            <div class="space-y-4">
              <h4 class="text-md font-medium text-gray-800 flex items-center">
                <span class="text-lg mr-2">📝</span>
                LaTeX Source
              </h4>
              <LaTeXViewer :job-id="jobId" file-type="cover-letter" />
            </div>
            
            <!-- PDF Preview Column -->
            <div class="space-y-4">
              <h4 class="text-md font-medium text-gray-800 flex items-center">
                <span class="text-lg mr-2">📋</span>
                PDF Preview
              </h4>
              <PDFViewer :job-id="jobId" file-type="cover-letter" />
            </div>
          </div>
          
          <button
            @click="downloadFile('cover-letter')"
            :disabled="downloading.coverLetter"
            class="btn btn-primary w-full"
          >
            <span v-if="downloading.coverLetter">Downloading...</span>
            <span v-else>Download Cover Letter PDF</span>
          </button>
        </div>

        <!-- Skills Changes Card -->
        <div class="card">
          <h3 class="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <span class="text-2xl mr-3">🛠️</span>
            Skills Changes
          </h3>
          <div class="h-96 overflow-y-auto mb-4">
            <div v-if="results.skillsChanges && Object.keys(results.skillsChanges).length > 0" class="space-y-4">
              <div
                v-for="(changes, category) in results.skillsChanges"
                :key="category"
                class="border border-gray-200 rounded-lg p-4"
              >
                <h4 class="text-sm font-medium text-gray-900 mb-3">{{ category }}</h4>
                
                <!-- Skills Added -->
                <div v-if="changes.added.length > 0" class="mb-3">
                  <h5 class="text-xs font-medium text-green-700 mb-2 flex items-center">
                      <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                      </svg>
                      Added ({{ changes.added.length }})
                    </h5>
                    <div class="flex flex-wrap gap-1">
                      <span
                        v-for="skill in changes.added"
                        :key="skill"
                        class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium"
                      >
                        {{ skill }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- Skills Removed -->
                  <div v-if="changes.removed.length > 0">
                    <h5 class="text-xs font-medium text-red-700 mb-2 flex items-center">
                      <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                      </svg>
                      Removed ({{ changes.removed.length }})
                    </h5>
                    <div class="flex flex-wrap gap-1">
                      <span
                        v-for="skill in changes.removed"
                        :key="skill"
                        class="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full font-medium line-through"
                      >
                        {{ skill }}
                      </span>
                    </div>
                  </div>
                </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <svg class="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <p class="text-sm">No skills changes were made</p>
            </div>
          </div>
          <button
            @click="downloadFile('edits')"
            :disabled="downloading.edits"
            class="btn btn-secondary w-full"
          >
            <span v-if="downloading.edits">Downloading...</span>
            <span v-else>Download Edit Details</span>
          </button>
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


      <!-- Review Overview -->
      <div v-if="results.reviewData?.overview" class="card">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">AI Analysis Overview</h2>
        <div class="bg-gray-50 p-4 rounded-lg mb-6">
          <p class="text-gray-700 leading-relaxed">{{ formatOverview(results.reviewData.overview) }}</p>
        </div>
        
        <!-- Statistics -->
        <div v-if="results.reviewData.statistics" class="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="text-center p-4 bg-white border border-gray-200 rounded-lg">
            <div class="text-2xl font-bold text-primary-600">{{ results.reviewData.statistics.total_chunks_modified }}</div>
            <div class="text-sm text-gray-600">Chunks Modified</div>
          </div>
          <div class="text-center p-4 bg-white border border-gray-200 rounded-lg">
            <div class="text-2xl font-bold text-primary-600">{{ results.reviewData.statistics.skills_sections_updated }}</div>
            <div class="text-sm text-gray-600">Skills Updated</div>
          </div>
          <div class="text-center p-4 bg-white border border-gray-200 rounded-lg">
            <div class="text-2xl font-bold text-primary-600">{{ results.reviewData.statistics.cover_letter_paragraphs }}</div>
            <div class="text-sm text-gray-600">Cover Letter Changes</div>
          </div>
          <div class="text-center p-4 bg-white border border-gray-200 rounded-lg">
            <div class="text-2xl font-bold text-primary-600">{{ results.reviewData.statistics.suggested_additions }}</div>
            <div class="text-sm text-gray-600">Suggested Additions</div>
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
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAPI } from '../composables/useAPI.js'
import ProcessingStatus from '../components/ProcessingStatus.vue'
import PDFViewer from '../components/PDFViewer.vue'
import LaTeXViewer from '../components/LaTeXViewer.vue'

const route = useRoute()
const { getResults, downloadFile: apiDownloadFile, checkStatus } = useAPI()

// Props
const props = defineProps({
  jobId: String
})

// State
const loading = ref(true)
const error = ref(null)
const results = ref(null)
const statusData = ref({ status: 'processing', progress: 0, step: 'Initializing...' })
const downloading = ref({
  resume: false,
  coverLetter: false,
  edits: false
})
let pollTimer = null

// Computed
const jobId = computed(() => props.jobId || route.params.jobId)
const isDownloadingAll = computed(() => 
  Object.values(downloading.value).some(d => d)
)
const isProcessing = computed(() => statusData.value?.status === 'processing')
const isCompleted = computed(() => statusData.value?.status === 'completed')
const statusProgress = computed(() => Number(statusData.value?.progress || 0))
const headerTitle = computed(() => {
  if (isProcessing.value) return 'Generating Your Resume...'
  if (isCompleted.value) return 'Resume Generated Successfully!'
  if (error.value) return 'Error Loading Results'
  return 'Preparing Results...'
})
const headerSubtitle = computed(() => {
  if (isProcessing.value) return 'AI is analyzing your job description and customizing your resume. This may take longer on local models.'
  if (isCompleted.value) return 'Your customized resume and cover letter are ready for download.'
  if (error.value) return error.value
  return 'Loading results...'
})

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

const pollStatus = async () => {
  try {
    const data = await checkStatus(jobId.value)
    statusData.value = data
    if (data.status === 'completed') {
      clearInterval(pollTimer)
      pollTimer = null
      await loadResults()
    } else if (data.status === 'error') {
      clearInterval(pollTimer)
      pollTimer = null
      error.value = data.error || 'Processing failed'
    }
  } catch (err) {
    // Keep polling; transient 404 while job initializes is expected
  }
}

const downloadFile = async (fileType) => {
  try {
    if (!isCompleted.value) return
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

const formatOverview = (overview) => {
  if (!overview) return ''
  
  // The backend now returns properly formatted text, so just return as-is
  return overview
}

// Lifecycle
onMounted(() => {
  if (!jobId.value) {
    error.value = 'No job ID provided'
    loading.value = false
    return
  }
  // Start polling status immediately and every 2s
  pollStatus()
  pollTimer = setInterval(pollStatus, 2000)
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>