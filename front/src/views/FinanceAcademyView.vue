<template>
  <div class="finance-academy-container">
    <h1>금융 아카데미</h1>
    <p class="subtitle">체계적인 학습을 통해 금융 지식을 쌓아보세요</p>
    
    <div class="academy-cards">
      <!-- 문제로 학습하기 카드 -->
      <div class="academy-card" @click="showComingSoon('문제로 학습하기')">
        <div class="card-image">
          <img src="@/assets/icons/problems.png" alt="문제로 학습하기">
        </div>
        <div class="card-content">
          <h3>문제로 학습하기</h3>
          <p>다양한 문제를 풀면서 금융 개념을 학습하고 실력을 향상시키세요.</p>
        </div>
      </div>
      
      <!-- 개념으로 학습하기 카드 -->
      <div class="academy-card" @click="showComingSoon('개념으로 학습하기')">
        <div class="card-image">
          <img src="@/assets/icons/concept.png" alt="개념으로 학습하기">
        </div>
        <div class="card-content">
          <h3>개념으로 학습하기</h3>
          <p>금융 기초 개념부터 고급 내용까지 체계적으로 학습하세요.</p>
        </div>
      </div>
      
      <!-- 평가 응시 카드 -->
      <div class="academy-card" @click="showComingSoon('평가 응시')">
        <div class="card-image">
          <img src="@/assets/icons/test.png" alt="평가 응시">
        </div>
        <div class="card-content">
          <h3>평가 응시</h3>
          <p>학습한 내용을 평가를 통해 확인하고 금융 전문가로 성장하세요.</p>
        </div>
      </div>
    </div>
    
    <!-- 학습 진행 현황 섹션 (선택사항) -->
    <div class="progress-section" v-if="isAuthenticated">
      <h2>나의 학습 현황</h2>
      <div class="progress-container">
        <div class="progress-item">
          <div class="progress-title">
            <span>문제 풀이 진행률</span>
            <span class="progress-percentage">{{ progressData.problem }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-filled" :style="{width: `${progressData.problem}%`}"></div>
          </div>
        </div>
        
        <div class="progress-item">
          <div class="progress-title">
            <span>개념 학습 진행률</span>
            <span class="progress-percentage">{{ progressData.concept }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-filled" :style="{width: `${progressData.concept}%`}"></div>
          </div>
        </div>
        
        <div class="progress-item">
          <div class="progress-title">
            <span>평가 응시 현황</span>
            <span class="progress-percentage">{{ progressData.exam }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-filled" :style="{width: `${progressData.exam}%`}"></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 로그인 안 된 경우 안내 메시지 -->
    <div class="login-notice" v-else>
      <p>
        <i class="bi bi-info-circle"></i>
        로그인하시면 학습 진행 현황을 확인하고 개인화된 학습 경험을 제공받을 수 있습니다.
        <router-link to="/login" class="login-link">로그인하기 →</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const isAuthenticated = ref(authStore.isAuthenticated);

// 학습 진행 현황 데이터 (실제로는 API에서 가져오거나 상태 관리에서 가져와야 함)
const progressData = ref({
  problem: 65,
  concept: 40,
  exam: 30
});

// 기능 준비 중 메시지 표시
const showComingSoon = (feature) => {
  alert(`${feature} 기능은 현재 개발 중입니다. 곧 만나보실 수 있습니다!`);
};
</script>

<style scoped>
.finance-academy-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Noto Sans KR', sans-serif;
}

h1 {
  margin-bottom: 10px;
  color: #333;
  font-weight: 700;
  position: relative;
  display: inline-block;
  padding-bottom: 8px;
}

h1::after {
  content: '';
  position: absolute;
  width: 60px;
  height: 3px;
  background-color: #4a90e2;
  bottom: 0;
  left: 0;
}

.subtitle {
  color: #666;
  font-size: 16px;
  margin-bottom: 40px;
}

.academy-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 30px;
  margin-bottom: 50px;
}

.academy-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  cursor: pointer;
  background-color: white;
  height: 280px;
}

.academy-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.card-image {
  height: 180px;
  width: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa; /* 배경색 추가하여 이미지가 작아져도 자연스럽게 */
}

.card-image::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 50%, rgba(0, 0, 0, 0.5) 100%);
  z-index: 1;
  opacity: 0;
  transition: opacity 0.3s;
}

.academy-card:hover .card-image::before {
  opacity: 1;
}

.card-image img {
  max-height: 100%; /* 높이도 90%로 제한 */
  width: auto; /* 원본 비율 유지 */
  height: auto; /* 원본 비율 유지 */
  object-fit: contain; /* cover에서 contain으로 변경하여 이미지가 잘리지 않게 함 */
  transition: transform 0.5s;
}
.academy-card:hover .card-image img {
  transform: scale(1.05); /* 1.08에서 1.05로 줄여 과도한 확대 방지 */
}

.card-content {
  padding: 20px;
  position: relative;
  z-index: 2;
}

.card-content h3 {
  margin: 0 0 8px;
  color: #222;
  font-size: 18px;
  font-weight: 600;
}

.card-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

/* 트렌디한 카드 액션 버튼 추가 */
.academy-card::after {
  content: '→';
  position: absolute;
  top: 20px;
  right: 20px;
  width: 30px;
  height: 30px;
  background-color: #4a90e2;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
  z-index: 5;
}

.academy-card:hover::after {
  opacity: 1;
  transform: translateX(0);
}

/* 카드 타입별 색상 다르게 적용 */
.academy-card:nth-child(1)::after {
  background-color: #4a90e2; /* 파란색 - 문제로 학습하기 */
}

.academy-card:nth-child(2)::after {
  background-color: #27ae60; /* 녹색 - 개념으로 학습하기 */
}

.academy-card:nth-child(3)::after {
  background-color: #e74c3c; /* 빨간색 - 평가 응시 */
}

/* 학습 진행 현황 섹션 스타일 */
.progress-section {
  background-color: #f9f9f9;
  padding: 30px;
  border-radius: 16px;
  margin-top: 40px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
}

.progress-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 24px;
  color: #333;
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-item {
  width: 100%;
}

.progress-title {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-weight: 500;
  color: #333;
}

.progress-percentage {
  color: #4a90e2;
  font-weight: bold;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #eee;
  border-radius: 4px;
  overflow: hidden;
}

.progress-filled {
  height: 100%;
  background: linear-gradient(to right, #4a90e2, #5ca9fb);
  transition: width 0.5s ease;
}

/* 로그인 안내 메시지 스타일 */
.login-notice {
  margin-top: 40px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #4a90e2;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.login-link {
  color: #4a90e2;
  text-decoration: none;
  margin-left: 5px;
  font-weight: 500;
}

.login-link:hover {
  text-decoration: underline;
}

/* 부드러운 트랜지션 효과 추가 */
* {
  transition-property: transform, box-shadow, opacity, background-color, color;
  transition-duration: 0.3s;
  transition-timing-function: ease;
}

@media (max-width: 768px) {
  .academy-cards {
    grid-template-columns: 1fr;
  }
  
  .progress-section {
    padding: 20px;
  }
}
</style>