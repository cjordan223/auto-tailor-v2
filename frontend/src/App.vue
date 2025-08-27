<template>
  <div id="app" class="h-screen flex flex-col">
    <!-- Navigation -->
    <nav class="glassmorphism-nav flex-shrink-0">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-3 group">
              <div class="text-3xl animate-float">📄</div>
              <span
                class="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-300">Tex-Tailor</span>
            </router-link>
          </div>

          <div class="flex items-center space-x-2">
            <!-- Always show Home -->
            <router-link to="/" class="nav-link text-gray-700 hover:text-blue-600 text-sm font-medium"
              :class="{ 'active': $route.name === 'Home' }">
              Home
            </router-link>
            
            <!-- Authenticated user navigation -->
            <template v-if="isAuthenticated">
              <router-link to="/dashboard" class="nav-link text-gray-700 hover:text-blue-600 text-sm font-medium"
                :class="{ 'active': $route.name === 'Dashboard' }">
                Dashboard
              </router-link>
              <router-link to="/settings" class="nav-link text-gray-700 hover:text-blue-600 text-sm font-medium"
                :class="{ 'active': $route.name === 'Settings' }">
                Settings
              </router-link>
              
              <!-- User menu -->
              <div class="flex items-center space-x-3 ml-4 pl-4 border-l border-gray-200">
                <span class="text-sm text-gray-600">{{ user?.email }}</span>
                <button @click="handleLogout" class="text-sm text-red-600 hover:text-red-500 font-medium">
                  Logout
                </button>
              </div>
            </template>
            
            <!-- Guest navigation -->
            <template v-else>
              <router-link to="/login" class="nav-link text-gray-700 hover:text-blue-600 text-sm font-medium"
                :class="{ 'active': $route.name === 'Login' }">
                Login
              </router-link>
              <router-link to="/register" class="nav-link text-blue-600 hover:text-blue-700 text-sm font-medium bg-blue-50 hover:bg-blue-100 px-3 py-1 rounded-md transition-colors"
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
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 min-h-full">
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
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from './composables/useAuth.js'

const router = useRouter()
const { user, isAuthenticated, logout, initialize } = useAuth()

// Initialize authentication state when app mounts
onMounted(() => {
  initialize()
})

// Handle logout
const handleLogout = async () => {
  logout()
  // Redirect to home page after logout
  await router.push('/')
}
</script>