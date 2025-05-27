<template>
  <div class="assessment-container">
    <!-- 평가 시작 전 -->
    <div v-if="!assessmentStarted && !assessmentResult" class="assessment-intro">
      <h2>{{ getDifficultyName(difficulty) }} 평가</h2>
      <div class="intro-content">
        <div class="assessment-info">
          <h3>평가 안내</h3>
          <ul>
            <li>총 10문제가 출제됩니다</li>
            <li>제한 시간은 없으며, 신중하게 답변해주세요</li>
            <li>6문제 이상 맞추면 합격입니다</li>
            <li>모든 문제를 푼 후 한 번에 채점됩니다</li>
          </ul>
        </div>
        
        <div class="grade-info">
          <h3>등급 기준</h3>
          <div class="grade-table">
            <div class="grade-row">
              <span class="score">90점 이상</span>
              <span class="grade">{{ getGradeName(difficulty, 90) }}</span>
            </div>
            <div class="grade-row">
              <span class="score">75점 이상</span>
              <span class="grade">{{ getGradeName(difficulty, 75) }}</span>
            </div>
            <div class="grade-row">
              <span class="score">60점 이상</span>
              <span class="grade">{{ getGradeName(difficulty, 60) }}</span>
            </div>
          </div>
        </div>
        
        <button @click="startAssessment" class="start-btn" :disabled="loading">
          <span v-if="loading">준비 중...</span>
          <span v-else>평가 시작</span>
        </button>
      </div>
    </div>

    <!-- 평가 진행 중 -->
    <div v-else-if="assessmentStarted && !assessmentResult" class="assessment-progress">
      <div class="progress-header">
        <h2>{{ getDifficultyName(difficulty) }} 평가</h2>
        <div class="progress-info">
          <span>{{ currentQuestionIndex + 1 }} / {{ questions.length }}</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: getProgress() + '%' }"></div>
          </div>
        </div>
      </div>

      <div v-if="getCurrentQuestion()" class="question-container">
        <div class="question-number">문제 {{ currentQuestionIndex + 1 }}</div>
        <div class="question-text">{{ getCurrentQuestion().text }}</div>
        
        <div class="choices">
          <label 
            v-for="choice in getCurrentQuestion().choices" 
            :key="choice.id"
            class="choice-label"
            :class="{ 'selected': userAnswers[getCurrentQuestion().id] === choice.id }"
          >
            <input 
              type="radio" 
              :name="'question-' + getCurrentQuestion().id"
              :value="choice.id"
              @change="saveAnswer(getCurrentQuestion().id, choice.id)"
            />
            <span class="choice-text">{{ choice.text }}</span>
          </label>
        </div>

        <div class="navigation-buttons">
          <button 
            @click="previousQuestion" 
            :disabled="currentQuestionIndex === 0"
            class="nav-btn prev-btn"
          >
            이전 문제
          </button>
          
          <button 
            v-if="currentQuestionIndex < questions.length - 1"
            @click="nextQuestion" 
            class="nav-btn next-btn"
          >
            다음 문제
          </button>
          
          <button 
            v-else
            @click="submitAssessment" 
            :disabled="!areAllQuestionsAnswered"
            class="submit-btn"
          >
            제출하기
          </button>
        </div>
      </div>
    </div>

    <!-- 평가 결과 -->
    <div v-else-if="assessmentResult" class="assessment-result">
      <div class="result-header">
        <h2>평가 결과</h2>
        <div class="result-score">
          <div class="score-circle" :class="{ 'passed': assessmentResult.passed }">
            <span class="score-text">{{ assessmentResult.score }}/10</span>
            <span class="grade-text">{{ assessmentResult.grade }}</span>
          </div>
        </div>
      </div>

      <div class="result-message">
        <div v-if="assessmentResult.passed" class="success-message">
          <h3>🎉 합격을 축하합니다!</h3>
          <p>{{ assessmentResult.score_percentage }}점으로 {{ assessmentResult.grade }} 등급을 획득하셨습니다.</p>
        </div>
        <div v-else class="fail-message">
          <h3>😊 조금 더 학습해보세요</h3>
          <p>{{ assessmentResult.score_percentage }}점입니다. 개념 학습을 통해 실력을 키워보세요!</p>
        </div>
      </div>

      <div class="result-actions">
        <button 
          v-if="!assessmentResult.passed"
          @click="goToConceptStudy" 
          class="study-btn"
        >
          개념 학습하러 가기
        </button>
        <button @click="goToFinanceAcademy" class="back-btn">
          금융 아카데미로 돌아가기
        </button>
      </div>

      <!-- 상세 결과 (선택적으로 표시) -->
      <div v-if="showDetailResults" class="detail-results">
        <h3>상세 결과</h3>
        <div 
          v-for="(result, index) in assessmentResult.question_results" 
          :key="index"
          class="question-result"
          :class="{ 'correct': result.is_correct, 'incorrect': !result.is_correct }"
        >
          <div class="question-result-header">
            <span class="question-number">문제 {{ index + 1 }}</span>
            <span class="result-icon">{{ result.is_correct ? '✓' : '✗' }}</span>
          </div>
          <div class="question-result-content">
            <p class="question">{{ result.question }}</p>
            <p class="answer-info">
              <span class="label">내 답안:</span> 
              <span :class="{ 'correct': result.is_correct, 'incorrect': !result.is_correct }">
                {{ result.user_answer }}
              </span>
            </p>
            <p v-if="!result.is_correct" class="correct-answer">
              <span class="label">정답:</span> {{ result.correct_answer }}
            </p>
            <p class="explanation">{{ result.explanation }}</p>
          </div>
        </div>
      </div>
      
      <button @click="showDetailResults = !showDetailResults" class="toggle-detail-btn">
        {{ showDetailResults ? '상세 결과 숨기기' : '상세 결과 보기' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssessmentStore } from '@/stores/assessment'
import { useAlertStore } from '@/stores/alert'

const route = useRoute()
const router = useRouter()
const assessmentStore = useAssessmentStore()
const alertStore = useAlertStore()

const difficulty = ref(route.params.difficulty)
const assessmentStarted = ref(false)
const showDetailResults = ref(false)

// Computed
const questions = computed(() => assessmentStore.questions)
const currentQuestionIndex = computed(() => assessmentStore.currentQuestionIndex)
const userAnswers = computed(() => assessmentStore.userAnswers)
const loading = computed(() => assessmentStore.loading)
const assessmentResult = computed(() => assessmentStore.assessmentResult)

// Methods
const startAssessment = async () => {
  try {
    await assessmentStore.startAssessment(difficulty.value)
    assessmentStarted.value = true
  } catch (error) {
    alertStore.showError('오류', '평가를 시작할 수 없습니다.')
  }
}

const saveAnswer = (questionId, choiceId) => {
  assessmentStore.saveAnswer(questionId, choiceId)
}

const nextQuestion = () => {
  assessmentStore.nextQuestion()
}

const previousQuestion = () => {
  assessmentStore.previousQuestion()
}

const submitAssessment = async () => {
  if (!assessmentStore.areAllQuestionsAnswered()) {
    alertStore.showWarning('알림', '모든 문제에 답변해주세요.')
    return
  }

  try {
    await assessmentStore.submitAssessment(difficulty.value)
    alertStore.showSuccess('완료', '평가가 제출되었습니다.')
  } catch (error) {
    alertStore.showError('오류', '평가 제출 중 오류가 발생했습니다.')
  }
}

const getCurrentQuestion = () => {
  return assessmentStore.getCurrentQuestion()
}

const getProgress = () => {
  return assessmentStore.getProgress()
}

const areAllQuestionsAnswered = computed(() => {
  return assessmentStore.areAllQuestionsAnswered()
})

const getDifficultyName = (diff) => {
  const names = {
    'adult_advanced': '성인 심화',
    'adult_basic': '성인 기본',
    'youth': '청소년'
  }
  return names[diff] || diff
}

const getGradeName = (diff, score) => {
  if (score >= 90) {
    return diff === 'adult_advanced' ? 'Advanced High (AH)' : 
           diff === 'adult_basic' ? 'Intermediate High (IH)' : 'Novel High (NH)'
  } else if (score >= 75) {
    return diff === 'adult_advanced' ? 'Advanced Mid (AM)' : 
           diff === 'adult_basic' ? 'Intermediate Mid (IM)' : 'Novel Mid (NM)'
  } else if (score >= 60) {
    return diff === 'adult_advanced' ? 'Advanced Low (AL)' : 
           diff === 'adult_basic' ? 'Intermediate Low (IL)' : 'Novel Low (NL)'
  }
  return '불합격'
}

const goToConceptStudy = () => {
  router.push(`/finance-academy/concept-study/${difficulty.value}`)
}

const goToFinanceAcademy = () => {
  router.push('/finance-academy')
}

onMounted(() => {
  assessmentStore.resetAssessment()
})
</script>

<style scoped>
.assessment-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.assessment-intro {
  text-align: center;
}

.intro-content {
  display: grid;
  gap: 30px;
  margin: 30px 0;
}

.assessment-info, .grade-info {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.assessment-info ul {
  text-align: left;
  max-width: 400px;
  margin: 0 auto;
}

.assessment-info li {
  margin: 8px 0;
}

.grade-table {
  display: grid;
  gap: 10px;
}

.grade-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #ddd;
}

.start-btn {
  background: #4a90e2;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.start-btn:hover:not(:disabled) {
  background: #357abd;
}

.start-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.progress-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.progress-bar {
  width: 200px;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4a90e2;
  transition: width 0.3s;
}

.question-container {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.question-number {
  color: #4a90e2;
  font-weight: bold;
  margin-bottom: 10px;
}

.question-text {
  font-size: 18px;
  margin-bottom: 30px;
  line-height: 1.6;
}

.choices {
  display: grid;
  gap: 15px;
  margin-bottom: 30px;
}

.choice-label {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.choice-label:hover {
  border-color: #4a90e2;
  background: #f9faff;
}

.choice-label.selected {
  border-color: #4a90e2;
  background: #f0f7ff;
}

.choice-label input {
  margin-right: 12px;
}

.choice-text {
  flex: 1;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

.nav-btn, .submit-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.prev-btn {
  background: #f8f9fa;
  color: #666;
}

.prev-btn:hover:not(:disabled) {
  background: #e9ecef;
}

.prev-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.next-btn {
  background: #4a90e2;
  color: white;
}

.next-btn:hover {
  background: #357abd;
}

.submit-btn {
  background: #28a745;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: #218838;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.assessment-result {
  text-align: center;
}

.result-header {
  margin-bottom: 30px;
}

.score-circle {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 8px solid #dc3545;
  margin: 20px 0;
}

.score-circle.passed {
  border-color: #28a745;
}

.score-text {
  font-size: 24px;
  font-weight: bold;
}

.grade-text {
  font-size: 16px;
  margin-top: 5px;
}

.success-message {
  color: #28a745;
}

.fail-message {
  color: #dc3545;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin: 30px 0;
}

.study-btn {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.study-btn:hover {
  background: #138496;
}

.back-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.back-btn:hover {
  background: #5a6268;
}

.detail-results {
  margin-top: 40px;
  text-align: left;
}

.question-result {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 15px;
  overflow: hidden;
}

.question-result.correct {
  border-left: 4px solid #28a745;
}

.question-result.incorrect {
  border-left: 4px solid #dc3545;
}

.question-result-header {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  background: #f8f9fa;
}

.question-result-content {
  padding: 15px;
}

.question-result-content .question {
  font-weight: bold;
  margin-bottom: 10px;
}

.answer-info, .correct-answer {
  margin: 8px 0;
}

.label {
  font-weight: bold;
}

.correct {
  color: #28a745;
}

.incorrect {
  color: #dc3545;
}

.explanation {
  margin-top: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  font-style: italic;
}

.toggle-detail-btn {
  background: #e9ecef;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 20px;
  transition: background 0.3s;
}

.toggle-detail-btn:hover {
  background: #dee2e6;
}
</style>