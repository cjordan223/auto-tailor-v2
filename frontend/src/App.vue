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
            <router-link to="/" class="nav-link text-gray-700 hover:text-blue-600 text-sm font-medium"
              :class="{ 'active': $route.name === 'Home' }">
              Home
            </router-link>
            <router-link to="/settings" class="nav-link text-gray-700 hover:text-blue-600 text-sm font-medium"
              :class="{ 'active': $route.name === 'Settings' }">
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
// Add any global app logic here
</script>