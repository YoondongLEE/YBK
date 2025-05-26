<template>
  <div>
    <header>
      <NavBar />
    </header>
    
    <main class="main-content">
      <router-view></router-view>
    </main>
    
    <footer class="footer">
      <div class="footer-content">
        © {{ currentYear }} 금융 정보 서비스 | 이윤동 김봉주 | SSAFY 최종 프로젝트
      </div>
    </footer>
    
    <!-- 커스텀 알림 컴포넌트 -->
    <AlertNotification
      :show="alertStore.isVisible"
      :title="alertStore.title"
      :message="alertStore.message"
      :type="alertStore.type"
      :duration="alertStore.duration"
      :auto-close="alertStore.autoClose"
      @close="alertStore.closeAlert"
    />
  </div>
</template>

<script setup>
import { computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import NavBar from './components/NavBar.vue';
import AlertNotification from './components/common/AlertNotification.vue';
import { useAlertStore } from './stores/alert';
import { useAuthStore } from './stores/auth';
import { useYoutubeStore } from './stores/youtube';

const alertStore = useAlertStore();
const authStore = useAuthStore();
const youtubeStore = useYoutubeStore();
const router = useRouter();
const currentYear = computed(() => new Date().getFullYear());
const isAuthenticated = computed(() => authStore.isAuthenticated);

// 인증 상태 변경을 감시
watch(() => isAuthenticated.value, (newValue) => {
  // 인증 상태가 변경되면 YouTube 데이터 초기화
  youtubeStore.refreshOnAuthChange();
});

onMounted(async () => {
  try {
    // 저장된 토큰으로 사용자 정보 불러오기
    if (authStore.token) {
      console.log('토큰 존재, 사용자 정보 로드 시도:', authStore.token);
      await authStore.fetchUserInfo();
      console.log('사용자 정보 로드됨:', authStore.user);
      // 사용자 객체를 문자열화하여 구조 확인
      console.log('사용자 객체 구조:', JSON.stringify(authStore.user));
    } else {
      console.log('토큰 없음, 로그인 필요');
    }
  } catch (error) {
    console.error('사용자 정보 로드 실패:', error);
  }
});
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Noto Sans KR', Arial, sans-serif;
  background-color: #f5f5f7;
  color: #333;
}

.main-content {
  min-height: calc(100vh - 150px);
  padding-bottom: 30px;
}

.footer {
  background-color: #f1f1f1;
  padding: 20px 0;
  text-align: center;
  border-top: 1px solid #ddd;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  color: #666;
  font-size: 14px;
}
</style>