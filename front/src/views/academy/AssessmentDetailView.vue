<template>
  <div class="assessment-detail-container">
    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>평가 결과를 불러오는 중...</p>
    </div>

    <!-- 평가 상세 내용 -->
    <div v-else-if="assessmentDetail" class="assessment-detail">
      <!-- 헤더 -->
      <div class="detail-header">
        <button @click="goBack" class="back-btn">
          <i class="bi bi-arrow-left"></i> 돌아가기
        </button>
        <h1>평가 결과 상세</h1>
      </div>

      <!-- 평가 요약 -->
      <div class="assessment-summary">
        <div class="summary-item">
          <div class="summary-label">난이도</div>
          <div class="summary-value difficulty" :class="assessmentDetail.difficulty">
            {{ getDifficultyName(assessmentDetail.difficulty) }}
          </div>
        </div>
        
        <div class="summary-item">
          <div class="summary-label">점수</div>
          <div class="summary-value score">
            {{ assessmentDetail.score }}/10 ({{ assessmentDetail.score_percentage }}%)
          </div>
        </div>
        
        <div class="summary-item">
          <div class="summary-label">등급</div>
          <div class="summary-value grade" :class="{ 'passed': assessmentDetail.passed }">
            {{ assessmentDetail.grade }}
          </div>
        </div>
        
        <div class="summary-item">
          <div class="summary-label">결과</div>
          <div class="summary-value result" :class="{ 'passed': assessmentDetail.passed }">
            {{ assessmentDetail.passed ? '합격' : '불합격' }}
          </div>
        </div>
        
        <div class="summary-item">
          <div class="summary-label">응시일</div>
          <div class="summary-value date">
            {{ formatDate(assessmentDetail.created_at) }}
          </div>
        </div>
      </div>

      <!-- 수료증 섹션 (합격한 경우에만 표시) -->
      <div v-if="assessmentDetail.passed" class="certificate-section">
        <div v-if="existingCertificate" class="certificate-exists">
          <div class="certificate-card">
            <i class="bi bi-award-fill"></i>
            <div class="certificate-info">
              <h3>수료증이 발급되었습니다!</h3>
              <p>발급번호: {{ existingCertificate.certificate_number }}</p>
              <p>등급: {{ existingCertificate.grade }}</p>
            </div>
            <button @click="goToCertificates" class="view-certificate-btn">
              <i class="bi bi-eye"></i>
              수료증 보기
            </button>
          </div>
        </div>
        <div v-else class="certificate-generate">
          <div class="certificate-prompt">
            <i class="bi bi-award"></i>
            <h3>수료증을 발급받으세요!</h3>
            <p>합격하신 것을 축하드립니다. 수료증을 발급받을 수 있습니다.</p>
            <button 
              @click="generateCertificate" 
              class="generate-certificate-btn"
              :disabled="generatingCertificate"
            >
              <i class="bi bi-award-fill"></i>
              {{ generatingCertificate ? '수료증 생성 중...' : '수료증 발급받기' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 문제별 상세 결과 -->
      <div class="questions-detail">
        <h2>문제별 상세 결과</h2>
        
        <div class="questions-list">
          <div 
            v-for="(question, index) in assessmentDetail.questions_data" 
            :key="question.question_id"
            class="question-item"
            :class="{ 'correct': question.is_correct, 'incorrect': !question.is_correct }"
          >
            <div class="question-header">
              <div class="question-number">문제 {{ index + 1 }}</div>
              <div class="question-result" :class="{ 'correct': question.is_correct }">
                <i :class="question.is_correct ? 'bi bi-check-circle-fill' : 'bi bi-x-circle-fill'"></i>
                {{ question.is_correct ? '정답' : '오답' }}
              </div>
            </div>
            
            <div class="question-content">
              <div class="question-text">{{ question.question }}</div>
              
              <div class="answer-section">
                <div class="user-answer">
                  <span class="answer-label">내 답변:</span>
                  <span class="answer-text" :class="{ 'correct': question.is_correct, 'incorrect': !question.is_correct }">
                    {{ question.user_answer }}
                  </span>
                </div>
                
                <div v-if="!question.is_correct" class="correct-answer">
                  <span class="answer-label">정답:</span>
                  <span class="answer-text correct">{{ question.correct_answer }}</span>
                </div>
              </div>
              
              <div class="explanation">
                <div class="explanation-label">
                  <i class="bi bi-lightbulb"></i> 해설
                </div>
                <div class="explanation-text">{{ question.explanation }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="action-buttons">
        <button @click="goToAssessment" class="retry-btn">
          다시 응시하기
        </button>
        <button @click="goToMyPage" class="mypage-btn">
          마이페이지로
        </button>
      </div>
    </div>

    <!-- 오류 상태 -->
    <div v-else class="error-container">
      <div class="error-content">
        <i class="bi bi-exclamation-triangle"></i>
        <h3>평가 결과를 불러올 수 없습니다</h3>
        <p>평가 결과가 존재하지 않거나 접근 권한이 없습니다.</p>
        <button @click="goBack" class="back-btn">돌아가기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssessmentStore } from '../../stores/assessment'
import { useCertificateStore } from '../../stores/certificate'

const route = useRoute()
const router = useRouter()
const assessmentStore = useAssessmentStore()
const certificateStore = useCertificateStore()

const loading = ref(false)
const assessmentDetail = ref(null)
const generatingCertificate = ref(false)

const getDifficultyName = (difficulty) => {
  const names = {
    'youth': '청소년',
    'adult_basic': '성인 기본',
    'adult_advanced': '성인 심화'
  }
  return names[difficulty] || difficulty
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 기존 수료증이 있는지 확인
const existingCertificate = computed(() => {
  if (!assessmentDetail.value) return null
  return certificateStore.getBestCertificate(assessmentDetail.value.difficulty)
})

const fetchDetail = async () => {
  try {
    loading.value = true
    const assessmentId = route.params.id
    const detail = await assessmentStore.fetchAssessmentDetail(assessmentId)
    assessmentDetail.value = detail
    
    // 합격한 경우 수료증 목록도 조회
    if (detail.passed) {
      await certificateStore.fetchUserCertificates()
    }
  } catch (error) {
    console.error('평가 상세 조회 실패:', error)
  } finally {
    loading.value = false
  }
}

// 수료증 생성
const generateCertificate = async () => {
  try {
    generatingCertificate.value = true
    await certificateStore.generateCertificate(assessmentDetail.value.id)
    
    // 성공 알림
    alert('수료증이 성공적으로 발급되었습니다!')
    
    // 수료증 페이지로 이동
    router.push({ name: 'certificates' })
  } catch (err) {
    console.error('수료증 생성 실패:', err)
    alert('수료증 발급에 실패했습니다. 다시 시도해주세요.')
  } finally {
    generatingCertificate.value = false
  }
}

// 수료증 페이지로 이동
const goToCertificates = () => {
  router.push({ name: 'certificates' })
}

const goBack = () => {
  router.go(-1)
}

const goToMyPage = () => {
  router.push({ name: 'mypage' })
}

const goToAssessment = () => {
  if (assessmentDetail.value) {
    router.push({ 
      name: 'assessment', 
      params: { difficulty: assessmentDetail.value.difficulty } 
    })
  }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.assessment-detail-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.back-btn {
  background: none;
  border: 2px solid #667eea;
  color: #667eea;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background-color: #667eea;
  color: white;
}

.detail-header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 28px;
  font-weight: 700;
}

.assessment-summary {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.summary-item {
  text-align: center;
}

.summary-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 8px;
  font-weight: 600;
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  padding: 10px;
  border-radius: 8px;
}

.summary-value.difficulty.youth {
  background-color: #e3f2fd;
  color: #1976d2;
}

.summary-value.difficulty.adult_basic {
  background-color: #fff3e0;
  color: #f57c00;
}

.summary-value.difficulty.adult_advanced {
  background-color: #ffebee;
  color: #d32f2f;
}

.summary-value.score {
  background-color: #f8f9fa;
  color: #2c3e50;
}

.summary-value.grade.passed,
.summary-value.result.passed {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.summary-value.grade:not(.passed),
.summary-value.result:not(.passed) {
  background-color: #ffebee;
  color: #d32f2f;
}

.summary-value.date {
  background-color: #f8f9fa;
  color: #2c3e50;
  font-size: 16px;
}

/* 수료증 섹션 스타일 */
.certificate-section {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.certificate-exists .certificate-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 25px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.certificate-card i {
  font-size: 3rem;
  color: #ffd700;
}

.certificate-info {
  flex: 1;
}

.certificate-info h3 {
  margin: 0 0 10px 0;
  font-size: 1.3rem;
}

.certificate-info p {
  margin: 5px 0;
  opacity: 0.9;
}

.view-certificate-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-certificate-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.certificate-generate .certificate-prompt {
  text-align: center;
  padding: 20px;
}

.certificate-prompt i {
  font-size: 4rem;
  color: #ffd700;
  margin-bottom: 20px;
}

.certificate-prompt h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.certificate-prompt p {
  color: #666;
  margin-bottom: 25px;
}

.generate-certificate-btn {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #333;
  border: none;
  padding: 15px 30px;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 5px 20px rgba(255, 215, 0, 0.3);
}

.generate-certificate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(255, 215, 0, 0.4);
}

.generate-certificate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.questions-detail {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.questions-detail h2 {
  color: #2c3e50;
  margin-bottom: 25px;
  font-size: 22px;
  font-weight: 700;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 10px;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.question-item {
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 25px;
  transition: all 0.3s ease;
}

.question-item.correct {
  border-color: #28a745;
  background-color: #f8fff9;
}

.question-item.incorrect {
  border-color: #dc3545;
  background-color: #fff8f8;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.question-number {
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
}

.question-result {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 20px;
}

.question-result.correct {
  background-color: #d4edda;
  color: #155724;
}

.question-result:not(.correct) {
  background-color: #f8d7da;
  color: #721c24;
}

.question-text {
  font-size: 16px;
  line-height: 1.6;
  color: #2c3e50;
  margin-bottom: 20px;
  font-weight: 500;
}

.answer-section {
  margin-bottom: 20px;
}

.user-answer,
.correct-answer {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 12px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.answer-label {
  font-weight: 600;
  color: #495057;
  min-width: 80px;
}

.answer-text {
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 500;
}

.answer-text.correct {
  background-color: #d4edda;
  color: #155724;
}

.answer-text.incorrect {
  background-color: #f8d7da;
  color: #721c24;
}

.explanation {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #667eea;
}

.explanation-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 10px;
}

.explanation-text {
  color: #6c757d;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.retry-btn,
.mypage-btn {
  padding: 12px 30px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.mypage-btn {
  background: transparent;
  border: 2px solid #667eea;
  color: #667eea;
}

.mypage-btn:hover {
  background-color: #667eea;
  color: white;
}

.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.error-content {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.error-content i {
  font-size: 48px;
  color: #e74c3c;
  margin-bottom: 20px;
}

.error-content h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.error-content p {
  color: #7f8c8d;
  margin-bottom: 25px;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .assessment-summary {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .question-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 15px;
  }
  
  .retry-btn,
  .mypage-btn {
    width: 100%;
  }
  
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .certificate-card {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
  
  .view-certificate-btn {
    align-self: center;
  }
}
</style>