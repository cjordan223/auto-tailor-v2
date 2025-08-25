<template>
  <div 
    class="application-card glassmorphism p-6 rounded-xl border border-gray-200 hover:shadow-lg transition-all duration-300 group relative"
    :class="{ 'compact': compact }"
  >
    <!-- Status Badge -->
    <div class="absolute top-4 right-4">
      <span 
        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
        :class="statusClasses"
      >
        {{ statusLabels[application.status] || application.status }}
      </span>
    </div>

    <!-- Main Content -->
    <div class="pr-16"> <!-- Add right padding to avoid status badge -->
      <!-- Job Title -->
      <h3 class="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors duration-200">
        {{ application.jobTitle || 'Untitled Position' }}
      </h3>

      <!-- Company Name -->
      <div class="flex items-center text-gray-600 mb-3">
        <span class="text-lg mr-2">🏢</span>
        <span class="font-medium">{{ application.companyName || 'Unknown Company' }}</span>
      </div>

      <!-- Metadata -->
      <div class="space-y-2 text-sm text-gray-500">
        <div class="flex items-center">
          <span class="text-sm mr-2">📅</span>
          <span>Saved {{ formatDate(application.createdAt) }}</span>
        </div>
        
        <div v-if="application.updatedAt && application.updatedAt !== application.createdAt" class="flex items-center">
          <span class="text-sm mr-2">🔄</span>
          <span>Updated {{ formatDate(application.updatedAt) }}</span>
        </div>

        <div v-if="application.generationMeta?.provider" class="flex items-center">
          <span class="text-sm mr-2">🤖</span>
          <span>{{ application.generationMeta.provider }} / {{ application.generationMeta.model || 'Unknown Model' }}</span>
        </div>
      </div>

      <!-- Notes Preview (if exists) -->
      <div v-if="application.notes" class="mt-3 p-2 bg-yellow-50 border-l-2 border-yellow-200 rounded">
        <p class="text-sm text-gray-700 line-clamp-2">
          <span class="text-yellow-600 mr-1">📝</span>
          {{ application.notes }}
        </p>
      </div>
    </div>

    <!-- Action Buttons (appear on hover) -->
    <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-5 rounded-xl transition-all duration-200 flex items-end justify-end p-4 opacity-0 group-hover:opacity-100">
      <div class="flex space-x-2">
        <!-- Status Change Dropdown -->
        <div class="relative" ref="statusDropdown">
          <button
            @click="toggleStatusMenu"
            class="px-3 py-2 bg-white text-gray-700 text-sm rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors duration-200 flex items-center space-x-1"
          >
            <span>Status</span>
            <span class="text-xs">▼</span>
          </button>
          
          <div 
            v-if="showStatusMenu"
            class="absolute bottom-full right-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10 min-w-32"
          >
            <button
              v-for="status in statusOptions"
              :key="status.value"
              @click="changeStatus(status.value)"
              :disabled="status.value === application.status"
              class="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              {{ status.label }}
            </button>
          </div>
        </div>

        <!-- Archive Button -->
        <button
          @click="archiveApplication"
          class="px-3 py-2 bg-red-100 text-red-700 text-sm rounded-lg hover:bg-red-200 transition-colors duration-200"
          title="Archive Application"
        >
          🗄️ Archive
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  application: {
    type: Object,
    required: true
  },
  compact: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['status-change', 'archive'])

// Reactive data
const showStatusMenu = ref(false)
const statusDropdown = ref(null)

// Status options
const statusOptions = [
  { value: 'saved', label: 'Saved' },
  { value: 'applied', label: 'Applied' },
  { value: 'interview', label: 'Interview' },
  { value: 'rejected', label: 'Rejected' }
]

// Status styling
const statusClasses = computed(() => {
  const status = props.application.status
  const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
  
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
    case 'archived':
      return 'bg-gray-100 text-gray-500'
    default:
      return 'bg-gray-100 text-gray-800'
  }
})

const statusLabels = {
  'saved': 'Saved',
  'applied': 'Applied', 
  'interview': 'Interview',
  'rejected': 'Rejected',
  'draft': 'Draft',
  'archived': 'Archived'
}

// Methods
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

const toggleStatusMenu = () => {
  showStatusMenu.value = !showStatusMenu.value
}

const changeStatus = (newStatus) => {
  showStatusMenu.value = false
  if (newStatus !== props.application.status) {
    emit('status-change', props.application._id, newStatus)
  }
}

const archiveApplication = () => {
  if (confirm(`Are you sure you want to archive "${props.application.jobTitle}" at ${props.application.companyName}?`)) {
    emit('archive', props.application._id)
  }
}

// Click outside handler
const handleClickOutside = (event) => {
  if (statusDropdown.value && !statusDropdown.value.contains(event.target)) {
    showStatusMenu.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.application-card {
  min-height: 200px;
}

.application-card.compact {
  min-height: 160px;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Glassmorphism effect - ensure it matches your existing styles */
.glassmorphism {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
</style>