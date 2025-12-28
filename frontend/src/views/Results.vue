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
        :step="statusData?.step" :detail="statusData?.detail" :provider="statusData?.provider" 
        @cancel="handleProcessingCancel" />
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

          <div class="flex gap-2">
            <button @click="downloadFile('cover-letter')" :disabled="downloading.coverLetter"
              class="btn btn-primary flex-1">
              <span v-if="downloading.coverLetter">Downloading...</span>
              <span v-else>Download Cover Letter PDF</span>
            </button>
            <button @click="showRegenerateModal = true" :disabled="regenerating.coverLetter" 
              class="btn btn-secondary">
              <span v-if="regenerating.coverLetter">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Regenerating...
              </span>
              <span v-else>
                🔄 Regenerate
              </span>
            </button>
          </div>
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
                    <div class="flex-shrink-0">
                      <div class="relative skill-dropdown" ref="skillDropdown">
                        <button
                          @click="toggleSkillMenu(skill.skill)"
                          :disabled="addingSkills.has(skill.skill)"
                          class="px-3 py-1 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white text-xs rounded-md transition-colors duration-200 flex items-center space-x-1"
                          title="Add this skill to your baseline skills inventory with confidence level"
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
                            Add Skill
                            <svg class="w-2 h-2 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                            </svg>
                          </span>
                        </button>
                        
                        <!-- Skill Addition Dropdown -->
                        <div 
                          v-if="openSkillMenus.has(skill.skill)"
                          class="absolute right-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10"
                        >
                          <div class="px-3 py-2 text-xs font-medium text-gray-500 border-b border-gray-100">
                            Add as:
                          </div>
                          
                          <!-- Expert Level -->
                          <button
                            @click="handleAddSkill(skill.skill, 'confirmed_skills', 'expert')"
                            class="w-full text-left px-3 py-2 text-xs hover:bg-gray-50 flex items-center"
                          >
                            <span class="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                            <div>
                              <div class="font-medium text-gray-900">Expert</div>
                              <div class="text-gray-500">High proficiency</div>
                            </div>
                          </button>
                          
                          <!-- Proficient Level -->
                          <button
                            @click="handleAddSkill(skill.skill, 'confirmed_skills', 'proficient')"
                            class="w-full text-left px-3 py-2 text-xs hover:bg-gray-50 flex items-center"
                          >
                            <span class="w-2 h-2 bg-orange-500 rounded-full mr-2"></span>
                            <div>
                              <div class="font-medium text-gray-900">Proficient</div>
                              <div class="text-gray-500">Good working knowledge</div>
                            </div>
                          </button>
                          
                          <!-- Familiar Level -->
                          <button
                            @click="handleAddSkill(skill.skill, 'conversational_skills', 'familiar')"
                            class="w-full text-left px-3 py-2 text-xs hover:bg-gray-50 flex items-center"
                          >
                            <span class="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
                            <div>
                              <div class="font-medium text-gray-900">Familiar</div>
                              <div class="text-gray-500">Basic understanding</div>
                            </div>
                          </button>
                          
                          <!-- Learning Level -->
                          <button
                            @click="handleAddSkill(skill.skill, 'conversational_skills', 'learning')"
                            class="w-full text-left px-3 py-2 text-xs hover:bg-gray-50 flex items-center"
                          >
                            <span class="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                            <div>
                              <div class="font-medium text-gray-900">Learning</div>
                              <div class="text-gray-500">Currently learning</div>
                            </div>
                          </button>
                        </div>
                      </div>
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
      <button v-if="results && !isSaved" @click="saveApplication" :disabled="savingApplication" class="btn btn-success">
        <span v-if="savingApplication">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Saving Application...
        </span>
        <span v-else>
          💾 Save Application
        </span>
      </button>
      <button v-if="results && isSaved" class="btn btn-success opacity-50 cursor-not-allowed">
        ✅ Application Saved
      </button>
      <button v-if="results" @click="downloadAll" :disabled="isDownloadingAll" class="btn btn-primary">
        <span v-if="isDownloadingAll">Downloading ZIP...</span>
        <span v-else>Download All Files (ZIP)</span>
      </button>
    </div>

    <!-- Regenerate Cover Letter Modal -->
    <div v-if="showRegenerateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Regenerate Cover Letter</h3>
            <button @click="showRegenerateModal = false" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <div class="mb-4">
            <p class="text-sm text-gray-600 mb-4">
              Generate a new version of your cover letter with different AI settings. Your resume will remain unchanged.
            </p>
            
            <!-- Original Settings Info -->
            <div v-if="originalSettings.provider" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p class="text-xs text-blue-700 mb-1">
                <strong>Original Generation Settings:</strong>
              </p>
              <p class="text-xs text-blue-600">
                {{ originalSettings.provider }} • {{ originalSettings.model }} • {{ originalSettings.personality }}
              </p>
            </div>
            
            <!-- Provider Selection -->
            <div class="mb-3">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                AI Provider
                <span v-if="isUsingOriginalSettings" class="ml-1 text-xs text-green-600">(Original)</span>
              </label>
              <select v-model="regenSettings.provider" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                <option value="gemini">Gemini (Google)</option>
                <option value="openai">OpenAI</option>
                <option value="mistral">Mistral</option>
                <option value="groq">Groq</option>
              </select>
            </div>

            <!-- Model Selection -->
            <div class="mb-3">
              <label class="block text-sm font-medium text-gray-700 mb-1">Model</label>
              <select v-model="regenSettings.model" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                <option v-for="model in availableModels" :key="model.id" :value="model.id">
                  {{ model.name }} {{ model.recommended ? '⭐' : '' }}
                </option>
              </select>
            </div>

            <!-- Personality Selection -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">Writing Style</label>
              <select v-model="regenSettings.personality" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                <option value="career_savvy_colleague">Professional & Engaging</option>
                <option value="confident_professional">Confident & Direct</option>
                <option value="enthusiastic_applicant">Enthusiastic & Energetic</option>
                <option value="experienced_expert">Expert & Authoritative</option>
              </select>
            </div>
          </div>
          
          <div class="flex justify-between items-center">
            <button 
              v-if="originalSettings.provider && !isUsingOriginalSettings"
              @click="resetToOriginalSettings" 
              class="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              Reset to Original Settings
            </button>
            <div class="flex space-x-3">
              <button @click="showRegenerateModal = false" class="btn btn-secondary">
                Cancel
              </button>
              <button @click="startRegeneration" :disabled="regenerating.coverLetter" class="btn btn-primary">
                <span v-if="regenerating.coverLetter">Regenerating...</span>
                <span v-else>🔄 Regenerate Cover Letter</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Regeneration Progress Modal -->
    <div v-if="regenerating.coverLetter" class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3 text-center">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Regenerating Cover Letter</h3>
          
          <!-- Progress indicator -->
          <ProcessingStatus 
            :status="regenStatus.status" 
            :progress="regenStatus.progress" 
            :error="regenStatus.error"
            :step="regenStatus.step" 
            :detail="regenStatus.detail" 
            :provider="regenSettings.provider" 
          />
          
          <div class="mt-4">
            <button @click="cancelRegeneration" class="btn btn-secondary">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAPI } from '../composables/useAPI.js'
import { useAuth } from '../composables/useAuth.js'
import { getFullUrl } from '../config/api.js'
import ProcessingStatus from '../components/ProcessingStatus.vue'
import PDFViewer from '../components/PDFViewer.vue'
import LaTeXEditor from '../components/LaTeXEditor.vue'

const route = useRoute()
const { getResults, downloadFile: apiDownloadFile, downloadAllAsZip, addSkillToBaseline, checkStatus } = useAPI()
const { getToken } = useAuth()

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
const openSkillMenus = ref(new Set()) // Track which skill dropdowns are open

// Application saving state
const savingApplication = ref(false)
const isSaved = ref(false)
const applicationId = ref(null)

// Cover letter regeneration state
const showRegenerateModal = ref(false)
const regenerating = ref({
  coverLetter: false
})
const regenSettings = ref({
  provider: 'ollama',
  model: 'qwen2.5:14b-instruct',
  personality: 'career_savvy_colleague'
})

// Original generation settings (populated from results)
const originalSettings = ref({
  provider: null,
  model: null,
  personality: null
})
const regenStatus = ref({
  status: 'idle',
  progress: 0,
  step: '',
  detail: ''
})

let regenPollTimer = null

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
const isViewingSavedApplication = computed(() => route.name === 'Application')
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
const loadSavedApplication = async () => {
  try {
    loading.value = true
    error.value = null
    
    console.log('Loading saved application:', jobId.value)
    const token = getToken()
    
    const response = await fetch(`/api/applications/${jobId.value}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to load application: ${response.statusText}`)
    }
    
    const data = await response.json()
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to load application')
    }
    
    const app = data.application
    
    // Extract original jobId from multiple possible sources
    const originalJobId = app.generationMeta?.originalJobId ||
                         app.files?.resume?.storageKey?.split('/')[0] || 
                         app.files?.coverLetter?.storageKey?.split('/')[0] ||
                         jobId.value
    
    console.log('Saved application file mapping:', {
      applicationId: jobId.value,
      originalJobId: originalJobId,
      resumeStorageKey: app.files?.resume?.storageKey,
      coverLetterStorageKey: app.files?.coverLetter?.storageKey
    })
    
    // Transform saved application data to match Results format
    results.value = {
      jobId: originalJobId,
      jobDescription: app.jobDetails?.jobDescription || '',
      edits: {
        summary: { replace: app.jobDetails?.resume?.summary },
        skills: app.jobDetails?.resume?.skills || {},
        cover_letter: { paragraphs: app.jobDetails?.coverLetter?.paragraphs || [] }
      },
      suggestedAdditions: [],
      skillsChanges: {},
      validationStatus: null,
      reviewData: {
        overview: `This is a saved application for ${app.jobDetails?.jobTitle || 'Unknown Position'} at ${app.jobDetails?.companyName || 'Unknown Company'}.`,
        statistics: {
          total_chunks_modified: 0,
          skills_sections_updated: 0,
          cover_letter_paragraphs: app.jobDetails?.coverLetter?.paragraphs?.length || 0,
          suggested_additions: 0
        }
      },
      createdAt: app.createdAt,
      provider: app.generationMeta?.provider || 'unknown',
      model: app.generationMeta?.model || 'unknown'
    }
    
    console.log('Saved application loaded:', results.value)
    isSaved.value = true
    
  } catch (err) {
    console.error('Error loading saved application:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const loadResults = async () => {
  try {
    loading.value = true
    error.value = null

    console.log('Loading results for jobId:', jobId.value)
    const data = await getResults(jobId.value)
    console.log('Results loaded:', data)
    results.value = data
    
    // Set original settings for regeneration if available
    if (data.originalSettings) {
      originalSettings.value = data.originalSettings
      // Update regeneration settings to match original
      regenSettings.value = {
        provider: data.originalSettings.provider || 'ollama',
        model: data.originalSettings.model || 'qwen2.5:14b-instruct',
        personality: data.originalSettings.personality || 'career_savvy_colleague'
      }
    }
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

const saveApplication = async () => {
  try {
    savingApplication.value = true
    
    // Check if user is authenticated
    const token = getToken()
    if (!token) {
      throw new Error('You must be logged in to save applications')
    }
    
    // Build application data from results
    const applicationData = {
      jobTitle: extractJobTitle(results.value.jobDescription),
      companyName: extractCompanyName(results.value.jobDescription),
      jobDescription: results.value.jobDescription,
      
      resume: {
        fileName: 'resume.pdf',
        summary: results.value.edits?.summary?.replace || null,
        skills: results.value.edits?.skills || {}
      },
      
      coverLetter: {
        fileName: 'cover-letter.pdf',
        paragraphs: results.value.edits?.cover_letter?.paragraphs || []
      },

      generationMeta: {
        provider: results.value.provider || 'unknown',
        model: results.value.model || 'unknown',
        processingTime: 0,
        validationPassed: true,
        originalJobId: jobId.value  // Store original job ID for file lookup
      },

      files: {
        resume: {
          url: getFullUrl(`/api/view/${jobId.value}/resume`),
          storageKey: `${jobId.value}/resume.pdf`
        },
        coverLetter: {
          url: getFullUrl(`/api/view/${jobId.value}/cover-letter`), 
          storageKey: `${jobId.value}/cover-letter.pdf`
        }
      }
    }

    // First, create the application in generated_applications
    const createResponse = await fetch('/api/applications', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(applicationData)
    })

    if (!createResponse.ok) {
      throw new Error(`Failed to create application: ${createResponse.statusText}`)
    }

    const createResult = await createResponse.json()
    
    if (!createResult.success) {
      throw new Error(createResult.error || 'Failed to create application')
    }

    // Then save it permanently to saved_applications
    const saveResponse = await fetch(`/api/applications/${createResult.applicationId}/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({})
    })

    if (!saveResponse.ok) {
      throw new Error(`Failed to save application: ${saveResponse.statusText}`)
    }

    const saveResult = await saveResponse.json()
    
    if (!saveResult.success) {
      throw new Error(saveResult.error || 'Failed to save application')
    }

    // Success - application is now saved permanently
    applicationId.value = saveResult.applicationId
    isSaved.value = true
    
    // Show success message
    alert('✅ Application saved successfully! You can now track and manage this application in your database.')

  } catch (err) {
    console.error('Error saving application:', err)
    alert(`Failed to save application: ${err.message}`)
  } finally {
    savingApplication.value = false
  }
}

// Helper functions for job data extraction
const extractJobTitle = (jobDescription) => {
  if (!jobDescription) return 'Software Engineer'
  
  const patterns = [
    /Position:\s*([^\n\r]+)/i,
    /Role:\s*([^\n\r]+)/i,  
    /Job Title:\s*([^\n\r]+)/i,
    /seeking\s+(?:a\s+)?([A-Z][a-zA-Z\s]+?)(?:\s+at|\s*,|\s*\.)/i,
    /hiring\s+(?:a\s+)?([A-Z][a-zA-Z\s]+?)(?:\s+to|\s*,|\s*\.)/i
  ]
  
  for (const pattern of patterns) {
    const match = jobDescription.match(pattern)
    if (match) {
      return match[1].trim()
    }
  }
  
  return 'Software Engineer'
}

const extractCompanyName = (jobDescription) => {
  if (!jobDescription) return 'Unknown Company'
  
  const patterns = [
    /Company:\s*([^\n\r,]+)/i,
    /at\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+is\s|\s*,|\s*\.|$)/i,
    /join\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+as\s|\s*,|\s*\.|$)/i,
    /([A-Z][a-zA-Z\s&.,]+?)\s+is\s+(?:seeking|hiring|looking)/i
  ]
  
  for (const pattern of patterns) {
    const match = jobDescription.match(pattern)
    if (match) {
      let company = match[1].trim()
      // Clean up common suffixes  
      company = company.replace(/\s+(Inc\.?|LLC\.?|Ltd\.?|Corp\.?|Corporation)\.?$/i, '')
      return company
    }
  }
  
  return 'Unknown Company'
}

// Regeneration methods
const availableModels = computed(() => {
  const modelsByProvider = {
    gemini: [
      { id: 'gemini-2.5-flash-lite', name: 'Gemini 2.5 Flash-Lite', recommended: true },
      { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', recommended: false },
      { id: 'gemini-1.5-pro-latest', name: 'Gemini 1.5 Pro', recommended: false }
    ],
    openai: [
      { id: 'gpt-4o-mini', name: 'GPT-4o Mini', recommended: true },
      { id: 'gpt-4o', name: 'GPT-4o', recommended: false }
    ],
    mistral: [
      { id: 'mistral-large-latest', name: 'Mistral Large', recommended: true },
      { id: 'mistral-medium-latest', name: 'Mistral Medium', recommended: false }
    ],
    groq: [
      { id: 'llama-3.1-70b-versatile', name: 'Llama 3.1 70B', recommended: true },
      { id: 'llama-3.1-8b-instant', name: 'Llama 3.1 8B', recommended: false }
    ]
  }
  
  return modelsByProvider[regenSettings.value.provider] || []
})

const isUsingOriginalSettings = computed(() => {
  if (!originalSettings.value.provider) return false
  return (
    regenSettings.value.provider === originalSettings.value.provider &&
    regenSettings.value.model === originalSettings.value.model &&
    regenSettings.value.personality === originalSettings.value.personality
  )
})

const resetToOriginalSettings = () => {
  if (originalSettings.value.provider) {
    regenSettings.value = {
      provider: originalSettings.value.provider,
      model: originalSettings.value.model,
      personality: originalSettings.value.personality
    }
  }
}

const startRegeneration = async () => {
  try {
    showRegenerateModal.value = false
    regenerating.value.coverLetter = true
    
    // Start regeneration
    const response = await fetch(`/api/regenerate/${jobId.value}/cover-letter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(regenSettings.value)
    })
    
    if (!response.ok) {
      throw new Error(`Failed to start regeneration: ${response.statusText}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      // Start polling for status
      startRegenPolling()
    } else {
      throw new Error(result.error || 'Failed to start regeneration')
    }
    
  } catch (error) {
    console.error('Error starting regeneration:', error)
    alert(`Failed to start cover letter regeneration: ${error.message}`)
    regenerating.value.coverLetter = false
  }
}

const startRegenPolling = () => {
  regenPollTimer = setInterval(async () => {
    try {
      const response = await fetch(`/api/regenerate/${jobId.value}/status`)
      const status = await response.json()
      
      regenStatus.value = status
      
      if (status.status === 'completed') {
        clearInterval(regenPollTimer)
        regenPollTimer = null
        regenerating.value.coverLetter = false
        
        // Refresh the cover letter PDF
        setTimeout(() => {
          coverLetterPdfKey.value++
          if (coverLetterPdfViewer.value) {
            coverLetterPdfViewer.value.forceRefresh()
          }
        }, 1000)
        
        alert('✅ Cover letter regenerated successfully! The new version is now displayed.')
        
      } else if (status.status === 'error') {
        clearInterval(regenPollTimer)
        regenPollTimer = null
        regenerating.value.coverLetter = false
        alert(`❌ Cover letter regeneration failed: ${status.error}`)
      }
      
    } catch (error) {
      console.error('Error polling regeneration status:', error)
    }
  }, 2000)
}

const cancelRegeneration = () => {
  if (regenPollTimer) {
    clearInterval(regenPollTimer)
    regenPollTimer = null
  }
  regenerating.value.coverLetter = false
  regenStatus.value = { status: 'idle', progress: 0, step: '', detail: '' }
}

const handleProcessingCancel = () => {
  console.log('Processing cancelled by user')
  
  // Clear any polling timers
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  
  // Reset status
  statusData.value = { status: 'idle', progress: 0 }
  
  // Navigate back to home
  window.location.href = '/home'
}

const toggleSkillMenu = (skill) => {
  if (openSkillMenus.value.has(skill)) {
    openSkillMenus.value.delete(skill)
  } else {
    // Close all other menus first
    openSkillMenus.value.clear()
    openSkillMenus.value.add(skill)
  }
}

const handleAddSkill = async (skill, category = 'conversational_skills', confidenceLevel = null) => {
  try {
    addingSkills.value.add(skill)
    openSkillMenus.value.delete(skill) // Close the dropdown
    
    await addSkillToBaseline(jobId.value, skill, category, confidenceLevel)
    
    // Show success message with better UX
    let categoryDisplay = category === 'confirmed_skills' ? 'confirmed skill' : 'conversational skill'
    let confidenceDisplay = ''
    
    if (confidenceLevel) {
      const confidenceLabels = {
        'expert': 'Expert level',
        'proficient': 'Proficient level', 
        'familiar': 'Familiar level',
        'learning': 'Learning level'
      }
      confidenceDisplay = ` as ${confidenceLabels[confidenceLevel]}`
    }
    
    const message = `✅ "${skill}" has been added to your skills inventory as a ${categoryDisplay}${confidenceDisplay}. This skill will no longer be flagged in future validations.`
    
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

// Recompile LaTeX content with polling-based verification
const recompileLatex = async (fileType, content) => {
  if (recompiling.value[fileType]) {
    return // Already recompiling
  }

  try {
    recompiling.value[fileType] = true

    // Import the enhanced recompile function
    const { recompileWithVerification } = await import('../utils/pdf-utils.js')

    console.log(`Starting recompilation for ${fileType}...`)
    const result = await recompileWithVerification(jobId.value, fileType, content)

    if (result.success) {
      console.log(`${fileType} recompiled successfully`, {
        updated: result.updated,
        fileSize: result.fileSize
      })

      if (result.updated) {
        // PDF was verified as updated, force refresh immediately
        console.log(`PDF verified as updated, refreshing viewer for ${fileType}`)

        if (fileType === 'resume') {
          resumePdfKey.value++
          if (resumePdfViewer.value) {
            resumePdfViewer.value.forceRefresh()
          }
        } else if (fileType === 'cover-letter') {
          coverLetterPdfKey.value++
          if (coverLetterPdfViewer.value) {
            coverLetterPdfViewer.value.forceRefresh()
          }
        }
      } else {
        // PDF update wasn't verified, but compilation succeeded
        // Try a delayed refresh as fallback
        console.warn(`PDF update not verified for ${fileType}, trying delayed refresh`)
        setTimeout(() => {
          if (fileType === 'resume') {
            resumePdfKey.value++
            if (resumePdfViewer.value) {
              resumePdfViewer.value.forceRefresh()
            }
          } else if (fileType === 'cover-letter') {
            coverLetterPdfKey.value++
            if (coverLetterPdfViewer.value) {
              coverLetterPdfViewer.value.forceRefresh()
            }
          }
        }, 3000) // Longer fallback delay
      }
    } else {
      throw new Error(result.error || 'Recompilation failed')
    }
  } catch (err) {
    console.error(`Failed to recompile ${fileType}:`, err)
    // Show user-friendly error notification
    const errorMessage = `Failed to update ${fileType === 'resume' ? 'resume' : 'cover letter'} PDF: ${err.message}`
    alert(errorMessage) // You might want to replace this with a proper toast notification
  } finally {
    recompiling.value[fileType] = false
  }
}

// Click outside handler for skill dropdowns
const handleClickOutside = (event) => {
  // Close all skill dropdowns if clicking outside
  if (openSkillMenus.value.size > 0) {
    const target = event.target
    const isDropdownClick = target.closest('.skill-dropdown')
    if (!isDropdownClick) {
      openSkillMenus.value.clear()
    }
  }
}

// Lifecycle
onMounted(async () => {
  if (!jobId.value) {
    error.value = 'No job ID provided'
    loading.value = false
    return
  }

  console.log('Component mounted, isViewingSavedApplication:', isViewingSavedApplication.value)

  if (isViewingSavedApplication.value) {
    // Load saved application directly
    console.log('Loading saved application...')
    await loadSavedApplication()
    // Set status to completed since it's a saved application
    statusData.value = { status: 'completed', progress: 100 }
  } else {
    // Check initial status first for new jobs
    console.log('Checking initial status for new job...')
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
  }
  
  // Add click outside listener
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (resumeRecompileTimeout) clearTimeout(resumeRecompileTimeout)
  if (coverLetterRecompileTimeout) clearTimeout(coverLetterRecompileTimeout)
  if (regenPollTimer) clearInterval(regenPollTimer)
  document.removeEventListener('click', handleClickOutside)
})
</script>