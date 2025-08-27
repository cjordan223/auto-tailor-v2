<template>
  <div class="min-h-full flex items-center justify-center px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl w-full space-y-8 text-center">
      <!-- Hero Section -->
      <div>
        <div class="mx-auto h-16 w-16 flex items-center justify-center text-6xl mb-6">
          📄
        </div>
        <h1 class="text-4xl md:text-6xl font-bold text-white mb-4 drop-shadow-lg">
          Tex-Tailor
        </h1>
        <h2 class="text-xl md:text-2xl font-semibold text-gray-100 mb-6">
          AI-Powered Resume Customization
        </h2>
        <p class="text-lg text-gray-200 max-w-2xl mx-auto mb-8">
          Transform your resume for every job application with intelligent AI customization. 
          Upload your job description and let our AI tailor your resume to match perfectly.
        </p>
      </div>

      <!-- Features -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        <div class="glassmorphism-card p-6 rounded-xl">
          <div class="text-3xl mb-3">🎯</div>
          <h3 class="text-lg font-semibold text-white mb-2">Perfect Match</h3>
          <p class="text-gray-200 text-sm">AI analyzes job requirements and customizes your resume to highlight relevant skills and experience.</p>
        </div>
        <div class="glassmorphism-card p-6 rounded-xl">
          <div class="text-3xl mb-3">⚡</div>
          <h3 class="text-lg font-semibold text-white mb-2">Lightning Fast</h3>
          <p class="text-gray-200 text-sm">Get your customized resume and cover letter in minutes, not hours of manual editing.</p>
        </div>
        <div class="glassmorphism-card p-6 rounded-xl">
          <div class="text-3xl mb-3">📊</div>
          <h3 class="text-lg font-semibold text-white mb-2">Professional Quality</h3>
          <p class="text-gray-200 text-sm">LaTeX-powered formatting ensures your documents look polished and professional.</p>
        </div>
      </div>

      <!-- Call to Action -->
      <div class="space-y-6">
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <router-link 
            to="/register" 
            class="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 px-8 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            Get Started Free
          </router-link>
          <router-link 
            to="/login" 
            class="w-full sm:w-auto border-2 border-white/30 hover:border-white/50 text-white font-semibold py-3 px-8 rounded-lg transition-all duration-300 hover:bg-white/10 backdrop-blur-sm"
          >
            Sign In
          </router-link>
        </div>
        
        <p class="text-sm text-gray-300">
          Join thousands of job seekers who've landed their dream jobs with perfectly tailored resumes.
        </p>
      </div>

      <!-- How it Works -->
      <div class="mt-16">
        <h3 class="text-2xl font-bold text-white mb-8">How It Works</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg mx-auto mb-4">1</div>
            <h4 class="font-semibold text-white mb-2">Upload Job Description</h4>
            <p class="text-gray-200 text-sm">Paste or upload the job posting you're applying for</p>
          </div>
          <div class="text-center">
            <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg mx-auto mb-4">2</div>
            <h4 class="font-semibold text-white mb-2">AI Customization</h4>
            <p class="text-gray-200 text-sm">Our AI analyzes requirements and tailors your resume</p>
          </div>
          <div class="text-center">
            <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg mx-auto mb-4">3</div>
            <h4 class="font-semibold text-white mb-2">Download & Apply</h4>
            <p class="text-gray-200 text-sm">Get your customized resume and cover letter instantly</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// No additional logic needed - this is a static landing page
</script>