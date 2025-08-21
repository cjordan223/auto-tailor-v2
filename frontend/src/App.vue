<template>
  <div id="app" class="h-screen flex flex-col bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200 flex-shrink-0">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-2">
              <div class="text-2xl font-bold text-primary-600">📄</div>
              <span class="text-xl font-bold text-gray-900">Tex-Tailor</span>
            </router-link>
          </div>
          
          <div class="flex items-center space-x-4">
            <router-link 
              to="/" 
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              :class="{ 'text-primary-600 bg-primary-50': $route.name === 'Home' }"
            >
              Home
            </router-link>
            <router-link 
              to="/settings" 
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              :class="{ 'text-primary-600 bg-primary-50': $route.name === 'Settings' }"
            >
              Settings
            </router-link>
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
    <footer class="bg-white border-t border-gray-200 flex-shrink-0">
      <div class="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
        <div class="text-center text-sm text-gray-500">
          <p>© 2025 Tex-Tailor. AI-powered resume customization.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
// Add any global app logic here
</script>