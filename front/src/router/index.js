import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import SignUpView from '../views/SignUpView.vue'
import FinanceAcademyView from '../views/FinanceAcademyView.vue'
import FinanceInfoView from '../views/FinanceInfoView.vue'
import MyPageView from '../views/MyPageView.vue'
import { useAuthStore } from '../stores/auth'
import DepositList from '../views/DepositList.vue'
import DepositDetail from '../views/DepositDetail.vue'

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
      component: SignUpView 
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
    },
    {
      path: '/mypage',
      name: 'mypage',
      component: MyPageView,
      meta: { requiresAuth: true }
    },
    {
      path: '/deposits',
      name: 'deposits',
      component: DepositList
    },
    { path: '/deposits/:id', name: 'depositDetail', component: DepositDetail },

  ]
})

// 네비게이션 가드 설정 - 로그인 필요한 페이지 보호
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 인증이 필요한 페이지인지 확인
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 인증되지 않은 사용자는 로그인 페이지로 리다이렉트
    next({ name: 'login' })
  } else {
    // 그 외의 경우 정상적으로 라우팅
    next()
  }
})

export default router