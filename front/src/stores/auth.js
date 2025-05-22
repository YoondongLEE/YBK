import { defineStore } from 'pinia';
import axios from 'axios';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null);
  const user = ref(null);
  const isAuthenticated = ref(!!token.value);
  
  // API URL 설정
  const API_URL = 'http://localhost:8000/api'; // Django 백엔드 URL

  // 로그인 함수 수정
  const login = async (username, password) => {
    try {
      // dj-rest-auth는 username과 password 필드만 필요함
      const response = await axios.post(`${API_URL}/accounts/login/`, {
        username,
        password
      });
      
      // 토큰 저장 (키 이름 확인)
      const authToken = response.data.key; // dj-rest-auth는 'key' 필드로 토큰 반환
      token.value = authToken;
      localStorage.setItem('token', authToken);
      isAuthenticated.value = true;
      
      // 사용자 정보 가져오기
      await fetchUserProfile();
      
      return true;
    } catch (error) {
      console.error('로그인 실패:', error);
      throw error;
    }
  };

  // 회원가입 함수 수정 - dj-rest-auth 형식에 맞게 변경
  const signup = async (username, password1, password2, email) => {
    try {
      // dj-rest-auth는 이 형태로 데이터를 기대합니다
      const response = await axios.post(`${API_URL}/accounts/signup/`, {
        username,
        email,
        password1,
        password2
      });
      
      // 회원가입 성공 시 자동 로그인 처리
      // 회원가입 응답에 바로 키가 포함되어 있을 수 있음
      if (response.data.key) {
        // 토큰 저장
        const authToken = response.data.key;
        token.value = authToken;
        localStorage.setItem('token', authToken);
        isAuthenticated.value = true;
        
        // 사용자 정보 가져오기
        await fetchUserProfile();
      } else {
        // 키가 없으면 별도로 로그인 요청
        await login(username, password1);
      }
      
      return true;
    } catch (error) {
      console.error('회원가입 실패:', error);
      if (error.response && error.response.data) {
        console.error('서버 응답:', error.response.data);
      }
      throw error;
    }
  };

  // 로그아웃 함수
  const logout = async () => {
    try {
      // 토큰이 있는 경우에만 로그아웃 API 호출
      if (token.value) {
        await axios.post(`${API_URL}/accounts/logout/`, {}, {
          headers: {
            'Authorization': `Token ${token.value}`
          }
        });
      }
      
      // 로컬 스토리지와 상태에서 토큰 제거
      localStorage.removeItem('token');
      token.value = null;
      user.value = null;
      isAuthenticated.value = false;
      
      return true;
    } catch (error) {
      console.error('로그아웃 실패:', error);
      // 로그아웃은 클라이언트 측에서라도 완료
      localStorage.removeItem('token');
      token.value = null;
      user.value = null;
      isAuthenticated.value = false;
      throw error;
    }
  };

  // 사용자 정보 가져오기
  const fetchUserProfile = async () => {
    try {
      if (!token.value) return;
      
      const response = await axios.get(`${API_URL}/accounts/user/`, {
        headers: {
          'Authorization': `Token ${token.value}`
        }
      });
      
      user.value = response.data;
    } catch (error) {
      console.error('사용자 정보 가져오기 실패:', error);
      // 토큰이 유효하지 않으면 로그아웃 처리
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        await logout();
      }
    }
  };

  // 초기화 - 앱 시작시 사용자 정보 로드
  if (token.value) {
    fetchUserProfile();
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    signup,
    logout,
    fetchUserProfile
  };
}, {
  persist: {
    storage: localStorage,
    paths: ['token']
  }
});