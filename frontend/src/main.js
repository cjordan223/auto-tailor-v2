import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './assets/style.css'
import { useAuth } from './composables/useAuth.js'

// Import views
import Home from './views/Home.vue'
import Results from './views/Results.vue'
import Settings from './views/Settings.vue'
import DashboardView from './views/DashboardView.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
      meta: { requiresAuth: false }
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: { requiresAuth: false, guestOnly: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
      meta: { requiresAuth: false, guestOnly: true }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/results/:jobId',
      name: 'Results',
      component: Results,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/application/:applicationId',
      name: 'Application',
      component: Results,
      props: (route) => ({ jobId: route.params.applicationId }),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'Settings', 
      component: Settings,
      meta: { requiresAuth: true }
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, initialize } = useAuth()
  
  // Initialize auth state if needed
  await initialize()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    // Redirect to login with return url
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
    return
  }
  
  // Check if route is guest-only (login/register pages)
  if (to.meta.guestOnly && isAuthenticated.value) {
    // Redirect authenticated users away from login/register pages
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})

// Create and mount app
const app = createApp(App)

// Initialize auth state
const { initialize } = useAuth()
initialize()

app.use(router).mount('#app')