<template>
  <div class="certificate-card">
    <div class="certificate-header">
      <div class="certificate-badge">
        <i class="fas fa-certificate"></i>
      </div>
      <div class="certificate-info">
        <h3>{{ getDifficultyName(certificate.difficulty) }} 과정</h3>
        <p class="certificate-number">{{ certificate.certificate_number }}</p>
        <p class="grade">{{ certificate.grade }} 등급</p>
      </div>
    </div>
    
    <div class="certificate-details">
      <div class="detail-item">
        <span class="label">점수:</span>
        <span class="value">{{ certificate.score }}/10 ({{ certificate.score_percentage.toFixed(1) }}%)</span>
      </div>
      <div class="detail-item">
        <span class="label">발급일:</span>
        <span class="value">{{ formatDate(certificate.created_at) }}</span>
      </div>
    </div>
    
    <div class="certificate-actions">
      <button 
        @click="downloadCertificate" 
        class="download-btn"
        :disabled="downloading"
      >
        <i class="fas fa-download"></i>
        {{ downloading ? '다운로드 중...' : '수료증 다운로드' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api'

const props = defineProps({
  certificate: {
    type: Object,
    required: true
  }
})

const downloading = ref(false)

const difficultyNames = {
  youth: '청소년',
  adult_basic: '성인 기본',
  adult_advanced: '성인 심화'
}

const getDifficultyName = (difficulty) => {
  return difficultyNames[difficulty] || difficulty
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const downloadCertificate = async () => {
  try {
    downloading.value = true
    
    const response = await api.get(`/finance-academy/certificate/download/${props.certificate.id}/`, {
      responseType: 'blob'
    })
    
    // Blob을 다운로드 링크로 변환
    const blob = new Blob([response.data], { type: 'image/png' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${props.certificate.certificate_number}_수료증.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
  } catch (error) {
    console.error('수료증 다운로드 실패:', error)
    alert('수료증 다운로드에 실패했습니다.')
  } finally {
    downloading.value = false
  }
}
</script>

<style scoped>
.certificate-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  padding: 25px;
  color: white;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}

.certificate-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="30" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="2"/></svg>') repeat;
  opacity: 0.1;
}

.certificate-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.certificate-badge {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  backdrop-filter: blur(10px);
}

.certificate-badge i {
  font-size: 24px;
  color: #ffd700;
}

.certificate-info h3 {
  margin: 0 0 5px 0;
  font-size: 20px;
  font-weight: 600;
}

.certificate-number {
  margin: 0 0 5px 0;
  font-size: 14px;
  opacity: 0.9;
}

.grade {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #ffd700;
}

.certificate-details {
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.label {
  opacity: 0.8;
}

.value {
  font-weight: 500;
}

.certificate-actions {
  position: relative;
  z-index: 1;
}

.download-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 12px 24px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  width: 100%;
}

.download-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.download-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.download-btn i {
  margin-right: 8px;
}
</style>