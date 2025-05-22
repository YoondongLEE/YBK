<template>
  <div class="login-container">
    <h1>로그인</h1>
    
    <!-- 오류 메시지 표시 영역 추가 -->
    <div v-if="errors.length > 0" class="error-messages">
      <ul>
        <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
      </ul>
    </div>
    
    <form @submit.prevent="login">
      <div class="form-group">
        <label for="username">아이디</label>
        <input v-model="username" type="text" id="username" required>
      </div>
      <div class="form-group">
        <label for="password">비밀번호</label>
        <input v-model="password" type="password" id="password" required>
      </div>
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? '처리 중...' : '로그인' }}
      </button>
    </form>
    <p>계정이 없으신가요? <router-link to="/signup">회원가입</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const username = ref('');
const password = ref('');
const router = useRouter();
const authStore = useAuthStore();
const errors = ref([]);
const isLoading = ref(false);

const login = async () => {
  errors.value = [];
  
  try {
    isLoading.value = true;
    
    // 로그인 시도
    await authStore.login(username.value, password.value);
    
    // 로그인 성공 시 바로 메인 페이지로 이동 (alert 없음)
    router.push({ name: 'home' });
  } catch (error) {
    console.error('로그인 실패:', error);
    
    // 서버에서 반환된 오류 메시지 처리
    if (error.response && error.response.data) {
      const responseData = error.response.data;
      
      // 각 필드별 오류 메시지를 배열에 추가
      for (const field in responseData) {
        if (Array.isArray(responseData[field])) {
          responseData[field].forEach(message => {
            errors.value.push(`${field}: ${message}`);
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
      errors.value.push('로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.');
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 40px auto;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.error-messages {
  background-color: #ffebee;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  color: #d32f2f;
}

.error-messages ul {
  margin: 0;
  padding-left: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover:not(:disabled) {
  background-color: #3a7bd5;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

p {
  margin-top: 15px;
  text-align: center;
}

a {
  color: #4a90e2;
}
</style>