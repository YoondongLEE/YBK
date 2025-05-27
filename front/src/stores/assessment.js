import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

export const useAssessmentStore = defineStore('assessment', () => {
  const questions = ref([])
  const currentQuestionIndex = ref(0)
  const userAnswers = ref({})
  const loading = ref(false)
  const assessmentResult = ref(null)
  const assessmentHistory = ref([])
  const assessmentDetail = ref(null) // 추가

  // API 인스턴스 생성
  const api = axios.create({
    baseURL: `${API_URL}/api/finance-academy`,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
  })

  // 요청 인터셉터 - 토큰 추가
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Token ${token}`
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  // 평가 시작
  const startAssessment = async (difficulty) => {
    loading.value = true
    try {
      const response = await api.post('/assessment/start/', { difficulty })
      questions.value = response.data.questions
      currentQuestionIndex.value = 0
      userAnswers.value = {}
      assessmentResult.value = null
      return response.data
    } catch (error) {
      console.error('평가 시작 실패:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 답안 저장
  const saveAnswer = (questionId, choiceId) => {
    userAnswers.value[questionId] = choiceId
  }

  // 평가 제출
  const submitAssessment = async (difficulty) => {
    loading.value = true
    try {
      const response = await api.post('/assessment/submit/', {
        difficulty,
        answers: userAnswers.value
      })
      assessmentResult.value = response.data
      return response.data
    } catch (error) {
      console.error('평가 제출 실패:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 평가 이력 조회
  const fetchAssessmentHistory = async () => {
    try {
      const response = await api.get('/assessment/history/')
      assessmentHistory.value = response.data
      return response.data
    } catch (error) {
      console.error('평가 이력 조회 실패:', error)
      throw error
    }
  }

  // 평가 상세 결과 조회 (수정)
  const fetchAssessmentDetail = async (assessmentId) => {
    loading.value = true
    try {
      const response = await api.get(`/assessment/${assessmentId}/`)
      assessmentDetail.value = response.data
      return response.data
    } catch (error) {
      console.error('평가 상세 조회 실패:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 평가 초기화 (수정)
  const resetAssessment = () => {
    questions.value = []
    currentQuestionIndex.value = 0
    userAnswers.value = {}
    assessmentResult.value = null
    assessmentDetail.value = null
  }

  // 현재 문제 가져오기
  const getCurrentQuestion = () => {
    return questions.value[currentQuestionIndex.value] || null
  }

  // 진행률 계산
  const getProgress = () => {
    if (questions.value.length === 0) return 0
    return ((currentQuestionIndex.value + 1) / questions.value.length) * 100
  }

  // 모든 문제가 답변되었는지 확인
  const areAllQuestionsAnswered = () => {
    return questions.value.every(q => userAnswers.value[q.id])
  }

  // 다음 문제로 이동
  const nextQuestion = () => {
    if (currentQuestionIndex.value < questions.value.length - 1) {
      currentQuestionIndex.value++
    }
  }

  // 이전 문제로 이동
  const previousQuestion = () => {
    if (currentQuestionIndex.value > 0) {
      currentQuestionIndex.value--
    }
  }

  return {
    // State
    questions,
    currentQuestionIndex,
    userAnswers,
    loading,
    assessmentResult,
    assessmentHistory,
    assessmentDetail, // 추가
    
    // Actions
    startAssessment,
    saveAnswer,
    submitAssessment,
    fetchAssessmentHistory,
    fetchAssessmentDetail,
    resetAssessment,
    
    // Getters
    getCurrentQuestion,
    getProgress,
    areAllQuestionsAnswered,
    
    // Navigation
    nextQuestion,
    previousQuestion
  }
})