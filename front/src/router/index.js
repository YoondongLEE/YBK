import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import SignUpView from '../views/SignUpView.vue'
import FinanceAcademyView from '../views/FinanceAcademyView.vue'
import FinanceInfoView from '../views/FinanceInfoView.vue'
import MyPageView from '../views/MyPageView.vue'
import { useAuthStore } from '../stores/auth'
import InterestRateCompare from '@/views/InterestRateCompare.vue'
import DepositList from '@/views/DepositList.vue'
import SavingDetail from '@/views/SavingDetail.vue'
import MetalPriceView from '../views/MetalPriceView.vue'
import CommunityView from '@/views/CommunityView.vue'
import PostListView from '@/views/community/PostListView.vue'
import PostDetailView from '@/views/community/PostDetailView.vue'
import PostCreateView from '@/views/community/PostCreateView.vue'
import PostEditView from '@/views/community/PostEditView.vue'


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
      path: '/finance/rates',
      name: 'interest-rate-compare',
      component: InterestRateCompare,
      meta: { requiresAuth: false }
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
      name: 'deposit-list',
      component: DepositList,
      meta: { requiresAuth: false }
    },
    
    // 예금 상세 페이지 (중복된 라우트 제거)
    {
      path: '/deposits/:id',
      name: 'deposit-detail',
      component: () => import('@/views/DepositDetail.vue'),
      meta: { requiresAuth: false }
    },
    
    // 새로운 금리비교 페이지 (예금/적금 통합)
    {
      path: '/interest-compare',
      name: 'interest-compare',
      component: () => import('../views/InterestRateCompare.vue')
    },
    
    // 적금 상세 페이지
    {
      path: '/savings/:id',
      name: 'saving-detail',
      component: SavingDetail,
      meta: { requiresAuth: false }
    },
    
    // 금/은 가격 변동 페이지 추가
    {
      path: '/metal-prices',
      name: 'metal-prices',
      component: MetalPriceView,
      meta: {
        title: '금/은 가격 변동'
      }
    },
    {
    path: '/community',
    name: 'community',
    component: CommunityView,
    children: [
      {
        path: '',
        name: 'post-list',
        component: PostListView
      },
      {
        path: 'create',
        name: 'post-create',
        component: PostCreateView,
        meta: { requiresAuth: true }
      },
      {
        path: ':id',
        name: 'post-detail',
        component: PostDetailView
      },
      {
        path: ':id/edit',
        name: 'post-edit',
        component: PostEditView,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 아카데미
  {
    path: '/finance-academy',
    name: 'financeAcademy',
    component: () => import('../views/FinanceAcademyView.vue')
  }
  // 다음 라우트는 구현 준비가 완료되면 주석 해제하세요
  /*
  {
    path: '/finance-academy/problem-learning',
    name: 'problem-learning',
    component: () => import('../views/academy/ProblemLearningView.vue')
  },
  {
    path: '/finance-academy/concept-learning',
    name: 'concept-learning',
    component: () => import('../views/academy/ConceptLearningView.vue')
  },
  {
    path: '/finance-academy/exam',
    name: 'exam',
    component: () => import('../views/academy/ExamView.vue')
  }
  */
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