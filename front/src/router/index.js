// filepath: c:\Users\SSAFY\LYD\final-pjt\front\src\router\index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import FinanceAcademyView from '../views/FinanceAcademyView.vue'
import FinanceInfoView from '../views/FinanceInfoView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView
    },
    {
      path: '/finance-academy',
      name: 'financeAcademy',
      component: FinanceAcademyView
    },
    {
      path: '/finance-info',
      name: 'financeInfo',
      component: FinanceInfoView
    }
  ]
})

export default router