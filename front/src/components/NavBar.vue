<template>
  <nav class="navbar">
    <div class="container">
      <div class="navbar-brand">
        <router-link to="/">윤봉길</router-link>
      </div>
      
      <div class="navbar-menu">
        <div class="navbar-start">
          <router-link to="/" class="navbar-item">홈</router-link>
          <router-link to="/finance-academy" class="navbar-item">금융 아카데미</router-link>
          <router-link to="/finance-info" class="navbar-item">금융정보</router-link>
        </div>
        
        <div class="navbar-end">
          <template v-if="authStore.isAuthenticated">
            <router-link to="/mypage" class="navbar-item">마이페이지</router-link>
            <a @click="handleLogout" class="navbar-item">로그아웃</a>
          </template>
          <template v-else>
            <router-link to="/login" class="navbar-item">로그인</router-link>
            <router-link to="/signup" class="navbar-item">회원가입</router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const handleLogout = async () => {
  try {
    await authStore.logout();
    router.push({ name: 'home' });
  } catch (error) {
    console.error('로그아웃 실패:', error);
  }
};
</script>

<style scoped>
.navbar {
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
  margin-bottom: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.navbar-brand {
  font-size: 1.5rem;
  font-weight: bold;
}

.navbar-brand a {
  text-decoration: none;
  color: #333;
}

.navbar-menu {
  display: flex;
  justify-content: space-between;
  flex-grow: 1;
  margin-left: 20px;
}

.navbar-start, .navbar-end {
  display: flex;
  align-items: center;
}

.navbar-item {
  margin: 0 10px;
  text-decoration: none;
  color: #333;
  cursor: pointer;
  position: relative;
  padding: 5px 0;
  font-weight: 500;
  transition: color 0.3s ease;
}

.navbar-item:hover {
  color: #4a90e2;
}

/* 밑줄 효과 추가 */
.navbar-item::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: #4a90e2;
  transition: width 0.3s ease;
}

.navbar-item:hover::after {
  width: 100%;
}

/* 현재 활성화된 페이지 스타일 */
.router-link-active {
  color: #4a90e2;
}

.router-link-active::after {
  width: 100%;
  background-color: #4a90e2;
}
</style>