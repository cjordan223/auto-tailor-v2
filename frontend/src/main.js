import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './assets/style.css'

// Import views
import Home from './views/Home.vue'
import Results from './views/Results.vue'
import Settings from './views/Settings.vue'

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/results/:jobId',
      name: 'Results',
      component: Results,
      props: true
    },
    {
      path: '/settings',
      name: 'Settings', 
      component: Settings
    }
  ]
})

// Create and mount app
createApp(App)
  .use(router)
  .mount('#app')