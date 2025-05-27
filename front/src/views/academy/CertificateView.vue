<template>
  <div class="certificate-container">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <button @click="goBack" class="back-btn">
        <i class="fas fa-arrow-left"></i> 돌아가기
      </button>
      <h1>
        <i class="fas fa-certificate"></i>
        나의 수료증
      </h1>
      <p>취득한 수료증을 확인하고 다운로드할 수 있습니다.</p>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>수료증 목록을 불러오는 중...</p>
    </div>

    <!-- 수료증 목록 -->
    <div v-else-if="certificates.length > 0" class="certificates-section">
      <div class="certificates-grid">
        <CertificateCard 
          v-for="certificate in certificates" 
          :key="certificate.id" 
          :certificate="certificate"
        />
      </div>
    </div>

    <!-- 수료증이 없는 경우 -->
    <div v-else class="empty-state">
      <div class="empty-content">
        <div class="empty-icon">
          <i class="fas fa-certificate"></i>
        </div>
        <h3>아직 취득한 수료증이 없습니다</h3>
        <p>평가에 합격하면 수료증을 자동으로 발급받을 수 있습니다.</p>
        <div class="action-buttons">
          <button @click="goToAssessment" class="primary-btn">
            <i class="fas fa-clipboard-check"></i>
            평가 응시하기
          </button>
          <button @click="goToConceptStudy" class="secondary-btn">
            <i class="fas fa-book"></i>
            개념 학습하기
          </button>
        </div>
      </div>
    </div>

    <!-- 오류 상태 -->
    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      {{ error }}
      <button @click="fetchCertificates" class="retry-btn">다시 시도</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCertificateStore } from '@/stores/certificate'
import CertificateCard from '@/components/CertificateCard.vue'

const router = useRouter()
const certificateStore = useCertificateStore()

const certificates = ref([])
const loading = ref(false)
const error = ref(null)

// 수료증 목록 조회
const fetchCertificates = async () => {
  try {
    loading.value = true
    error.value = null
    certificates.value = await certificateStore.fetchUserCertificates()
  } catch (err) {
    error.value = '수료증 목록을 불러오는 중 오류가 발생했습니다.'
    console.error('수료증 조회 실패:', err)
  } finally {
    loading.value = false
  }
}

// 뒤로가기
const goBack = () => {
  router.push('/finance-academy')
}

// 평가 응시하기
const goToAssessment = () => {
  router.push('/finance-academy')
}

// 개념 학습하기
const goToConceptStudy = () => {
  router.push('/finance-academy')
}

onMounted(() => {
  fetchCertificates()
})
</script>

<style scoped>
.certificate-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Noto Sans KR', sans-serif;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.back-btn {
  position: absolute;
  left: 0;
  top: 0;
  background: none;
  border: none;
  color: #666;
  font-size: 16px;
  cursor: pointer;
  padding: 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background-color: #f8f9fa;
  color: #333;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.page-header h1 i {
  color: #ffd700;
}

.page-header p {
  color: #666;
  font-size: 1.1rem;
  margin: 0;
}

.loading-container {
  text-align: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
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

.certificates-section {
  margin-top: 20px;
}

.certificates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 25px;
  margin-top: 20px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  padding: 40px;
}

.empty-content {
  text-align: center;
  max-width: 500px;
}

.empty-icon {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 30px;
}

.empty-icon i {
  font-size: 48px;
  color: white;
}

.empty-content h3 {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 15px;
}

.empty-content p {
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 30px;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.primary-btn, .secondary-btn {
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  border: none;
}

.primary-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.secondary-btn {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.secondary-btn:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 15px 20px;
  border-radius: 8px;
  margin: 20px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: space-between;
}

.retry-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  background: #c82333;
}

@media (max-width: 768px) {
  .certificates-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .primary-btn, .secondary-btn {
    width: 200px;
    justify-content: center;
  }
}
</style>