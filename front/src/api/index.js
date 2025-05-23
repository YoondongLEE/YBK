import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 요청 인터셉터
api.interceptors.request.use(config => {
  // localStorage에서 토큰 가져오기
  const token = localStorage.getItem('token');
  
  // 토큰이 있으면 헤더에 추가
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  
  return config;
}, error => {
  return Promise.reject(error);
});

// 응답 인터셉터 - 토큰 만료 처리
api.interceptors.response.use(
  response => response,
  async error => {
    // 오류 응답이 없는 경우 (네트워크 오류 등)
    if (!error.response) {
      console.error('네트워크 오류:', error);
      return Promise.reject(error);
    }
    
    const originalRequest = error.config;
    
    // 토큰 만료된 경우 (401 오류)
    if (error.response.status === 401 && !originalRequest._retry) {
      // 로그인 페이지에서는 401 에러 무시
      if (window.location.href.includes('login') || window.location.href.includes('signup')) {
        return Promise.reject(error);
      }
      
      originalRequest._retry = true;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // 현재 페이지가 로그인 필요한 페이지면 로그인 페이지로 리다이렉트
      window.location.href = '/login';
      return Promise.reject(error);
    }
    
    return Promise.reject(error);
  }
);

export default api;