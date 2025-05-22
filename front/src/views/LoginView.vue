<!-- filepath: c:\Users\SSAFY\LYD\final-pjt\front\src\views\LoginView.vue -->
<template>
  <div class="login-container">
    <h1>로그인</h1>
    <form @submit.prevent="login">
      <div class="form-group">
        <label for="username">아이디</label>
        <input v-model="username" type="text" id="username" required>
      </div>
      <div class="form-group">
        <label for="password">비밀번호</label>
        <input v-model="password" type="password" id="password" required>
      </div>
      <button type="submit">로그인</button>
    </form>
    <p>계정이 없으신가요? <router-link to="/signup">회원가입</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
// import { useAuthStore } from '../stores/auth';

const username = ref('');
const password = ref('');
const router = useRouter();
// const authStore = useAuthStore();

const login = async () => {
  try {
    // 임시로 로그인 성공으로 처리
    // await authStore.login(username.value, password.value);
    alert('로그인 성공!');
    router.push({ name: 'home' });
  } catch (error) {
    alert('로그인 실패: ' + error.message);
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