<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900 mb-2">Dashboard</h1>
      <p class="text-lg text-gray-600">Track and manage your job applications</p>
    </div>

    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="glassmorphism p-4 rounded-lg">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <span class="text-2xl">📋</span>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">Total Applications</p>
            <p class="text-2xl font-bold text-gray-900">{{ filteredApplications.length }}</p>
          </div>
        </div>
      </div>
      
      <div class="glassmorphism p-4 rounded-lg">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <span class="text-2xl">✅</span>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">Applied</p>
            <p class="text-2xl font-bold text-green-600">{{ getStatusCount('applied') }}</p>
          </div>
        </div>
      </div>
      
      <div class="glassmorphism p-4 rounded-lg">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <span class="text-2xl">🎯</span>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">Interviews</p>
            <p class="text-2xl font-bold text-purple-600">{{ getStatusCount('interview') }}</p>
          </div>
        </div>
      </div>
      
      <div class="glassmorphism p-4 rounded-lg">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <span class="text-2xl">❌</span>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">Rejected</p>
            <p class="text-2xl font-bold text-red-600">{{ getStatusCount('rejected') }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Applications Table -->
    <div class="glassmorphism p-6">
      <div class="mb-6">
        <h2 class="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
          <span class="text-2xl mr-2">📊</span>
          Job Applications Tracker
        </h2>
        
        <!-- Search and Filter Controls -->
        <div class="flex flex-col lg:flex-row gap-4 items-center justify-between mb-6">
          <!-- Search Bar -->
          <div class="flex-1 max-w-md">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search by job title or company..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                @input="debouncedSearch"
              />
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span class="text-gray-500">🔍</span>
              </div>
            </div>
          </div>
          
          <!-- Filter Buttons -->
          <div class="flex space-x-2">
            <button
              v-for="status in filterOptions"
              :key="status.value"
              @click="selectedFilter = status.value"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200',
                selectedFilter === status.value
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              ]"
            >
              {{ status.label }}
            </button>
          </div>
          
          <!-- Sort Dropdown -->
          <select
            v-model="sortBy"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @change="fetchSavedApplications"
          >
            <option value="createdAt">Date Saved (Newest)</option>
            <option value="updatedAt">Last Updated</option>
            <option value="jobTitle">Job Title (A-Z)</option>
            <option value="companyName">Company (A-Z)</option>
          </select>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loadingSaved" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-gray-600 mt-2">Loading applications...</p>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="filteredApplications.length === 0" class="text-center py-8 text-gray-500">
        <div class="text-6xl mb-4">📭</div>
        <p class="text-xl">No applications found</p>
        <p class="text-sm mt-2">
          {{ searchQuery || selectedFilter !== 'all' ? 'Try adjusting your search or filters' : 'Start by creating your first application!' }}
        </p>
      </div>
      
      <!-- Applications Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full border-collapse bg-white rounded-lg shadow-sm">
          <!-- Table Header -->
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Job Title
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Saved Date
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Updated
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                AI Provider
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Notes
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          
          <!-- Table Body -->
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="app in filteredApplications" 
              :key="app._id"
              class="hover:bg-gray-50 transition-colors duration-150"
            >
              <!-- Job Title -->
              <td class="px-4 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span class="text-blue-600 text-sm font-medium">
                      {{ getJobTitleInitial(app.jobDetails?.jobTitle) }}
                    </span>
                  </div>
                  <div class="ml-3">
                    <div class="text-sm font-medium text-gray-900">
                      {{ app.jobDetails?.jobTitle || 'Untitled Position' }}
                    </div>
                    <div v-if="app.jobDetails?.location" class="text-sm text-gray-500">
                      📍 {{ app.jobDetails.location }}
                    </div>
                  </div>
                </div>
              </td>
              
              <!-- Company -->
              <td class="px-4 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ app.jobDetails?.companyName || 'Unknown Company' }}
                </div>
                <div v-if="app.jobDetails?.jobUrl" class="text-sm text-gray-500">
                  <a :href="app.jobDetails.jobUrl" target="_blank" class="text-blue-600 hover:text-blue-800">
                    🔗 View Job
                  </a>
                </div>
              </td>
              
              <!-- Status -->
              <td class="px-4 py-4 whitespace-nowrap">
                <select
                  :value="app.status"
                  @change="handleStatusChange(app._id, $event.target.value)"
                  class="text-sm rounded-full px-3 py-1 font-medium border-0 focus:ring-2 focus:ring-blue-500"
                  :class="getStatusClasses(app.status)"
                >
                  <option value="saved">Saved</option>
                  <option value="applied">Applied</option>
                  <option value="interview">Interview</option>
                  <option value="rejected">Rejected</option>
                </select>
              </td>
              
              <!-- Saved Date -->
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(app.createdAt) }}
              </td>
              
              <!-- Last Updated -->
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(app.updatedAt) }}
              </td>
              
              <!-- AI Provider -->
              <td class="px-4 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  {{ app.generationMeta?.provider || 'Unknown' }}
                </div>
                <div class="text-xs text-gray-500">
                  {{ app.generationMeta?.model || 'Unknown Model' }}
                </div>
              </td>
              
              <!-- Notes -->
              <td class="px-4 py-4 whitespace-nowrap">
                <div v-if="app.trackingInfo?.notes" class="text-sm text-gray-900 max-w-xs truncate" :title="app.trackingInfo.notes">
                  {{ app.trackingInfo.notes }}
                </div>
                <div v-else class="text-sm text-gray-400 italic">
                  No notes
                </div>
              </td>
              
              <!-- Actions -->
              <td class="px-4 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <button
                    @click="viewApplication(app._id)"
                    class="text-blue-600 hover:text-blue-900 transition-colors duration-150"
                    title="View Details"
                  >
                    👁️
                  </button>
                  <button
                    @click="downloadApplication(app._id)"
                    class="text-green-600 hover:text-green-900 transition-colors duration-150"
                    title="Download Files"
                  >
                    📥
                  </button>
                  <button
                    @click="addNotes(app._id)"
                    class="text-yellow-600 hover:text-yellow-900 transition-colors duration-150"
                    title="Add Notes"
                  >
                    📝
                  </button>
                  <button
                    @click="archiveApplication(app._id)"
                    class="text-red-600 hover:text-red-900 transition-colors duration-150"
                    title="Archive"
                  >
                    🗄️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Load More Button -->
        <div v-if="hasMoreApplications" class="text-center mt-6">
          <button
            @click="loadMoreApplications"
            :disabled="loadingMore"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            <span v-if="loadingMore">Loading...</span>
            <span v-else>Load More Applications</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

// Reactive data
const loadingSaved = ref(true)
const loadingMore = ref(false)
const savedApplications = ref([])
const searchQuery = ref('')
const selectedFilter = ref('all')
const sortBy = ref('createdAt')
const hasMoreApplications = ref(true)
const currentPage = ref(0)

// Filter options
const filterOptions = [
  { value: 'all', label: 'All' },
  { value: 'saved', label: 'Saved' },
  { value: 'applied', label: 'Applied' },
  { value: 'interview', label: 'Interview' },
  { value: 'rejected', label: 'Rejected' }
]

// Computed properties
const filteredApplications = computed(() => {
  let filtered = savedApplications.value

  // Filter by status
  if (selectedFilter.value !== 'all') {
    filtered = filtered.filter(app => app.status === selectedFilter.value)
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(app => 
      app.jobDetails?.jobTitle?.toLowerCase().includes(query) ||
      app.jobDetails?.companyName?.toLowerCase().includes(query)
    )
  }

  return filtered
})

// Debounced search function
let searchTimeout
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchSavedApplications(true)
  }, 300)
}

// Helper functions
const getJobTitleInitial = (jobTitle) => {
  if (!jobTitle) return '?'
  return jobTitle.charAt(0).toUpperCase()
}

const getStatusCount = (status) => {
  return savedApplications.value.filter(app => app.status === status).length
}

const getStatusClasses = (status) => {
  switch (status) {
    case 'saved':
      return 'bg-blue-100 text-blue-800'
    case 'applied':
      return 'bg-green-100 text-green-800'
    case 'interview':
      return 'bg-purple-100 text-purple-800'
    case 'rejected':
      return 'bg-red-100 text-red-800'
    case 'draft':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return 'Today'
  } else if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7)
    return `${weeks} week${weeks > 1 ? 's' : ''} ago`
  } else {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined 
    })
  }
}

// API functions
const fetchSavedApplications = async (reset = false) => {
  if (reset) {
    currentPage.value = 0
    savedApplications.value = []
    hasMoreApplications.value = true
  }
  
  loadingSaved.value = reset || currentPage.value === 0
  
  try {
    const params = new URLSearchParams({
      limit: '50',
      skip: (currentPage.value * 50).toString(),
      sortBy: sortBy.value,
      sortOrder: 'desc'
    })
    
    if (selectedFilter.value !== 'all') {
      params.set('status', selectedFilter.value)
    }
    
    const response = await fetch(`/api/applications/saved?${params}`)
    const result = await response.json()
    
    if (result.success) {
      const newApps = result.applications || []
      
      if (reset) {
        savedApplications.value = newApps
      } else {
        savedApplications.value = [...savedApplications.value, ...newApps]
      }
      
      hasMoreApplications.value = newApps.length === 50
      currentPage.value++
    }
  } catch (error) {
    console.error('Error fetching saved applications:', error)
  } finally {
    loadingSaved.value = false
    loadingMore.value = false
  }
}

const loadMoreApplications = () => {
  loadingMore.value = true
  fetchSavedApplications()
}

// Event handlers
const handleStatusChange = async (applicationId, newStatus) => {
  try {
    const response = await fetch(`/api/applications/${applicationId}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: newStatus })
    })
    
    if (response.ok) {
      // Update the application in the array
      const appIndex = savedApplications.value.findIndex(app => app._id === applicationId)
      if (appIndex !== -1) {
        savedApplications.value[appIndex].status = newStatus
        savedApplications.value[appIndex].updatedAt = new Date().toISOString()
      }
    }
  } catch (error) {
    console.error('Error updating application status:', error)
  }
}

const viewApplication = (applicationId) => {
  // Navigate to application details page
  window.location.href = `/application/${applicationId}`
}

const downloadApplication = async (applicationId) => {
  try {
    const response = await fetch(`/api/applications/${applicationId}/download`)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `application-${applicationId}.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    }
  } catch (error) {
    console.error('Error downloading application:', error)
  }
}

const addNotes = async (applicationId) => {
  const notes = prompt('Add notes for this application:')
  if (notes !== null) {
    try {
      const response = await fetch(`/api/applications/${applicationId}/notes`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notes: notes })
      })
      
      if (response.ok) {
        // Update the application in the array
        const appIndex = savedApplications.value.findIndex(app => app._id === applicationId)
        if (appIndex !== -1) {
          savedApplications.value[appIndex].trackingInfo = savedApplications.value[appIndex].trackingInfo || {}
          savedApplications.value[appIndex].trackingInfo.notes = notes
          savedApplications.value[appIndex].updatedAt = new Date().toISOString()
        }
      }
    } catch (error) {
      console.error('Error adding notes:', error)
    }
  }
}

const archiveApplication = async (applicationId) => {
  if (confirm('Are you sure you want to archive this application?')) {
    try {
      const response = await fetch(`/api/applications/${applicationId}/archive`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ archived: true })
      })
      
      if (response.ok) {
        // Remove from array
        savedApplications.value = savedApplications.value.filter(app => app._id !== applicationId)
      }
    } catch (error) {
      console.error('Error archiving application:', error)
    }
  }
}

// Watchers
watch(selectedFilter, () => {
  fetchSavedApplications(true)
})

// Lifecycle
onMounted(() => {
  fetchSavedApplications()
})
</script>

<style scoped>
/* Glassmorphism effect */
.glassmorphism {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Table styling */
table {
  border-radius: 8px;
  overflow: hidden;
}

th {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Hover effects */
tr:hover {
  background-color: rgba(59, 130, 246, 0.05);
}

/* Status select styling */
select {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
  padding-right: 32px;
}
</style>