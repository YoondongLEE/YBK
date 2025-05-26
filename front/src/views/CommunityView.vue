<template>
  <div class="community-container">
    <h1>커뮤니티</h1>
    <p class="subtitle">금융 지식과 경험을 나누는 공간입니다</p>
    
    <div class="community-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
// 필요한 경우 여기에 스크립트 추가
</script>

<style scoped>
.community-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 10px;
  color: #333;
}

.subtitle {
  color: #666;
  margin-bottom: 30px;
}

.community-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}
</style>