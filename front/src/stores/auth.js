import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import router from '@/router'

// 인증 전용 Axios 인스턴스 - Railway Backend URL로 변경
const authApi = axios.create({
  baseURL: 'https://ybk-production.up.railway.app/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

export const useAuthStore = defineStore('auth', () => {
  // 상태
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const loadingUser = ref(false)
  const error = ref(null)

  // 로그인 여부
  const isAuthenticated = computed(() => !!token.value)

  // 토큰 저장
  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  // 인증 해제
  function clearAuth() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 사용자 정보 조회
  async function fetchUserInfo() {
    if (!token.value) {
      user.value = null
      return null
    }
    loadingUser.value = true
    error.value = null
    try {
      const res = await authApi.get('/accounts/user/', {
        headers: { Authorization: `Token ${token.value}` }
      })
      user.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
      return res.data
    } catch (err) {
      console.error('사용자 정보 로딩 실패:', err)
      error.value = '사용자 정보를 가져올 수 없습니다.'
      if (err.response?.status === 401) clearAuth()
      throw err
    } finally {
      loadingUser.value = false
    }
  }

  // 로그인
  async function login(username, password) {
    loadingUser.value = true
    error.value = null
    try {
      const res = await authApi.post('/accounts/login/', { username, password })
      const key = res.data.key
      if (!key) throw new Error('토큰이 없습니다')
      setToken(key)
      await fetchUserInfo()
      router.push({ name: 'home' })
      return res
    } catch (err) {
      console.error('로그인 실패:', err)
      error.value = '로그인 실패. 다시 시도해주세요.'
      throw err
    } finally {
      loadingUser.value = false
    }
  }

  // 회원가입
  async function signup(username, password1, password2, email) {
    loadingUser.value = true
    error.value = null
    try {
      const res = await authApi.post('/accounts/signup/', {
        username, password1, password2, email
      })
      const key = res.data.key
      if (!key) throw new Error('토큰이 없습니다')
      setToken(key)
      await fetchUserInfo()
      router.push({ name: 'home' })
      return res
    } catch (err) {
      console.error('회원가입 실패:', err)
      error.value = '회원가입 실패. 다시 시도해주세요.'
      throw err
    } finally {
      loadingUser.value = false
    }
  }

  // 로그아웃
  async function logout() {
    try {
      if (token.value) {
        await authApi.post('/accounts/logout/', {}, {
          headers: { Authorization: `Token ${token.value}` }
        })
      }
    } catch (err) {
      console.error('로그아웃 실패:', err)
    } finally {
      clearAuth()
      router.push({ name: 'home' })
    }
  }

  return {
    token,
    user,
    loadingUser,
    error,
    isAuthenticated,
    login,
    signup,
    logout,
    fetchUserInfo
  }
})