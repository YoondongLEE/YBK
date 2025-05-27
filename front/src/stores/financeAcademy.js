import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/api'

export const useFinanceAcademyStore = defineStore('financeAcademy', () => {
  // 상태
  const questions = ref([])
  const categories = ref([])
  const currentQuestionIndex = ref(0)
  const answerResult = ref(null)
  const showResult = ref(false)
  const quizScore = ref(0)
  const totalQuestions = ref(0)
  const loading = ref(false)

  // 문제 목록 조회
  const fetchQuestions = async (difficulty = 'youth') => {
    loading.value = true
    try {
      const response = await api.get('/finance-academy/questions/', {
        params: { difficulty }
      })
      questions.value = response.data
      totalQuestions.value = response.data.length
      return response.data
    } catch (error) {
      console.error('문제 조회 실패:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 개별 문제 조회
  const fetchQuestion = async (questionId) => {
    loading.value = true
    try {
      const response = await api.get(`/finance-academy/questions/${questionId}/`)
      return response.data
    } catch (error) {
      console.error('문제 조회 실패:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 답안 제출
  const submitAnswer = async (questionId, choiceId) => {
    try {
      const response = await api.post(`/finance-academy/questions/${questionId}/submit/`, {
        choice_id: choiceId
      })
      
      answerResult.value = response.data
      showResult.value = true
      
      // 정답이면 점수 증가
      if (response.data.is_correct) {
        quizScore.value += 1
      }
      
      return response.data
    } catch (error) {
      console.error('답안 제출 실패:', error)
      throw error
    }
  }

  // 카테고리 목록 조회
  const fetchCategories = async () => {
    try {
      const response = await api.get('/finance-academy/categories/')
      categories.value = response.data
      return response.data
    } catch (error) {
      console.error('카테고리 조회 실패:', error)
      throw error
    }
  }

  // 다음 문제로 이동
  const nextQuestion = () => {
    if (currentQuestionIndex.value < questions.value.length - 1) {
      currentQuestionIndex.value += 1
      answerResult.value = null
      showResult.value = false
    }
  }

  // 이전 문제로 이동
  const previousQuestion = () => {
    if (currentQuestionIndex.value > 0) {
      currentQuestionIndex.value -= 1
      answerResult.value = null
      showResult.value = false
    }
  }

  // 퀴즈 초기화
  const resetQuiz = () => {
    currentQuestionIndex.value = 0
    answerResult.value = null
    showResult.value = false
    quizScore.value = 0
  }

  // 현재 문제 가져오기
  const getCurrentQuestion = () => {
    return questions.value[currentQuestionIndex.value] || null
  }

  // 퀴즈 진행률 계산
  const getProgress = () => {
    if (totalQuestions.value === 0) return 0
    return ((currentQuestionIndex.value + 1) / totalQuestions.value) * 100
  }

  // 퀴즈 완료 여부
  const isQuizCompleted = () => {
    return currentQuestionIndex.value >= questions.value.length - 1 && showResult.value
  }

  return {
    // 상태
    questions,
    categories,
    currentQuestionIndex,
    answerResult,
    showResult,
    quizScore,
    totalQuestions,
    loading,
    
    // 액션
    fetchQuestions,
    fetchQuestion,
    submitAnswer,
    fetchCategories,
    nextQuestion,
    previousQuestion,
    resetQuiz,
    getCurrentQuestion,
    getProgress,
    isQuizCompleted
  }
})