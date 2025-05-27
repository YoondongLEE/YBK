<template>
  <div class="problem-learning-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>문제를 불러오는 중...</p>
    </div>

    <div v-else-if="!quizStarted && !showResults" class="quiz-intro">
      <h1>{{ getDifficultyLabel(difficulty) }} 문제 풀이</h1>
      <div class="intro-card">
        <h2>학습 방법</h2>
        <ul>
          <li>랜덤으로 선택된 10문제가 출제됩니다</li>
          <li>각 문제당 시간 제한은 없습니다</li>
          <li>1문제씩 결과와 해설을 확인할 수 있습니다</li>
          <li>신중하게 답을 선택해주세요</li>
          <li>매번 다른 문제가 출제됩니다</li>
        </ul>
        <button class="start-btn" @click="startQuiz">시작하기</button>
      </div>
    </div>

    <!-- 문제 풀이 단계 -->
    <div v-else-if="quizStarted && !showResults" class="quiz-container">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }"></div>
      </div>
      
      <div class="question-info">
        <span class="question-number">{{ currentQuestionIndex + 1 }} / {{ questions.length }}</span>
        <span class="difficulty-badge">{{ getDifficultyLabel(difficulty) }}</span>
        <span class="score-display">점수: {{ quizScore }} / {{ totalAnswered }}</span>
      </div>

      <div v-if="currentQuestion" class="question-card">
        <!-- 문제 출제 단계 -->
        <div v-if="currentStep === 'solving'" class="question-solving">
          <h2 class="question-text">{{ currentQuestion.text }}</h2>
          
          <div class="choices">
            <button 
              v-for="choice in currentQuestion.choices" 
              :key="choice.id"
              class="choice-btn"
              :class="{ selected: selectedChoice && selectedChoice.id === choice.id }"
              @click="selectChoice(choice)"
            >
              <span class="choice-number">{{ getChoiceLabel(choice.id) }}</span>
              <span class="choice-text">{{ choice.text }}</span>
            </button>
          </div>

          <div class="action-buttons">
            <button 
              v-if="selectedChoice"
              class="submit-btn"
              @click="submitAnswer"
              :disabled="submitting"
            >
              {{ submitting ? '제출 중...' : '답안 제출' }}
            </button>
          </div>
        </div>

        <!-- 정답 확인 단계 -->
        <div v-if="currentStep === 'result'" class="result-step">
          <h2 class="question-text">{{ currentQuestion.text }}</h2>
          
          <div class="result-header" :class="{ 'correct': answerResult.is_correct, 'incorrect': !answerResult.is_correct }">
            <div class="result-icon">
              {{ answerResult.is_correct ? '🎉' : '😞' }}
            </div>
            <div class="result-text">
              {{ answerResult.is_correct ? '정답입니다!' : '오답입니다.' }}
            </div>
          </div>

          <div class="answer-comparison">
            <div class="answer-item" :class="{ 'user-wrong': !answerResult.is_correct }">
              <div class="answer-label">선택한 답:</div>
              <div class="answer-content">{{ answerResult.selected_choice.text }}</div>
            </div>
            
            <div v-if="!answerResult.is_correct" class="answer-item correct-answer">
              <div class="answer-label">정답:</div>
              <div class="answer-content">{{ answerResult.correct_choice.text }}</div>
            </div>
          </div>

          <div class="explanation-section">
            <h4>💡 해설</h4>
            <div class="explanation-content">
              {{ answerResult.explanation }}
            </div>
          </div>

          <div class="action-buttons">
            <button
              v-if="!isLastQuestion()"
              @click="goToNextQuestion"
              class="next-question-btn"
            >
              다음 문제 →
            </button>
            <button
              v-else
              @click="showFinalResults"
              class="finish-btn"
            >
              결과 확인
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 최종 결과 -->
    <div v-else-if="showResults" class="results-container">
      <div class="score-card">
        <h1>퀴즈 완료!</h1>
        <div class="score-display">
          <div class="score-circle">
            <span class="score-number">{{ quizScore }}</span>
            <span class="score-total">/ {{ questions.length }}</span>
          </div>
          <div class="score-percentage">
            {{ Math.round((quizScore / questions.length) * 100) }}%
          </div>
        </div>
        
        <div class="result-message">
          <div v-if="(quizScore / questions.length) >= 0.8" class="excellent">
            🌟 훌륭합니다! 금융 지식이 우수하네요!
          </div>
          <div v-else-if="(quizScore / questions.length) >= 0.6" class="good">
            👍 잘했습니다! 조금 더 공부하면 완벽해요!
          </div>
          <div v-else class="needs-improvement">
            📚 더 공부해보세요! 금융 지식을 늘려가는 중이에요!
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <button class="retry-btn" @click="retryQuiz">다시 풀기</button>
        <button class="back-btn" @click="goBack">돌아가기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const difficulty = ref(route.params.difficulty)
const loading = ref(true)
const quizStarted = ref(false)
const showResults = ref(false)
const questions = ref([])
const currentQuestionIndex = ref(0)
const currentStep = ref('solving') // 'solving' | 'result'
const selectedChoice = ref(null)
const answerResult = ref(null)
const quizScore = ref(0)
const totalAnswered = ref(0)
const submitting = ref(false)

const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value]
})

const getDifficultyLabel = (diff) => {
  const labels = {
    'youth': '청소년',
    'adult_basic': '성인 기본',
    'adult_advanced': '성인 심화'
  }
  return labels[diff] || diff
}

// 선택지 라벨 생성 (A, B, C, D)
const getChoiceLabel = (choiceId) => {
  const currentQ = currentQuestion.value
  if (!currentQ) return ''
  
  const index = currentQ.choices.findIndex(choice => choice.id === choiceId)
  return String.fromCharCode(65 + index) // A, B, C, D
}

// 마지막 문제인지 확인
const isLastQuestion = () => {
  return currentQuestionIndex.value >= questions.value.length - 1
}

// 선택지 선택
const selectChoice = (choice) => {
  selectedChoice.value = choice
}

// 랜덤 10문제 가져오기 (기존 API 사용)
const fetchRandomQuestions = async () => {
  try {
    loading.value = true
    // 백엔드의 랜덤 10문제 API 사용
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/finance-academy/quiz/${difficulty.value}/`)
    
    // API 응답 구조에 맞게 수정
    if (response.data.questions) {
      questions.value = response.data.questions
    } else {
      questions.value = response.data
    }
    
    console.log('랜덤 문제 로드 완료:', questions.value.length, '문제')
  } catch (error) {
    console.error('랜덤 문제를 가져오는데 실패했습니다:', error)
    alert('문제를 불러오는데 실패했습니다.')
    router.push({ name: 'financeAcademy' })
  } finally {
    loading.value = false
  }
}

const startQuiz = async () => {
  // 퀴즈 시작할 때마다 새로운 랜덤 문제 가져오기
  try {
    await fetchRandomQuestions()
    quizStarted.value = true
    currentStep.value = 'solving'
    currentQuestionIndex.value = 0
    selectedChoice.value = null
    answerResult.value = null
    quizScore.value = 0
    totalAnswered.value = 0
  } catch (error) {
    console.error('퀴즈 시작 실패:', error)
  }
}

// 답안 제출
const submitAnswer = async () => {
  if (!selectedChoice.value || submitting.value) return
  
  submitting.value = true
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/finance-academy/questions/${currentQuestion.value.id}/submit/`,
      { choice_id: selectedChoice.value.id },
      {
        headers: {
          Authorization: `Token ${authStore.token}`
        }
      }
    )
    
    answerResult.value = response.data
    totalAnswered.value += 1
    
    // 정답이면 점수 증가
    if (response.data.is_correct) {
      quizScore.value += 1
    }
    
    // 결과 확인 단계로 이동
    currentStep.value = 'result'
    
  } catch (error) {
    console.error('답안 제출 실패:', error)
    alert('답안 제출 중 오류가 발생했습니다.')
  } finally {
    submitting.value = false
  }
}

// 다음 문제로 이동
const goToNextQuestion = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value += 1
    currentStep.value = 'solving'
    selectedChoice.value = null
    answerResult.value = null
  }
}

// 최종 결과 표시
const showFinalResults = () => {
  showResults.value = true
  quizStarted.value = false
}

const retryQuiz = async () => {
  // 다시 풀기 시에도 새로운 랜덤 문제 가져오기
  quizStarted.value = false
  showResults.value = false
  await startQuiz()
}

const goBack = () => {
  router.push({ name: 'financeAcademy' })
}

// 초기 로드 시에는 문제를 가져오지 않고 시작 화면만 표시
onMounted(() => {
  loading.value = false
})
</script>

<style scoped>
.problem-learning-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Noto Sans KR', sans-serif;
}

.loading {
  text-align: center;
  padding: 50px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4a90e2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.quiz-intro {
  text-align: center;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.intro-card h1 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 2rem;
}

.intro-card h2 {
  color: #34495e;
  margin-bottom: 20px;
}

.intro-card ul {
  list-style: none;
  padding: 0;
  margin: 20px 0;
}

.intro-card li {
  padding: 8px 0;
  color: #555;
  position: relative;
  padding-left: 25px;
}

.intro-card li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #27ae60;
  font-weight: bold;
}

.start-btn {
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: white;
  border: none;
  padding: 15px 40px;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 20px;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.quiz-container {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 20px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.5s ease;
}

.question-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 10px;
}

.question-number {
  font-weight: bold;
  color: #2c3e50;
  font-size: 16px;
}

.difficulty-badge {
  background: #e74c3c;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.score-display {
  font-weight: bold;
  color: #27ae60;
  font-size: 16px;
}

.question-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 20px;
}

.question-text {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 25px;
  line-height: 1.6;
  color: #2c3e50;
}

.choices {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 25px;
}

.choice-btn {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background: white;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 15px;
}

.choice-btn:hover {
  border-color: #3498db;
  background: #f8f9fa;
}

.choice-btn.selected {
  border-color: #3498db;
  background: #e3f2fd;
}

.choice-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 25px;
  height: 25px;
  background: #3498db;
  color: white;
  border-radius: 50%;
  font-weight: bold;
  margin-right: 12px;
  flex-shrink: 0;
  font-size: 12px;
}

.choice-btn.selected .choice-number {
  background: #2980b9;
}

.choice-text {
  flex: 1;
}

.action-buttons {
  text-align: center;
  margin-top: 20px;
}

.submit-btn {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 결과 확인 단계 스타일 */
.result-step {
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.result-header.correct {
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  border: 2px solid #28a745;
}

.result-header.incorrect {
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  border: 2px solid #dc3545;
}

.result-icon {
  font-size: 24px;
}

.result-text {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.answer-comparison {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.answer-item {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.answer-item.user-wrong {
  background: #ffe6e6;
  border-color: #ff9999;
}

.answer-item.correct-answer {
  background: #e6ffe6;
  border-color: #99dd99;
}

.answer-label {
  font-weight: bold;
  color: #555;
  margin-bottom: 4px;
  font-size: 13px;
}

.answer-content {
  color: #333;
  font-size: 14px;
}

.explanation-section {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  border-left: 4px solid #2196f3;
}

.explanation-section h4 {
  margin: 0 0 12px 0;
  color: #1976d2;
  font-size: 16px;
}

.explanation-content {
  color: #424242;
  font-size: 14px;
  line-height: 1.6;
}

.next-question-btn, .finish-btn {
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.next-question-btn:hover, .finish-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

/* 최종 결과 스타일 */
.results-container {
  text-align: center;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.score-card h1 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 2rem;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.2);
}

.score-number {
  font-size: 24px;
  font-weight: bold;
}

.score-total {
  font-size: 14px;
  opacity: 0.9;
}

.score-percentage {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 20px;
}

.result-message {
  margin: 20px 0;
  font-size: 16px;
  font-weight: 500;
}

.excellent { color: #27ae60; }
.good { color: #3498db; }
.needs-improvement { color: #f39c12; }

.retry-btn, .back-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  margin: 10px;
}

.retry-btn {
  background: #27ae60;
  color: white;
}

.back-btn {
  background: #95a5a6;
  color: white;
}

.retry-btn:hover, .back-btn:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

@media (max-width: 768px) {
  .problem-learning-container {
    padding: 15px;
  }
  
  .quiz-container {
    padding: 20px;
  }
  
  .question-text {
    font-size: 18px;
  }
  
  .choice-btn {
    padding: 12px;
    font-size: 14px;
  }
}
</style>