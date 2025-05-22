

<!-- filepath: c:\Users\SSAFY\LYD\final-pjt\front\src\App.vue -->
<template>
  <header>
    <div class="header-container">
      <router-link to="/" class="logo">윤봉길</router-link>
      <div class="auth-links">
        <router-link to="/login">로그인</router-link>
        <span class="separator">|</span>
        <router-link to="/signup">회원가입</router-link>
      </div>
    </div>
  </header>

  <main>
    <router-view />
  </main>
</template>

<script>

</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Arial', sans-serif;
  line-height: 1.6;
  color: #333;
}

header {
  background-color: #f8f9fa;
  padding: 15px 0;
  border-bottom: 1px solid #e0e0e0;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  text-decoration: none;
}

.auth-links a {
  text-decoration: none;
  color: #333;
  margin-left: 5px;
  margin-right: 5px;
}

.separator {
  color: #ccc;
}

main {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}
</style>