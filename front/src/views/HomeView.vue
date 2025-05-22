<!-- filepath: c:\Users\SSAFY\LYD\final-pjt\front\src\views\HomeView.vue -->
<template>
  <div class="home-container">
    <div class="main-banner">
      <!-- 사진이 들어갈 메인 공간 -->
      <h2>윤봉길 금융 아카데미</h2>
      <div class="banner-placeholder">
        <!-- 나중에 이미지로 대체될 공간 -->
        <p>메인 배너 이미지가 들어갈 공간입니다</p>
      </div>
    </div>
    
    <div class="menu-section">
      <div class="menu-item academy" @click="navigateTo('financeAcademy')">
        <h2>금융 아카데미 (TEST)</h2>
        <p>금융 교육 콘텐츠를 제공합니다</p>
      </div>
      
      <div class="menu-item info" @click="navigateTo('financeInfo')">
        <h2>금융 정보 길잡이 (INFO)</h2>
        <p>유용한 금융 정보를 확인하세요</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const navigateTo = (routeName) => {
  router.push({ name: routeName });
};
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.main-banner {
  width: 100%;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.banner-placeholder {
  width: 100%;
  height: 300px;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.menu-section {
  display: flex;
  gap: 20px;
}

.menu-item {
  flex: 1;
  padding: 30px;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  text-align: center;
  transition: transform 0.3s;
}

.menu-item:hover {
  transform: translateY(-5px);
}

.academy {
  background-color: #4a90e2;
}

.info {
  background-color: #4a90e2;
}

h2 {
  margin-bottom: 10px;
}
</style>