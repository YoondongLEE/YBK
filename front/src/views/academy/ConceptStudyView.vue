<template>
  <div class="concept-study-container">
    <div class="study-header">
      <button @click="goBack" class="back-button">← 카테고리로</button>
      <div class="header-info">
        <h1>{{ categoryInfo.name }}</h1>
        <p>{{ getDifficultyLabel(difficulty) }} · {{ totalQuestions }}개 문제</p>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>문제를 불러오는 중...</p>
    </div>

    <div v-else-if="questions.length > 0" class="study-content">
      <div class="study-info">
        <div class="info-card">
          <h3>📖 학습 안내</h3>
          <ul>
            <li>각 문제와 함께 정답과 해설을 확인할 수 있습니다</li>
            <li>정답은 ✓ 표시로 구분됩니다</li>
            <li>해설을 통해 개념을 정확히 이해해보세요</li>
            <li>스크롤하여 모든 문제를 학습할 수 있습니다</li>
          </ul>
        </div>
      </div>

      <div class="questions-list">
        <div 
          v-for="(question, index) in questions" 
          :key="question.id"
          class="question-item"
        >
          <div class="question-header">
            <span class="question-number">Q{{ index + 1 }}</span>
            <div class="question-tags">
              <span class="difficulty-tag">{{ getDifficultyLabel(difficulty) }}</span>
              <span v-if="question.keywords" class="keywords-tag">
                🔖 {{ question.keywords }}
              </span>
            </div>
          </div>

          <div class="question-text">
            {{ question.text }}
          </div>

          <div class="choices-section">
            <h4>선택지</h4>
            <div class="choices">
              <div 
                v-for="choice in question.choices" 
                :key="choice.id"
                class="choice-item"
                :class="{ 'correct': choice.is_correct }"
              >
                <span class="choice-number">{{ getChoiceLabel(choice, question.choices) }}</span>
                <span class="choice-text">{{ choice.text }}</span>
                <span v-if="choice.is_correct" class="correct-mark">✓ 정답</span>
              </div>
            </div>
          </div>

          <div class="explanation-section">
            <h4>💡 해설</h4>
            <div class="explanation-content">
              {{ question.explanation }}
            </div>
          </div>
        </div>
      </div>

      <div class="study-complete">
        <div class="complete-card">
          <h3>🎉 학습 완료!</h3>
          <p>{{ categoryInfo.name }} 카테고리의 모든 문제를 학습했습니다.</p>
          <div class="action-buttons">
            <button @click="goToQuiz" class="quiz-button">
              📝 퀴즈로 실력 확인
            </button>
            <button @click="goBack" class="back-to-category">
              📚 다른 카테고리 학습
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-questions">
      <p>해당 카테고리의 문제를 찾을 수 없습니다.</p>
      <button @click="goBack" class="back-button">카테고리로 돌아가기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const difficulty = ref(route.params.difficulty)
const categoryId = ref(route.params.categoryId)
const questions = ref([])
const categoryInfo = ref({})
const totalQuestions = ref(0)
const loading = ref(true)

const getDifficultyLabel = (diff) => {
  const labels = {
    'youth': '청소년',
    'adult_basic': '성인 기본',
    'adult_advanced': '성인 심화'
  }
  return labels[diff] || diff
}

// 선택지 라벨 생성 (A, B, C, D)
const getChoiceLabel = (choice, allChoices) => {
  const index = allChoices.findIndex(c => c.id === choice.id)
  return String.fromCharCode(65 + index) // A, B, C, D
}

const fetchConceptStudyData = async () => {
  try {
    loading.value = true
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/finance-academy/concept-study/${difficulty.value}/category/${categoryId.value}/`
    )
    
    questions.value = response.data.questions
    categoryInfo.value = response.data.category
    totalQuestions.value = response.data.total_questions
    
  } catch (error) {
    console.error('개념 학습 데이터 조회 실패:', error)
    alert('학습 데이터를 불러오는데 실패했습니다.')
    goBack()
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({
    name: 'concept-category',
    params: { difficulty: difficulty.value }
  })
}

const goToQuiz = () => {
  router.push({
    name: 'problem-learning',
    params: { difficulty: difficulty.value }
  })
}

onMounted(() => {
  fetchConceptStudyData()
})
</script>

<style scoped>
.concept-study-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.study-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  background: white;
  padding: 25px;
  border-radius: 16px;
  box-shadow: 0 2px 20px rgba(0,0,0,0.1);
}

.back-button {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.back-button:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
}

.header-info h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 5px;
}

.header-info p {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.loading {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #ecf0f1;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.study-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.study-info {
  background: white;
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 2px 20px rgba(0,0,0,0.1);
}

.info-card h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.3rem;
}

.info-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.info-card li {
  padding: 8px 0;
  color: #555;
  position: relative;
  padding-left: 25px;
}

.info-card li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #27ae60;
  font-weight: bold;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.question-item {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  border-left: 4px solid #3498db;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.question-number {
  background: #3498db;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 14px;
}

.question-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.difficulty-tag {
  background: #e74c3c;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.keywords-tag {
  background: #f39c12;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.question-text {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 25px;
  line-height: 1.6;
  color: #2c3e50;
}

.choices-section {
  margin-bottom: 25px;
}

.choices-section h4 {
  color: #34495e;
  margin-bottom: 15px;
  font-size: 16px;
}

.choices {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.choice-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.choice-item.correct {
  border-color: #27ae60;
  background: #e8f5e8;
}

.choice-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 25px;
  height: 25px;
  background: #95a5a6;
  color: white;
  border-radius: 50%;
  font-weight: bold;
  margin-right: 12px;
  flex-shrink: 0;
  font-size: 12px;
}

.choice-item.correct .choice-number {
  background: #27ae60;
}

.choice-text {
  flex: 1;
  color: #2c3e50;
}

.correct-mark {
  background: #27ae60;
  color: white;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
  margin-left: 10px;
}

.explanation-section {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  padding: 20px;
  border-radius: 12px;
  border-left: 4px solid #2196f3;
}

.explanation-section h4 {
  margin: 0 0 12px 0;
  color: #1976d2;
  font-size: 16px;
}

.explanation-content {
  color: #424242;
  font-size: 15px;
  line-height: 1.7;
}

.study-complete {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  text-align: center;
}

.complete-card h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.5rem;
}

.complete-card p {
  color: #7f8c8d;
  margin-bottom: 25px;
  font-size: 1.1rem;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.quiz-button, .back-to-category {
  padding: 12px 25px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.quiz-button {
  background: #3498db;
  color: white;
}

.back-to-category {
  background: #95a5a6;
  color: white;
}

.quiz-button:hover, .back-to-category:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

.no-questions {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

@media (max-width: 768px) {
  .concept-study-container {
    padding: 15px;
  }
  
  .study-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-info h1 {
    font-size: 1.5rem;
  }
  
  .question-item {
    padding: 20px;
  }
  
  .question-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .question-text {
    font-size: 16px;
  }
  
  .choice-item {
    padding: 12px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons button {
    width: 100%;
  }
}
</style>