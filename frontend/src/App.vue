<template>
  <div id="app" class="h-screen flex flex-col">
    <!-- Dark Mode Toggle -->
    <button @click="toggleDarkMode" class="dark-mode-toggle"
      :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'">
      <svg v-if="isDarkMode" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z">
        </path>
      </svg>
      <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
      </svg>
    </button>

    <!-- Navigation -->
    <nav class="glassmorphism-nav flex-shrink-0">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-12">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-2 group">
              <div class="text-2xl animate-float">📄</div>
              <span
                class="text-lg font-bold text-gray-900 group-hover:text-green-600 transition-colors duration-300">Tex-Tailor</span>
            </router-link>
          </div>

          <div class="flex items-center space-x-2">
            <!-- Authenticated user navigation -->
            <template v-if="isAuthenticated">
              <router-link to="/home" class="nav-link text-gray-700 hover:text-green-600 text-sm font-medium"
                :class="{ 'active': $route.name === 'Home' }">
                Home
              </router-link>
              <router-link to="/dashboard" class="nav-link text-gray-700 hover:text-green-600 text-sm font-medium"
                :class="{ 'active': $route.name === 'Dashboard' }">
                Dashboard
              </router-link>
              <router-link to="/settings" class="nav-link text-gray-700 hover:text-green-600 text-sm font-medium"
                :class="{ 'active': $route.name === 'Settings' }">
                Settings
              </router-link>

              <!-- User menu -->
              <div class="flex items-center space-x-2 ml-3 pl-3 border-l border-gray-200">
                <span class="text-xs text-gray-600">{{ user?.email }}</span>
                <button @click="handleLogout" class="text-xs text-red-600 hover:text-red-500 font-medium">
                  Logout
                </button>
              </div>
            </template>

            <!-- Guest navigation -->
            <template v-else>
              <router-link to="/login" class="nav-link text-gray-700 hover:text-green-600 text-sm font-medium"
                :class="{ 'active': $route.name === 'Login' }">
                Login
              </router-link>
              <router-link to="/register"
                class="nav-link text-green-600 hover:text-green-700 text-sm font-medium bg-green-50 hover:bg-green-100 px-3 py-1 rounded-md transition-colors"
                :class="{ 'active': $route.name === 'Register' }">
                Sign Up
              </router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto">
      <div class="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 min-h-full">
        <router-view />
      </div>
    </main>

    <!-- Footer -->
    <!-- <footer class="glassmorphism-footer flex-shrink-0">
      <div class="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
        <div class="text-center text-sm text-gray-600">
          <p>© 2025 Tex-Tailor. AI-powered resume customization with style ✨</p>
        </div>
      </div>
    </footer> -->
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from './composables/useAuth.js'

const router = useRouter()
const { user, isAuthenticated, logout, initialize } = useAuth()

// Dark mode state
const isDarkMode = ref(true) // Default to dark mode

// Initialize authentication state when app mounts
onMounted(() => {
  initialize()

  // Load dark mode preference from localStorage
  const savedMode = localStorage.getItem('darkMode')
  if (savedMode !== null) {
    isDarkMode.value = savedMode === 'true'
  }

  // Apply initial theme
  applyTheme()
})

// Toggle dark mode
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('darkMode', isDarkMode.value.toString())
  applyTheme()
}

// Apply theme to body
const applyTheme = () => {
  if (isDarkMode.value) {
    document.body.classList.remove('light-mode')
  } else {
    document.body.classList.add('light-mode')
  }
}

// Handle logout
const handleLogout = async () => {
  logout()
  // Redirect to welcome page after logout
  await router.push('/')
}
</script>