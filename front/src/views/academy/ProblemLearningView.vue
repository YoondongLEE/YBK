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
          <li>1문제씩 결과와 해설을 바로 확인할 수 있습니다</li>
          <li>선택지를 고른 후 "다음" 버튼을 눌러 정답을 확인하세요</li>
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
        <!-- 1단계: 문제 풀이 (선택지 선택 후 다음 버튼) -->
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
              class="next-btn"
              @click="submitAndShowResult"
              :disabled="submitting"
            >
              {{ submitting ? '제출 중...' : '다음' }}
            </button>
          </div>
        </div>

        <!-- 2단계: 정답 확인 및 해설 -->
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
        </div>
        <div class="score-percentage">
          정답률: {{ Math.round((quizScore / questions.length) * 100) }}%
        </div>
        <div class="encouragement">
          <p v-if="quizScore === questions.length">🏆 완벽합니다! 모든 문제를 맞히셨네요!</p>
          <p v-else-if="quizScore >= questions.length * 0.8">🎉 훌륭합니다! 높은 점수를 획득하셨어요!</p>
          <p v-else-if="quizScore >= questions.length * 0.6">👍 좋습니다! 꾸준히 학습하시면 더 향상될 거예요!</p>
          <p v-else>💪 아직 부족하지만 포기하지 마세요! 다시 도전해보세요!</p>
        </div>
      </div>
      
      <div class="result-actions">
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

// 랜덤 10문제 가져오기
const fetchRandomQuestions = async () => {
  try {
    loading.value = true
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/finance-academy/quiz/${difficulty.value}/`)
    
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

// 1단계에서 "다음" 버튼 클릭 - 답안 제출하고 결과 표시
const submitAndShowResult = async () => {
  if (!selectedChoice.value || submitting.value) return
  
  submitting.value = true
  try {
    // 로그인 상태라면 토큰과 함께 요청, 아니라면 토큰 없이 요청
    const headers = {}
    if (authStore.isAuthenticated && authStore.token) {
      headers.Authorization = `Token ${authStore.token}`
    }
    
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/finance-academy/questions/${currentQuestion.value.id}/submit/`,
      { choice_id: selectedChoice.value.id },
      { headers }
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
    
    // 401 에러가 발생해도 로그아웃 상태에서는 괜찮음
    if (error.response && error.response.status === 401 && !authStore.isAuthenticated) {
      console.log('비로그인 상태에서 401 에러 발생 - 정상적인 상황')
      // 비로그인 상태에서는 간단한 클라이언트 사이드 정답 확인
      handleOfflineAnswerCheck()
    } else {
      alert('답안 제출 중 오류가 발생했습니다.')
    }
  } finally {
    submitting.value = false
  }
}

// 오프라인(비로그인) 상태에서의 정답 확인 처리
const handleOfflineAnswerCheck = () => {
  // 현재 문제에서 정답 찾기
  const correctChoice = currentQuestion.value.choices.find(choice => choice.is_correct)
  const isCorrect = selectedChoice.value.id === correctChoice.id
  
  // 결과 객체 생성
  answerResult.value = {
    is_correct: isCorrect,
    selected_choice: selectedChoice.value,
    correct_choice: correctChoice,
    explanation: currentQuestion.value.explanation || '해설이 없습니다.'
  }
  
  totalAnswered.value += 1
  
  // 정답이면 점수 증가
  if (isCorrect) {
    quizScore.value += 1
  }
  
  // 결과 확인 단계로 이동
  currentStep.value = 'result'
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
  border-top: 4px solid #3498db;
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
  padding: 40px 20px;
}

.quiz-intro h1 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 2.5rem;
}

.intro-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin: 0 auto;
}

.intro-card h2 {
  color: #34495e;
  margin-bottom: 20px;
}

.intro-card ul {
  text-align: left;
  margin: 20px 0;
  padding-left: 20px;
}

.intro-card li {
  margin: 10px 0;
  color: #7f8c8d;
  line-height: 1.6;
}

.start-btn {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  border: none;
  padding: 15px 40px;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 20px;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.3);
}

.quiz-container {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  margin-bottom: 20px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2980b9);
  transition: width 0.3s ease;
}

.question-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 12px;
}

.question-number {
  font-weight: 600;
  color: #2c3e50;
}

.difficulty-badge {
  background: #e74c3c;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.score-display {
  color: #27ae60;
  font-weight: 600;
}

.question-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 30px;
}

.question-text {
  color: #2c3e50;
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 30px;
  line-height: 1.6;
}

.choices {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.choice-btn {
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

.choice-btn:hover {
  border-color: #3498db;
  background: #f8f9fa;
  transform: translateX(5px);
}

.choice-btn.selected {
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
  font-weight: 600;
  margin-right: 15px;
  flex-shrink: 0;
}

.choice-text {
  flex: 1;
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.next-btn, .next-question-btn, .finish-btn {
  background: linear-gradient(135deg, #27ae60, #229954);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.next-btn:hover, .next-question-btn:hover, .finish-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(39, 174, 96, 0.3);
}

.next-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 결과 표시 스타일 */
.result-header {
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 25px;
}

.result-header.correct {
  background: linear-gradient(135deg, #d5f4e6, #c8e6c9);
  border: 2px solid #27ae60;
}

.result-header.incorrect {
  background: linear-gradient(135deg, #ffebee, #ffcdd2);
  border: 2px solid #e74c3c;
}

.result-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.result-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
}

.answer-comparison {
  margin-bottom: 25px;
}

.answer-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  border-left: 4px solid #3498db;
}

.answer-item.user-wrong {
  border-left-color: #e74c3c;
  background: #ffeaea;
}

.answer-item.correct-answer {
  border-left-color: #27ae60;
  background: #eaffea;
}

.answer-label {
  font-weight: 600;
  color: #7f8c8d;
  font-size: 12px;
  text-transform: uppercase;
  margin-bottom: 5px;
}

.answer-content {
  color: #2c3e50;
  font-size: 16px;
}

.explanation-section {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
}

.explanation-section h4 {
  color: #f39c12;
  margin: 0 0 15px 0;
  font-size: 1.1rem;
}

.explanation-content {
  color: #856404;
  line-height: 1.6;
  font-size: 15px;
}

/* 최종 결과 스타일 */
.results-container {
  text-align: center;
  padding: 40px 20px;
}

.score-card {
  background: white;
  border-radius: 20px;
  padding: 50px 30px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.score-card h1 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 2.5rem;
}

.score-circle {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #2980b9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 10px 30px rgba(52, 152, 219, 0.3);
}

.score-number {
  font-size: 3rem;
  font-weight: 700;
  color: white;
  line-height: 1;
}

.score-total {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
}

.score-percentage {
  font-size: 1.5rem;
  color: #27ae60;
  font-weight: 600;
  margin-bottom: 20px;
}

.encouragement {
  color: #7f8c8d;
  font-size: 1.1rem;
  line-height: 1.6;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.retry-btn, .back-btn {
  padding: 15px 30px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn {
  background: linear-gradient(135deg, #f39c12, #e67e22);
  color: white;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(243, 156, 18, 0.3);
}

.back-btn {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  color: white;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(149, 165, 166, 0.3);
}

@media (max-width: 768px) {
  .problem-learning-container {
    padding: 10px;
  }
  
  .question-info {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .result-actions {
    flex-direction: column;
  }
  
  .quiz-intro h1 {
    font-size: 2rem;
  }
  
  .score-circle {
    width: 120px;
    height: 120px;
  }
  
  .score-number {
    font-size: 2.5rem;
  }
}
</style>