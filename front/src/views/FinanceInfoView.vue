<!-- filepath: c:\Users\SSAFY\LYD\final-pjt\front\src\views\FinanceInfoView.vue -->
<template>
  <div class="info-container">
    <h1>금융 정보 길잡이</h1>
    <p class="description">유용한 금융 정보를 확인하세요</p>
    
    <div class="info-list">
      <!-- 실제 데이터를 연동하면 v-for로 반복 렌더링 -->
      <div class="info-card">
        <div class="info-image-placeholder"></div>
        <div class="info-content">
          <h3>최신 금융 트렌드</h3>
          <p>최근 금융 시장의 주요 트렌드와 이슈를 소개합니다.</p>
        </div>
      </div>
      
      <div class="info-card">
        <div class="info-image-placeholder"></div>
        <div class="info-content">
          <h3>재테크 팁</h3>
          <p>효과적인 재테크 방법과 팁을 알아봅니다.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 나중에 API 연동 로직 추가
</script>

<style scoped>
.info-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 10px;
}

.description {
  color: #666;
  margin-bottom: 30px;
}

.info-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.info-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s;
}

.info-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.info-image-placeholder {
  height: 150px;
  background-color: #e0e0e0;
}

.info-content {
  padding: 15px;
}

h3 {
  margin-bottom: 10px;
}

p {
  color: #666;
}
</style>