import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)
app.mount('#app')

// 앱 로드 직후에 한 번만 호출
const authStore = useAuthStore(pinia)
authStore.fetchUserInfo().catch(() => {})