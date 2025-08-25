<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ headerTitle }}</h1>
      <p class="text-gray-600">{{ headerSubtitle }}</p>
    </div>

    <!-- Loading/Processing State -->
    <div v-if="loading || isProcessing" class="py-6">
      <ProcessingStatus :status="isProcessing ? 'processing' : 'idle'" :progress="statusProgress" :error="null"
        :step="statusData?.step" :detail="statusData?.detail" :provider="statusData?.provider" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <div class="text-error-600 mb-4">
        <svg class="mx-auto w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <h2 class="text-xl font-semibold text-gray-900 mb-2">Error Loading Results</h2>
      <p class="text-gray-600 mb-4">{{ error }}</p>
      <button @click="loadResults" class="btn btn-primary">Try Again</button>
    </div>

    <!-- Results Content -->
    <div v-else-if="results && isCompleted" class="space-y-6">

      <!-- Document Previews and Downloads - MOVED TO TOP -->
      <div class="space-y-6">
        <!-- Resume Section -->
        <div class="card">
          <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <span class="text-2xl mr-3">📄</span>
            Resume
          </h3>

          <!-- Two-column layout for LaTeX and PDF -->
          <div class="grid lg:grid-cols-2 gap-6 mb-4">
            <!-- LaTeX Source Column -->
            <div class="space-y-4">

              <LaTeXEditor :job-id="jobId" file-type="resume" @content-changed="onResumeContentChanged"
                @save="onResumeSave" @revert="onResumeRevert" @reset="onResumeReset" />
            </div>

            <!-- PDF Preview Column -->
            <div class="space-y-4">

              <PDFViewer ref="resumePdfViewer" :key="resumePdfKey" :job-id="jobId" file-type="resume" />
            </div>
          </div>

          <button @click="downloadFile('resume')" :disabled="downloading.resume" class="btn btn-primary w-full">
            <span v-if="downloading.resume">Downloading...</span>
            <span v-else>Download Resume PDF</span>
          </button>
        </div>

        <!-- Cover Letter Section -->
        <div class="card">
          <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <span class="text-2xl mr-3">💌</span>
            Cover Letter
          </h3>

          <!-- Two-column layout for LaTeX and PDF -->
          <div class="grid lg:grid-cols-2 gap-6 mb-4">
            <!-- LaTeX Source Column -->
            <div class="space-y-4">

              <LaTeXEditor :job-id="jobId" file-type="cover-letter" @content-changed="onCoverLetterContentChanged"
                @save="onCoverLetterSave" @revert="onCoverLetterRevert" @reset="onCoverLetterReset" />
            </div>

            <!-- PDF Preview Column -->
            <div class="space-y-4">

              <PDFViewer ref="coverLetterPdfViewer" :key="coverLetterPdfKey" :job-id="jobId" file-type="cover-letter" />
            </div>
          </div>

          <button @click="downloadFile('cover-letter')" :disabled="downloading.coverLetter"
            class="btn btn-primary w-full">
            <span v-if="downloading.coverLetter">Downloading...</span>
            <span v-else>Download Cover Letter PDF</span>
          </button>
        </div>
      </div>

      <!-- Compact Information Grid -->
      <div class="grid lg:grid-cols-2 gap-6">
        <!-- Left Column -->
        <div class="space-y-6">
          <!-- Job Description Card (Collapsible) -->
          <div v-if="results.jobDescription" class="card">
            <div class="flex items-center justify-between cursor-pointer" @click="toggleJobDescription">
              <h2 class="text-lg font-semibold text-gray-900 flex items-center">
                <span class="text-xl mr-2">📋</span>
                This is what I applied for
              </h2>
              <svg 
                class="w-5 h-5 text-gray-500 transition-transform duration-200" 
                :class="{ 'rotate-180': showJobDescription }"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </div>
            
            <div v-if="showJobDescription" class="mt-4">
              <div class="bg-gradient-to-r from-purple-50 to-indigo-50 p-4 rounded-lg border border-purple-200">
                <h3 class="text-md font-semibold text-purple-900 mb-2 flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z">
                    </path>
                  </svg>
                  Job Description Summary
                </h3>
                <div class="text-purple-800 leading-relaxed whitespace-pre-wrap text-sm max-h-48 overflow-y-auto">{{ cleanJobDescription(results.jobDescription) }}</div>
              </div>
            </div>
          </div>

          <!-- Skills Changes Card -->
          <div class="card">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span class="text-xl mr-2">🛠️</span>
              Skills Changes
            </h3>
            <div class="max-h-64 overflow-y-auto mb-4">
              <div v-if="results.skillsChanges && Object.keys(results.skillsChanges).length > 0" class="space-y-3">
                <div v-for="(changes, category) in results.skillsChanges" :key="category"
                  class="border border-gray-200 rounded-lg p-3">
                  <h4 class="text-sm font-medium text-gray-900 mb-2">{{ category }}</h4>

                  <!-- Skills Added -->
                  <div v-if="changes.added.length > 0" class="mb-2">
                    <h5 class="text-xs font-medium text-green-700 mb-1 flex items-center">
                      <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                      </svg>
                      Added ({{ changes.added.length }})
                    </h5>
                    <div class="flex flex-wrap gap-1">
                      <span v-for="skill in changes.added" :key="skill"
                        class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                        {{ skill }}
                      </span>
                    </div>
                  </div>

                  <!-- Skills Removed -->
                  <div v-if="changes.removed.length > 0">
                    <h5 class="text-xs font-medium text-red-700 mb-1 flex items-center">
                      <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                      </svg>
                      Removed ({{ changes.removed.length }})
                    </h5>
                    <div class="flex flex-wrap gap-1">
                      <span v-for="skill in changes.removed" :key="skill"
                        class="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full font-medium line-through">
                        {{ skill }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-6 text-gray-500">
                <svg class="w-8 h-8 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z">
                  </path>
                </svg>
                <p class="text-sm">No skills changes were made</p>
              </div>
            </div>
            <button @click="downloadFile('edits')" :disabled="downloading.edits" class="btn btn-secondary w-full">
              <span v-if="downloading.edits">Downloading...</span>
              <span v-else>Download Edit Details</span>
            </button>
          </div>

          <!-- Skills Validation Status -->
          <div v-if="results.validationStatus" class="card">
            <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span class="text-xl mr-2">🔍</span>
              Skills Validation Status
            </h2>
            <div class="space-y-3">
              <!-- Validation Summary -->
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="font-medium text-gray-900 text-sm">Validation Summary</h3>
                  <span :class="{
                    'px-2 py-1 text-xs rounded-full font-medium': true,
                    'bg-green-100 text-green-800': results.validationStatus.confidence === 'high',
                    'bg-yellow-100 text-yellow-800': results.validationStatus.confidence === 'medium',
                    'bg-red-100 text-red-800': results.validationStatus.confidence === 'low'
                  }">
                    {{ results.validationStatus.confidence.toUpperCase() }} Confidence
                  </span>
                </div>
                <p class="text-xs text-gray-600">
                  {{ results.validationStatus.flaggedCount }} skills were flagged for validation and moved to suggested
                  additions.
                </p>
              </div>

              <!-- Flagged Skills -->
              <div v-if="results.validationStatus.flaggedSkills?.length" class="space-y-2">
                <h3 class="font-medium text-gray-900 text-sm">Flagged Skills (Moved to Suggestions)</h3>
                <div class="space-y-2 max-h-32 overflow-y-auto">
                  <div v-for="(skill, index) in results.validationStatus.flaggedSkills" :key="index"
                    class="flex items-start space-x-2 p-2 bg-yellow-50 rounded-lg border border-yellow-200">
                    <div
                      class="flex-shrink-0 w-4 h-4 bg-yellow-500 text-white rounded-full flex items-center justify-center text-xs font-medium">
                      ⚠️
                    </div>
                    <div class="flex-1">
                      <h4 class="font-medium text-gray-900 text-sm">{{ skill.skill }}</h4>
                      <p class="text-xs text-gray-600">{{ skill.reason }}</p>
                      <p class="text-xs text-yellow-700 mt-1">Confidence: {{ skill.confidence }}</p>
                    </div>
                    <div class="flex-shrink-0 flex space-x-1">
                      <button
                        @click="handleAddSkill(skill.skill, 'conversational_skills')"
                        :disabled="addingSkills.has(skill.skill)"
                        class="px-3 py-1 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white text-xs rounded-md transition-colors duration-200 flex items-center space-x-1"
                        title="Add this skill to your baseline skills inventory. It will no longer be flagged in future validations."
                      >
                        <span v-if="addingSkills.has(skill.skill)" class="flex items-center">
                          <svg class="animate-spin -ml-1 mr-1 h-3 w-3 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Adding...
                        </span>
                        <span v-else class="flex items-center">
                          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                          </svg>
                          Add to Skills
                        </span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="space-y-6">
          <!-- Review Overview (Collapsible) -->
          <div v-if="results.reviewData?.overview" class="card">
            <div class="flex items-center justify-between cursor-pointer" @click="toggleAnalysisOverview">
              <h2 class="text-lg font-semibold text-gray-900">AI Analysis Overview</h2>
              <svg 
                class="w-5 h-5 text-gray-500 transition-transform duration-200" 
                :class="{ 'rotate-180': showAnalysisOverview }"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </div>
            
            <div v-if="showAnalysisOverview" class="mt-4 space-y-4">
              <!-- Job Description Section -->
              <div v-if="getJobSection(results.reviewData.overview)"
                class="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-200">
                <h3 class="text-md font-semibold text-blue-900 mb-2 flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6">
                    </path>
                  </svg>
                  What This Job Is About
                </h3>
                <p class="text-blue-800 leading-relaxed text-sm">{{ getJobSection(results.reviewData.overview) }}</p>
              </div>

              <!-- Customization Strategy Section -->
              <div v-if="getCustomizationSection(results.reviewData.overview)"
                class="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg border border-green-200">
                <h3 class="text-md font-semibold text-green-900 mb-2 flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  How We Customized Your Resume
                </h3>
                <p class="text-green-800 leading-relaxed text-sm">{{ getCustomizationSection(results.reviewData.overview) }}</p>
              </div>

              <!-- Statistics -->
              <div v-if="results.reviewData.statistics" class="grid grid-cols-2 gap-3">
                <div class="text-center p-3 bg-white border border-gray-200 rounded-lg">
                  <div class="text-lg font-bold text-primary-600">{{ results.reviewData.statistics.total_chunks_modified }}
                  </div>
                  <div class="text-xs text-gray-600">Chunks Modified</div>
                </div>
                <div class="text-center p-3 bg-white border border-gray-200 rounded-lg">
                  <div class="text-lg font-bold text-primary-600">{{ results.reviewData.statistics.skills_sections_updated }}
                  </div>
                  <div class="text-xs text-gray-600">Skills Updated</div>
                </div>
                <div class="text-center p-3 bg-white border border-gray-200 rounded-lg">
                  <div class="text-lg font-bold text-primary-600">{{ results.reviewData.statistics.cover_letter_paragraphs }}
                  </div>
                  <div class="text-xs text-gray-600">Cover Letter Changes</div>
                </div>
                <div class="text-center p-3 bg-white border border-gray-200 rounded-lg">
                  <div class="text-lg font-bold text-primary-600">{{ results.reviewData.statistics.suggested_additions }}
                  </div>
                  <div class="text-xs text-gray-600">Suggested Additions</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Suggested Additions -->
          <div v-if="results.suggestedAdditions?.length" class="card">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Suggested Additions</h2>
            <p class="text-gray-600 mb-3 text-sm">
              These skills or keywords from the job description weren't found in your resume. Consider adding them if
              relevant:
            </p>
            <div class="space-y-2 max-h-64 overflow-y-auto">
              <div v-for="(suggestion, index) in results.suggestedAdditions" :key="index"
                class="flex items-start space-x-2 p-3 bg-blue-50 rounded-lg">
                <div
                  class="flex-shrink-0 w-5 h-5 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-medium">
                  {{ index + 1 }}
                </div>
                <div>
                  <h4 class="font-medium text-gray-900 text-sm">{{ suggestion.term }}</h4>
                  <p class="text-xs text-gray-600">{{ suggestion.why }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Job Details -->
          <div class="card">
            <h2 class="text-lg font-semibold text-gray-900 mb-3">Generation Details</h2>
            <div class="grid grid-cols-1 gap-3">
              <div>
                <h3 class="font-medium text-gray-900 mb-1 text-sm">Job ID</h3>
                <p class="text-xs text-gray-600 font-mono">{{ results.jobId }}</p>
              </div>
              <div>
                <h3 class="font-medium text-gray-900 mb-1 text-sm">Generated</h3>
                <p class="text-xs text-gray-600">{{ formatDate(results.createdAt) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-center space-x-4">
      <router-link to="/" class="btn btn-secondary">
        Generate Another Resume
      </router-link>
      <button v-if="results" @click="downloadAll" :disabled="isDownloadingAll" class="btn btn-primary">
        <span v-if="isDownloadingAll">Downloading ZIP...</span>
        <span v-else>Download All Files (ZIP)</span>
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
import LaTeXEditor from '../components/LaTeXEditor.vue'

const route = useRoute()
const { getResults, downloadFile: apiDownloadFile, downloadAllAsZip, addSkillToBaseline, checkStatus } = useAPI()

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
const downloadingZip = ref(false)
const addingSkills = ref(new Set()) // Track which skills are being added

// Collapsible state
const showJobDescription = ref(false)
const showAnalysisOverview = ref(true) // Start expanded by default

// Real-time editing state
const resumeContent = ref('')
const coverLetterContent = ref('')
const resumePdfKey = ref(0)
const coverLetterPdfKey = ref(0)
const recompiling = ref({
  resume: false,
  coverLetter: false
})

// PDF viewer refs
const resumePdfViewer = ref(null)
const coverLetterPdfViewer = ref(null)

let pollTimer = null

// Computed
const jobId = computed(() => props.jobId || route.params.jobId)
const isDownloadingAll = computed(() =>
  Object.values(downloading.value).some(d => d) || downloadingZip.value
)
const isProcessing = computed(() => statusData.value?.status === 'processing')
const isCompleted = computed(() => {
  const completed = statusData.value?.status === 'completed'
  console.log('isCompleted computed:', completed, 'statusData:', statusData.value)
  return completed
})
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

    console.log('Loading results for jobId:', jobId.value)
    const data = await getResults(jobId.value)
    console.log('Results loaded:', data)
    results.value = data
  } catch (err) {
    console.error('Error loading results:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const pollStatus = async () => {
  try {
    console.log('Polling status for jobId:', jobId.value)
    const data = await checkStatus(jobId.value)
    console.log('Status data received:', data)
    statusData.value = data
    if (data.status === 'completed') {
      console.log('Job completed, stopping polling and loading results')
      clearInterval(pollTimer)
      pollTimer = null
      await loadResults()
    } else if (data.status === 'error') {
      console.log('Job error, stopping polling')
      clearInterval(pollTimer)
      pollTimer = null
      error.value = data.error || 'Processing failed'
    }
  } catch (err) {
    console.log('Polling error (expected for 404s):', err.message)
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
  try {
    downloadingZip.value = true
    await downloadAllAsZip(jobId.value)
  } catch (err) {
    alert(`Failed to download zip file: ${err.message}`)
  } finally {
    downloadingZip.value = false
  }
}

const handleAddSkill = async (skill, category = 'conversational_skills') => {
  try {
    addingSkills.value.add(skill)
    await addSkillToBaseline(jobId.value, skill, category)
    
    // Show success message with better UX
    const categoryDisplay = category === 'confirmed_skills' ? 'confirmed skill' : 'conversational skill'
    const message = `✅ "${skill}" has been added to your skills inventory as a ${categoryDisplay}. This skill will no longer be flagged in future validations.`
    
    // Use a more user-friendly notification (could be replaced with a proper toast library)
    if (confirm(message + '\n\nWould you like to refresh the page to see updated validation status?')) {
      await loadResults()
    }
    
  } catch (err) {
    alert(`Failed to add skill: ${err.message}`)
  } finally {
    addingSkills.value.delete(skill)
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

const getJobSection = (overview) => {
  if (!overview) return ''

  // First, try to parse as JSON (fallback for when AI returns JSON)
  try {
    const jsonData = JSON.parse(overview)
    if (jsonData.what_this_job_is_about) {
      return jsonData.what_this_job_is_about
    }
  } catch (e) {
    // Not JSON, continue with text parsing
  }

  // Look for the job section in plain text
  const jobMatch = overview.match(/WHAT THIS JOB IS ABOUT:?\s*(.*?)(?=HOW WE CUSTOMIZED|$)/s)
  if (jobMatch) {
    return jobMatch[1].trim()
  }

  // Fallback: try to find the first paragraph if no clear section headers
  const paragraphs = overview.split('\n\n').filter(p => p.trim())
  return paragraphs[0] || overview
}

const getCustomizationSection = (overview) => {
  if (!overview) return ''

  // First, try to parse as JSON (fallback for when AI returns JSON)
  try {
    const jsonData = JSON.parse(overview)
    if (jsonData.how_we_customized_your_resume) {
      return jsonData.how_we_customized_your_resume
    }
  } catch (e) {
    // Not JSON, continue with text parsing
  }

  // Look for the customization section in plain text
  const customMatch = overview.match(/HOW WE CUSTOMIZED YOUR RESUME:?\s*(.*?)$/s)
  if (customMatch) {
    return customMatch[1].trim()
  }

  // Fallback: try to find the second paragraph if no clear section headers
  const paragraphs = overview.split('\n\n').filter(p => p.trim())
  return paragraphs.length > 1 ? paragraphs.slice(1).join('\n\n') : ''
}

// Toggle functions for collapsible sections
const toggleJobDescription = () => {
  showJobDescription.value = !showJobDescription.value
}

const toggleAnalysisOverview = () => {
  showAnalysisOverview.value = !showAnalysisOverview.value
}

// Clean job description for display
const cleanJobDescription = (jobDescription) => {
  if (!jobDescription) return ''
  
  // Remove excessive whitespace and normalize line breaks
  let cleaned = jobDescription
    .replace(/\r\n/g, '\n') // Normalize line endings
    .replace(/\n{3,}/g, '\n\n') // Remove excessive blank lines
    .replace(/[ \t]+/g, ' ') // Normalize spaces
    .trim()
  
  // Fix common formatting issues
  cleaned = cleaned
    .replace(/([.!?])\s*([A-Z])/g, '$1\n\n$2') // Add line breaks after sentences
    .replace(/([.!?])\s*([•\-\*])/g, '$1\n$2') // Fix bullet points
    .replace(/([•\-\*])\s*/g, '  $1 ') // Indent bullet points
  
  // Clean up any remaining formatting artifacts
  cleaned = cleaned
    .replace(/\n{3,}/g, '\n\n') // Remove excessive blank lines again
    .replace(/^\s+|\s+$/gm, '') // Trim whitespace from each line
  
  return cleaned
}

// Real-time editing event handlers
const onResumeContentChanged = (content) => {
  console.log('Resume content changed, length:', content.length)
  resumeContent.value = content
  // Trigger recompilation after a delay to avoid too many requests
  debouncedRecompileResume()
}

const onCoverLetterContentChanged = (content) => {
  coverLetterContent.value = content
  // Trigger recompilation after a delay to avoid too many requests
  debouncedRecompileCoverLetter()
}

const onResumeSave = async (content) => {
  try {
    await recompileLatex('resume', content)
    console.log('Resume saved and recompiled')
  } catch (err) {
    console.error('Failed to save resume:', err)
  }
}

const onCoverLetterSave = async (content) => {
  try {
    await recompileLatex('cover-letter', content)
    console.log('Cover letter saved and recompiled')
  } catch (err) {
    console.error('Failed to save cover letter:', err)
  }
}

const onResumeRevert = (content) => {
  resumeContent.value = content
  console.log('Resume changes reverted')
}

const onCoverLetterRevert = (content) => {
  coverLetterContent.value = content
  console.log('Cover letter changes reverted')
}

const onResumeReset = async (content) => {
  try {
    resumeContent.value = content
    await recompileLatex('resume', content)
    console.log('Resume reset to original and recompiled')
  } catch (err) {
    console.error('Failed to reset resume:', err)
  }
}

const onCoverLetterReset = async (content) => {
  try {
    coverLetterContent.value = content
    await recompileLatex('cover-letter', content)
    console.log('Cover letter reset to original and recompiled')
  } catch (err) {
    console.error('Failed to reset cover letter:', err)
  }
}

// Debounced recompilation functions
let resumeRecompileTimeout = null
let coverLetterRecompileTimeout = null

const debouncedRecompileResume = () => {
  if (resumeRecompileTimeout) {
    clearTimeout(resumeRecompileTimeout)
  }
  resumeRecompileTimeout = setTimeout(() => {
    if (resumeContent.value) {
      console.log('Debounced recompile triggered for resume')
      recompileLatex('resume', resumeContent.value)
    }
  }, 2000) // 2 second delay
}

const debouncedRecompileCoverLetter = () => {
  if (coverLetterRecompileTimeout) {
    clearTimeout(coverLetterRecompileTimeout)
  }
  coverLetterRecompileTimeout = setTimeout(() => {
    if (coverLetterContent.value) {
      recompileLatex('cover-letter', coverLetterContent.value)
    }
  }, 2000) // 2 second delay
}

// Recompile LaTeX content
const recompileLatex = async (fileType, content) => {
  if (recompiling.value[fileType]) {
    return // Already recompiling
  }

  try {
    recompiling.value[fileType] = true

    const response = await fetch(`/api/recompile/${jobId.value}/${fileType}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content })
    })

    if (!response.ok) {
      throw new Error(`Recompilation failed: ${response.statusText}`)
    }

    const result = await response.json()

    if (result.success) {
      console.log(`${fileType} recompiled successfully`)

      // Wait for backend to confirm file is ready, then force refresh once
      setTimeout(() => {
        if (fileType === 'resume') {
          resumePdfKey.value++ // Single key update
          if (resumePdfViewer.value) {
            resumePdfViewer.value.forceRefresh()
          }
        } else {
          coverLetterPdfKey.value++ // Single key update
          if (coverLetterPdfViewer.value) {
            coverLetterPdfViewer.value.forceRefresh()
          }
        }
      }, 2000) // Increased to 2 seconds for file system consistency
    } else {
      throw new Error(result.error || 'Recompilation failed')
    }
  } catch (err) {
    console.error(`Failed to recompile ${fileType}:`, err)
    // You might want to show an error notification to the user here
  } finally {
    recompiling.value[fileType] = false
  }
}

// Lifecycle
onMounted(async () => {
  if (!jobId.value) {
    error.value = 'No job ID provided'
    loading.value = false
    return
  }

  console.log('Component mounted, checking initial status...')

  // Check initial status first
  try {
    const initialStatus = await checkStatus(jobId.value)
    console.log('Initial status:', initialStatus)
    statusData.value = initialStatus

    if (initialStatus.status === 'completed') {
      console.log('Job already completed, loading results directly')
      await loadResults()
      // Don't start polling since it's already done
    } else {
      console.log('Job not completed, starting polling')
      // Start polling status every 2s
      pollTimer = setInterval(pollStatus, 2000)
    }
  } catch (err) {
    console.log('Initial status check failed, starting polling anyway:', err.message)
    // Start polling status every 2s
    pollTimer = setInterval(pollStatus, 2000)
  }
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (resumeRecompileTimeout) clearTimeout(resumeRecompileTimeout)
  if (coverLetterRecompileTimeout) clearTimeout(coverLetterRecompileTimeout)
})
</script>