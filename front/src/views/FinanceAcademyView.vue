<!-- filepath: c:\Users\SSAFY\LYD\final-pjt\front\src\views\FinanceAcademyView.vue -->
<template>
  <div class="academy-container">
    <h1>금융 아카데미</h1>
    <p class="description">다양한 금융 교육 콘텐츠를 제공합니다</p>
    
    <div class="course-list">
      <!-- 실제 데이터를 연동하면 v-for로 반복 렌더링 -->
      <div class="course-card">
        <div class="course-image-placeholder"></div>
        <div class="course-info">
          <h3>금융 기초 개념</h3>
          <p>금융 용어와 기본 개념에 대해 배워봅니다.</p>
        </div>
      </div>
      
      <div class="course-card">
        <div class="course-image-placeholder"></div>
        <div class="course-info">
          <h3>투자 전략 기초</h3>
          <p>효과적인 투자 전략 수립 방법을 알아봅니다.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 나중에 API 연동 로직 추가
</script>

<style scoped>
.academy-container {
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

.course-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.course-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.course-image-placeholder {
  height: 150px;
  background-color: #e0e0e0;
}

.course-info {
  padding: 15px;
}

h3 {
  margin-bottom: 10px;
}

p {
  color: #666;
}
</style>