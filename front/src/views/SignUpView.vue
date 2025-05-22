<!-- filepath: c:\Users\SSAFY\LYD\final-pjt\front\src\views\SignupView.vue -->
<template>
  <div class="signup-container">
    <h1>회원가입</h1>
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
      <button type="submit">가입하기</button>
    </form>
    <p>이미 계정이 있으신가요? <router-link to="/login">로그인</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
// import { useAuthStore } from '../stores/auth';

const username = ref('');
const email = ref('');
const password1 = ref('');
const password2 = ref('');
const router = useRouter();
// const authStore = useAuthStore();

const signup = async () => {
  if (password1.value !== password2.value) {
    alert('비밀번호가 일치하지 않습니다.');
    return;
  }
  
  try {
    // 임시로 회원가입 성공으로 처리
    // await authStore.signup(username.value, password1.value, password2.value, email.value);
    alert('회원가입 성공! 로그인 페이지로 이동합니다.');
    router.push({ name: 'login' });
  } catch (error) {
    alert('회원가입 실패: ' + error.message);
  }
};
</script>

<style scoped>
.signup-container {
  max-width: 400px;
  margin: 40px auto;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
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

button:hover {
  background-color: #3a7bd5;
}

p {
  margin-top: 15px;
  text-align: center;
}

a {
  color: #4a90e2;
}
</style>