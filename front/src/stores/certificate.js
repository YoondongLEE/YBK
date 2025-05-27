import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/api'

export const useCertificateStore = defineStore('certificate', () => {
  const certificates = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 사용자의 수료증 목록 조회
  const fetchUserCertificates = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/finance-academy/certificates/')
      certificates.value = response.data
      return response.data
    } catch (err) {
      error.value = '수료증 목록을 불러오는 중 오류가 발생했습니다.'
      console.error('수료증 목록 조회 실패:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 평가 결과로 수료증 생성
  const generateCertificate = async (assessmentId) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/finance-academy/certificate/generate/${assessmentId}/`)
      
      // 새로 생성된 수료증을 목록에 추가
      await fetchUserCertificates()
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || '수료증 생성 중 오류가 발생했습니다.'
      console.error('수료증 생성 실패:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 수료증 다운로드
  const downloadCertificate = async (certificateId) => {
    try {
      const response = await api.get(`/finance-academy/certificate/download/${certificateId}/`, {
        responseType: 'blob'
      })
      
      return response.data
    } catch (err) {
      error.value = '수료증 다운로드 중 오류가 발생했습니다.'
      console.error('수료증 다운로드 실패:', err)
      throw err
    }
  }

  // 특정 난이도의 수료증 확인
  const hasCertificate = (difficulty) => {
    return certificates.value.some(cert => cert.difficulty === difficulty)
  }

  // 특정 난이도의 최고 등급 수료증 가져오기
  const getBestCertificate = (difficulty) => {
    const diffCerts = certificates.value.filter(cert => cert.difficulty === difficulty)
    if (diffCerts.length === 0) return null
    
    // 등급 우선순위 (숫자가 높을수록 높은 등급)
    const gradePriority = {
      'AH': 9, 'AM': 8, 'AL': 7,
      'IH': 6, 'IM': 5, 'IL': 4,
      'NH': 3, 'NM': 2, 'NL': 1
    }
    
    return diffCerts.reduce((best, current) => {
      const bestPriority = gradePriority[best.grade] || 0
      const currentPriority = gradePriority[current.grade] || 0
      return currentPriority > bestPriority ? current : best
    })
  }

  // 오류 초기화
  const clearError = () => {
    error.value = null
  }

  return {
    // 상태
    certificates,
    loading,
    error,
    
    // 액션
    fetchUserCertificates,
    generateCertificate,
    downloadCertificate,
    hasCertificate,
    getBestCertificate,
    clearError
  }
})