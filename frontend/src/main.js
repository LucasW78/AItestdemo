import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

// Import global styles
import './styles/main.scss'

const app = createApp(App)

// Use plugins
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { size: 'default' })

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err)
  console.error('Error Info:', info)
  // TODO: Add error reporting service
}

app.mount('#app')