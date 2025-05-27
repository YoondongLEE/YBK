<template>
  <div class="quiz-container">
    <div class="quiz-header">
      <h2>💰 금융교육 퀴즈</h2>
      <div class="quiz-progress">
        문제 {{ currentQuestionIndex + 1 }} / {{ totalQuestions }}
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${getProgress()}%` }"
          ></div>
        </div>
      </div>
      <div class="score-display">
        점수: {{ quizScore }} / {{ totalAnswered }}
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>문제를 불러오는 중...</p>
    </div>

    <div v-else-if="questions.length > 0" class="quiz-content">
      <div class="question-card">
        <div class="question-number">
          Q{{ currentQuestionIndex + 1 }}
        </div>
        
        <div class="question-text">
          {{ currentQuestion.text }}
        </div>

        <!-- 1단계: 문제 풀이 (선택지 선택 후 다음 버튼) -->
        <div v-if="currentStep === 'solving'" class="question-solving">
          <div class="choices">
            <button
              v-for="choice in currentQuestion.choices"
              :key="choice.id"
              @click="selectChoice(choice)"
              class="choice-button"
              :class="{ 'selected': selectedChoice && selectedChoice.id === choice.id }"
            >
              <span class="choice-number">{{ getChoiceLabel(choice.id) }}</span>
              <span class="choice-text">{{ choice.text }}</span>
            </button>
          </div>
          
          <div class="action-buttons">
            <button 
              v-if="selectedChoice"
              @click="submitAndShowResult" 
              class="next-button"
              :disabled="submitting"
            >
              {{ submitting ? '제출 중...' : '다음' }}
            </button>
          </div>
        </div>

        <!-- 2단계: 정답 확인 및 해설 -->
        <div v-if="currentStep === 'result'" class="result-step">
          <div class="result-header" :class="{ 'correct': answerResult.is_correct, 'incorrect': !answerResult.is_correct }">
            <div class="result-icon">
              {{ answerResult.is_correct ? '🎉' : '😞' }}
            </div>
            <div class="result-text">
              {{ answerResult.is_correct ? '정답입니다!' : '오답입니다.' }}
            </div>
          </div>

          <!-- 선택한 답과 정답 표시 -->
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

          <!-- 해설 -->
          <div class="explanation-section">
            <h4>💡 해설</h4>
            <div class="explanation-content">
              {{ answerResult.explanation }}
            </div>
          </div>

          <!-- 다음 문제 버튼 -->
          <div class="action-buttons">
            <button
              v-if="!isLastQuestion()"
              @click="goToNextQuestion"
              class="next-question-button"
            >
              다음 문제 →
            </button>
            <button
              v-else
              @click="showFinalResult"
              class="finish-button"
            >
              결과 확인
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-questions">
      <p>문제를 찾을 수 없습니다.</p>
      <button @click="goToQuizList" class="back-button">퀴즈 목록으로</button>
    </div>

    <!-- 최종 결과 모달 -->
    <div v-if="showFinalResults" class="final-result-modal" @click="closeFinalResult">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>🎊 퀴즈 완료!</h3>
        </div>
        
        <div class="final-score">
          <div class="score-circle">
            <div class="score-number">{{ quizScore }}</div>
            <div class="score-total">/ {{ totalQuestions }}</div>
          </div>
          <div class="score-percentage">
            {{ Math.round((quizScore / totalQuestions) * 100) }}%
          </div>
        </div>

        <div class="result-message">
          <div v-if="(quizScore / totalQuestions) >= 0.8" class="excellent">
            🌟 훌륭합니다! 금융 지식이 우수하네요!
          </div>
          <div v-else-if="(quizScore / totalQuestions) >= 0.6" class="good">
            👍 잘했습니다! 조금 더 공부하면 완벽해요!
          </div>
          <div v-else class="needs-improvement">
            📚 더 공부해보세요! 금융 지식을 늘려가는 중이에요!
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="restartQuiz" class="restart-button">
            🔄 다시 도전
          </button>
          <button @click="goToQuizList" class="list-button">
            📋 퀴즈 목록
          </button>
          <button @click="goToAcademy" class="home-button">
            🏠 아카데미로
          </button>
        </div>
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

// 상태 관리
const questions = ref([])
const currentQuestionIndex = ref(0)
const currentStep = ref('solving') // 'solving' | 'result'
const selectedChoice = ref(null)
const answerResult = ref(null)
const quizScore = ref(0)
const totalQuestions = ref(0)
const totalAnswered = ref(0)
const loading = ref(false)
const submitting = ref(false)
const showFinalResults = ref(false)

const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value] || null
})

// 선택지 라벨 생성 (A, B, C, D)
const getChoiceLabel = (choiceId) => {
  const currentQ = currentQuestion.value
  if (!currentQ) return ''
  
  const index = currentQ.choices.findIndex(choice => choice.id === choiceId)
  return String.fromCharCode(65 + index) // A, B, C, D
}

// 진행률 계산
const getProgress = () => {
  if (totalQuestions.value === 0) return 0
  return ((currentQuestionIndex.value + 1) / totalQuestions.value) * 100
}

// 마지막 문제인지 확인
const isLastQuestion = () => {
  return currentQuestionIndex.value >= questions.value.length - 1
}

// 선택지 선택
const selectChoice = (choice) => {
  selectedChoice.value = choice
}

// 문제 조회
const fetchQuestions = async () => {
  const difficulty = route.params.difficulty || 'youth'
  
  loading.value = true
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/finance-academy/questions/`, {
      params: { difficulty }
    })
    questions.value = response.data
    totalQuestions.value = response.data.length
    resetQuiz()
  } catch (error) {
    console.error('문제 조회 실패:', error)
    alert('퀴즈 문제를 불러오는데 실패했습니다.')
    router.push({ name: 'quiz-list' })
  } finally {
    loading.value = false
  }
}

// 1단계에서 "다음" 버튼 클릭 - 답안 제출하고 결과 표시
const submitAndShowResult = async () => {
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

// 2단계에서 "다음 문제" 버튼 클릭 - 다음 문제로 이동
const goToNextQuestion = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value += 1
    currentStep.value = 'solving'
    selectedChoice.value = null
    answerResult.value = null
  }
}

// 최종 결과 표시
const showFinalResult = () => {
  showFinalResults.value = true
}

// 최종 결과 모달 닫기
const closeFinalResult = () => {
  showFinalResults.value = false
}

// 퀴즈 다시 시작
const restartQuiz = () => {
  showFinalResults.value = false
  resetQuiz()
}

// 퀴즈 초기화
const resetQuiz = () => {
  currentQuestionIndex.value = 0
  currentStep.value = 'solving'
  selectedChoice.value = null
  answerResult.value = null
  quizScore.value = 0
  totalAnswered.value = 0
}

// 퀴즈 목록으로 이동
const goToQuizList = () => {
  router.push({ name: 'quiz-list' })
}

// 아카데미로 이동
const goToAcademy = () => {
  router.push({ name: 'financeAcademy' })
}

// 컴포넌트 초기화
onMounted(() => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push({ name: 'login' })
    return
  }
  
  fetchQuestions()
})
</script>

<style scoped>
.quiz-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.quiz-header {
  text-align: center;
  margin-bottom: 40px;
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 2px 20px rgba(0,0,0,0.1);
}

.quiz-header h2 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 1.8rem;
}

.quiz-progress {
  margin: 20px 0;
  font-size: 16px;
  color: #555;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background-color: #ecf0f1;
  border-radius: 5px;
  overflow: hidden;
  margin-top: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.5s ease;
}

.score-display {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
  margin-top: 15px;
}

.loading {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
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

.question-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.question-number {
  display: inline-block;
  background: #3498db;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  font-size: 14px;
}

.question-text {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 30px;
  line-height: 1.6;
  color: #2c3e50;
}

/* 1단계: 문제 풀이 스타일 */
.question-solving .choices {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.choice-button {
  display: flex;
  align-items: center;
  padding: 20px;
  border: 2px solid #ecf0f1;
  border-radius: 12px;
  background: white;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
}

.choice-button:hover {
  border-color: #3498db;
  background: #f8f9fa;
  transform: translateX(5px);
}

.choice-button.selected {
  border-color: #3498db;
  background: #e3f2fd;
  transform: translateX(5px);
}

.choice-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: #3498db;
  color: white;
  border-radius: 50%;
  font-weight: bold;
  margin-right: 15px;
  flex-shrink: 0;
}

.choice-button.selected .choice-number {
  background: #2980b9;
}

.choice-text {
  flex: 1;
}

.action-buttons {
  text-align: center;
}

.next-button {
  padding: 15px 40px;
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.next-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
}

.next-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 2단계: 결과 확인 스타일 */
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
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 25px;
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
  font-size: 28px;
}

.result-text {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
}

.answer-comparison {
  margin-bottom: 25px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.answer-item {
  padding: 15px;
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
  margin-bottom: 5px;
  font-size: 14px;
}

.answer-content {
  color: #333;
  font-size: 16px;
}

.explanation-section {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 30px;
  border-left: 4px solid #2196f3;
}

.explanation-section h4 {
  margin: 0 0 15px 0;
  color: #1976d2;
  font-size: 18px;
}

.explanation-content {
  color: #424242;
  font-size: 16px;
  line-height: 1.7;
}

.next-question-button, .finish-button {
  padding: 15px 40px;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.next-question-button:hover, .finish-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.final-result-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: white;
  padding: 40px;
  border-radius: 20px;
  text-align: center;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
  animation: slideIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(-50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header h3 {
  margin: 0 0 30px 0;
  font-size: 24px;
  color: #2c3e50;
}

.final-score {
  margin: 30px 0;
}

.score-circle {
  width: 120px;
  height: 120px;
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
  font-size: 32px;
  font-weight: bold;
}

.score-total {
  font-size: 16px;
  opacity: 0.9;
}

.score-percentage {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.result-message {
  margin: 30px 0;
  font-size: 18px;
  font-weight: 500;
}

.excellent { color: #27ae60; }
.good { color: #3498db; }
.needs-improvement { color: #f39c12; }

.modal-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
  flex-wrap: wrap;
}

.restart-button, .list-button, .home-button {
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.restart-button {
  background: #27ae60;
  color: white;
}

.list-button {
  background: #3498db;
  color: white;
}

.home-button {
  background: #95a5a6;
  color: white;
}

.restart-button:hover, .list-button:hover, .home-button:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

.no-questions {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 20px rgba(0,0,0,0.1);
}

.back-button {
  padding: 12px 30px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .quiz-container {
    padding: 15px;
  }
  
  .quiz-header {
    padding: 20px;
  }
  
  .question-card {
    padding: 25px;
  }
  
  .question-text {
    font-size: 18px;
  }
  
  .choice-button {
    padding: 15px;
    font-size: 15px;
  }
  
  .modal-content {
    padding: 30px 20px;
  }
  
  .modal-buttons {
    flex-direction: column;
  }
  
  .modal-buttons button {
    width: 100%;
  }
}
</style>