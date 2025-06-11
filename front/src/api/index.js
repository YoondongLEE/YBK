import axios from 'axios'

// API 기본 URL 설정 - Railway Backend URL로 변경
const api = axios.create({
  // baseURL: 'http://localhost:8000/api',
  baseURL: 'https://ybk-production.up.railway.app/api',  // 변경된 부분
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터 설정 - 토큰이 있으면 헤더에 추가
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

export default api