<template>
  <div class="finance-academy-container">
    <h1>금융 아카데미</h1>
    <p class="subtitle">체계적인 학습을 통해 금융 지식을 쌓아보세요</p>
    
    <div class="academy-cards">
      <!-- 문제로 학습하기 카드 -->
      <div class="academy-card" @click="showDifficultySelector('problem')">
        <div class="card-image">
          <img src="@/assets/icons/problems.png" alt="문제로 학습하기">
        </div>
        <div class="card-content">
          <h3>문제로 학습하기</h3>
          <p>다양한 문제를 풀면서 금융 개념을 학습하고 실력을 향상시키세요.</p>
        </div>
      </div>
      
      <!-- 개념으로 학습하기 카드 -->
      <div class="academy-card" @click="showDifficultySelector('concept')">
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

    <!-- 난이도 선택 모달 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>{{ getModalTitle() }}</h2>
        <div class="difficulty-buttons">
          <button 
            v-for="difficulty in difficulties" 
            :key="difficulty.value"
            class="difficulty-btn"
            @click="selectDifficulty(difficulty.value)"
          >
            <h3>{{ difficulty.label }}</h3>
            <p>{{ getDifficultyDescription(difficulty.value) }}</p>
          </button>
        </div>
        <button class="close-btn" @click="closeModal">취소</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()
const isAuthenticated = ref(authStore.isAuthenticated)
const showModal = ref(false)
const difficulties = ref([])
const selectedType = ref('') // 'problem' 또는 'concept'

// 학습 진행 현황 데이터 (실제로는 API에서 가져오거나 상태 관리에서 가져와야 함)
const progressData = ref({
  problem: 65,
  concept: 40,
  exam: 30
})

// 기능 준비 중 메시지 표시
const showComingSoon = (feature) => {
  alert(`${feature} 기능은 현재 개발 중입니다. 곧 만나보실 수 있습니다!`)
}

const showDifficultySelector = (type) => {
  selectedType.value = type
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedType.value = ''
}

const getModalTitle = () => {
  if (selectedType.value === 'problem') {
    return '문제풀이 난이도를 선택하세요'
  } else if (selectedType.value === 'concept') {
    return '개념학습 난이도를 선택하세요'
  }
  return '난이도를 선택하세요'
}

const getDifficultyDescription = (difficulty) => {
  const descriptions = {
    'youth': '기초적인 금융 개념과 용어',
    'adult_basic': '실생활 금융 지식과 상품 이해',
    'adult_advanced': '투자와 자산관리, 심화 금융 지식'
  }
  return descriptions[difficulty] || ''
}

const selectDifficulty = (difficulty) => {
  if (selectedType.value === 'problem') {
    router.push({ 
      name: 'problem-learning', 
      params: { difficulty } 
    })
  } else if (selectedType.value === 'concept') {
    router.push({
      name: 'concept-category',
      params: { difficulty }
    })
  }
  closeModal()
}

// 기존 함수들과의 호환성을 위해 유지
const startQuiz = (difficulty) => {
  router.push({ 
    name: 'problem-learning', 
    params: { difficulty } 
  })
  closeModal()
}

const fetchDifficulties = async () => {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/finance-academy/quiz/difficulties/`)
    difficulties.value = response.data
  } catch (error) {
    console.error('난이도 목록을 가져오는데 실패했습니다:', error)
  }
}

onMounted(() => {
  fetchDifficulties()
})
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
  background-color: #f5f7fa;
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
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  transition: transform 0.5s;
}

.academy-card:hover .card-image img {
  transform: scale(1.05);
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

.academy-card:nth-child(1)::after {
  background-color: #4a90e2;
}

.academy-card:nth-child(2)::after {
  background-color: #27ae60;
}

.academy-card:nth-child(3)::after {
  background-color: #e74c3c;
}

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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 90%;
}

.modal-content h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.difficulty-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.difficulty-btn {
  padding: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.difficulty-btn:hover {
  border-color: #4a90e2;
  background-color: #f8f9fa;
  transform: translateY(-2px);
}

.difficulty-btn h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
}

.difficulty-btn p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.close-btn {
  width: 100%;
  padding: 12px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

.close-btn:hover {
  background: #5a6268;
}

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