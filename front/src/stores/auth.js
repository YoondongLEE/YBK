import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    user: null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('http://localhost:8000/api/accounts/login/', {
          username,
          password
        })
        this.token = response.data.access_token
        this.user = { username }
        return response
      } catch (error) {
        throw new Error('로그인 실패')
      }
    },
    async signup(username, password1, password2, email) {
      try {
        const response = await axios.post('http://localhost:8000/api/accounts/signup/', {
          username,
          password1,
          password2,
          email
        })
        return response
      } catch (error) {
        throw new Error('회원가입 실패')
      }
    },
    logout() {
      this.token = null
      this.user = null
    }
  },
  persist: true
})