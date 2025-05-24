import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import router from '../router'

// 기본 API 인스턴스 생성 (인증 관련 전용)
const authApi = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
  
  // 로그인 상태 확인
  const isAuthenticated = computed(() => !!token.value)
  
  // 로그인
  const login = async (username, password) => {
    try {
      // withCredentials 옵션 제거 (필요하지 않음)
      const response = await authApi.post('/accounts/login/', {
        username,
        password
      })
      
      console.log('로그인 응답:', response.data)
      
      // 토큰 저장
      if (response.data && response.data.key) {
        token.value = response.data.key
        localStorage.setItem('token', response.data.key)
        
        // 사용자 정보 가져오기
        await fetchUserInfo()
        return response
      } else {
        throw new Error('로그인 응답에 토큰이 없습니다')
      }
    } catch (error) {
      console.error('로그인 실패:', error)
      throw error
    }
  }
  
  // 회원가입
  const signup = async (username, password1, password2, email) => {
    try {
      const response = await authApi.post('/accounts/signup/', {
        username,
        password1,
        password2,
        email
      })
      
      console.log('회원가입 응답:', response.data)
      
      // 토큰 저장
      if (response.data && response.data.key) {
        token.value = response.data.key
        localStorage.setItem('token', response.data.key)
        
        // 사용자 정보 가져오기
        await fetchUserInfo()
        return response
      } else {
        throw new Error('회원가입 응답에 토큰이 없습니다')
      }
    } catch (error) {
      console.error('회원가입 실패:', error)
      throw error
    }
  }
  
  // 로그아웃
  const logout = async () => {
    try {
      if (token.value) {
        await authApi.post('/accounts/logout/', {}, {
          headers: {
            'Authorization': `Token ${token.value}`
          }
        })
      }
    } catch (error) {
      console.error('로그아웃 API 에러:', error)
    } finally {
      // 로컬 상태 초기화
      token.value = ''
      user.value = {}
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 홈페이지로 리다이렉트
      router.push({ name: 'home' })
    }
  }
  
  // 사용자 정보 가져오기
const fetchUserInfo = async () => {
  if (!token.value) {
    console.warn('토큰이 없어 사용자 정보를 가져올 수 없습니다.')
    return null
  }
  
  try {
    // profile 대신 user 엔드포인트 사용
    const response = await authApi.get('/accounts/user/', {
      headers: {
        'Authorization': `Token ${token.value}`
      }
    })
    
    user.value = response.data
    localStorage.setItem('user', JSON.stringify(response.data))
    return response.data
  } catch (error) {
    console.error('사용자 정보 가져오기 실패:', error)
    
    if (error.response && error.response.status === 401) {
      // 토큰이 유효하지 않은 경우 로그아웃 처리
      token.value = ''
      user.value = {}
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
    
    throw error
  }
}
  
  return {
    token,
    user,
    isAuthenticated,
    login,
    signup,
    logout,
    fetchUserInfo
  }
})