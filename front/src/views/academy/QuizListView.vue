<template>
  <div class="quiz-list-container">
    <div class="page-header">
      <h1>💰 금융교육 퀴즈</h1>
      <p>다양한 난이도의 금융 퀴즈로 실력을 테스트해보세요!</p>
    </div>

    <div class="quiz-categories">
      <div class="category-card" @click="startQuiz('youth')">
        <div class="category-icon">🎓</div>
        <h3>청소년 금융 퀴즈</h3>
        <p>금융의 기초부터 차근차근 배워보세요</p>
        <div class="difficulty">난이도: ⭐</div>
        <button class="start-button">시작하기</button>
      </div>

      <div class="category-card" @click="startQuiz('adult_basic')">
        <div class="category-icon">💼</div>
        <h3>성인 기본 금융 퀴즈</h3>
        <p>실생활에 필요한 금융 지식을 익혀보세요</p>
        <div class="difficulty">난이도: ⭐⭐</div>
        <button class="start-button">시작하기</button>
      </div>

      <div class="category-card" @click="startQuiz('adult_advanced')">
        <div class="category-icon">📈</div>
        <h3>성인 심화 금융 퀴즈</h3>
        <p>전문적인 금융 투자 지식에 도전해보세요</p>
        <div class="difficulty">난이도: ⭐⭐⭐</div>
        <button class="start-button">시작하기</button>
      </div>
    </div>

    <div class="quiz-info">
      <h3>📋 퀴즈 진행 방법</h3>
      <ul>
        <li>각 문제는 4개의 선택지 중 하나를 고르는 객관식입니다</li>
        <li>답안 제출 후 즉시 정답 여부와 해설을 확인할 수 있습니다</li>
        <li>모든 문제를 풀고 나면 최종 점수를 확인할 수 있습니다</li>
        <li>언제든지 다시 도전할 수 있습니다</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const startQuiz = (difficulty) => {
  router.push({ 
    name: 'interactiveQuiz', 
    params: { difficulty } 
  })
}
</script>

<style scoped>
.quiz-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  font-size: 1.2rem;
  color: #7f8c8d;
}

.quiz-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 50px;
}

.category-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
  border-color: #3498db;
}

.category-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.category-card h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

.category-card p {
  color: #7f8c8d;
  margin-bottom: 20px;
  line-height: 1.6;
}

.difficulty {
  font-weight: bold;
  color: #e67e22;
  margin-bottom: 25px;
}

.start-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s ease;
  width: 100%;
}

.start-button:hover {
  background: #2980b9;
}

.quiz-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 30px;
  border-left: 4px solid #3498db;
}

.quiz-info h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.quiz-info ul {
  list-style: none;
  padding: 0;
}

.quiz-info li {
  padding: 8px 0;
  color: #555;
  position: relative;
  padding-left: 25px;
}

.quiz-info li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #27ae60;
  font-weight: bold;
}

@media (max-width: 768px) {
  .quiz-list-container {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .quiz-categories {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .category-card {
    padding: 20px;
  }
}
</style>