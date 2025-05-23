<template>
  <div class="signup-container">
    <h1>회원가입</h1>
    
    <!-- 오류 메시지 표시 영역 추가 -->
    <div v-if="errors.length > 0" class="error-messages">
      <ul>
        <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
      </ul>
    </div>
    
    <form @submit.prevent="signup">
      <div class="form-group">
        <label for="username">아이디</label>
        <input v-model="username" type="text" id="username" required>
      </div>
      
      <div class="form-group">
        <label for="email">이메일</label>
        <input v-model="email" type="email" id="email" required>
      </div>
      
      <div class="form-group">
        <label for="password1">비밀번호</label>
        <input v-model="password1" type="password" id="password1" required>
      </div>
      
      <div class="form-group">
        <label for="password2">비밀번호 확인</label>
        <input v-model="password2" type="password" id="password2" required>
      </div>
      
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? '처리 중...' : '회원가입' }}
      </button>
    </form>
    
    <p>이미 계정이 있으신가요? <router-link to="/login">로그인</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const username = ref('');
const email = ref('');
const password1 = ref('');
const password2 = ref('');
const router = useRouter();
const authStore = useAuthStore();
const errors = ref([]);
const isLoading = ref(false);

const signup = async () => {
  // 폼 검증
  errors.value = [];
  
  if (password1.value !== password2.value) {
    errors.value.push('비밀번호가 일치하지 않습니다.');
    return;
  }
  
  try {
    isLoading.value = true;
    
    console.log('회원가입 시도:', {
      username: username.value,
      email: email.value,
    });
    
    // 회원가입 및 자동 로그인
    const response = await authStore.signup(username.value, password1.value, password2.value, email.value);
    
    console.log('회원가입 성공:', response);
    console.log('저장된 토큰:', localStorage.getItem('token'));
    console.log('인증 상태:', authStore.isAuthenticated);
    
    // 회원가입 성공 시 바로 메인 페이지로 이동
    router.push({ name: 'home' });
  } catch (error) {
    console.error('회원가입 실패:', error);
    
    // 서버에서 반환된 오류 메시지 처리
    if (error.response && error.response.data) {
      const responseData = error.response.data;
      
      // 각 필드별 오류 메시지를 배열에 추가
      for (const field in responseData) {
        if (Array.isArray(responseData[field])) {
          responseData[field].forEach(message => {
            const fieldName = field === 'password1' ? '비밀번호' : 
                             field === 'password2' ? '비밀번호 확인' :
                             field === 'username' ? '아이디' : 
                             field === 'email' ? '이메일' : field;
            
            errors.value.push(`${fieldName}: ${message}`);
          });
        } else if (typeof responseData[field] === 'string') {
          errors.value.push(`${field}: ${responseData[field]}`);
        }
      }
      
      // non_field_errors가 있는 경우
      if (responseData.non_field_errors) {
        responseData.non_field_errors.forEach(message => {
          errors.value.push(message);
        });
      }
    }
    
    // 오류 메시지가 없는 경우 기본 메시지 표시
    if (errors.value.length === 0) {
      errors.value.push('회원가입 처리 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.signup-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

p {
  text-align: center;
  margin-top: 20px;
}

.error-messages {
  background-color: #ffebee;
  border-left: 3px solid #f44336;
  margin-bottom: 20px;
  padding: 10px 15px;
}

.error-messages ul {
  margin: 0;
  padding-left: 15px;
}

.error-messages li {
  color: #d32f2f;
}
</style>