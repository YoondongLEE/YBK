<template>
  <div class="concept-category-container">
    <div class="page-header">
      <h1>📚 {{ getDifficultyLabel(difficulty) }} 개념 학습</h1>
      <p>카테고리별로 금융 개념을 체계적으로 학습해보세요</p>
      <button @click="goBack" class="back-button">← 돌아가기</button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>카테고리를 불러오는 중...</p>
    </div>

    <div v-else-if="categories.length > 0" class="categories-grid">
      <div 
        v-for="category in categories" 
        :key="category.id"
        class="category-card"
        @click="selectCategory(category)"
      >
        <div class="category-icon">
          {{ getCategoryIcon(category.name) }}
        </div>
        <div class="category-content">
          <h3>{{ category.name }}</h3>
          <p>{{ category.description }}</p>
          <div class="question-count">
            📝 {{ category.question_count }}개 문제
          </div>
        </div>
        <div class="arrow">→</div>
      </div>
    </div>

    <div v-else class="no-categories">
      <p>해당 난이도의 카테고리를 찾을 수 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const difficulty = ref(route.params.difficulty)
const categories = ref([])
const loading = ref(true)

const getDifficultyLabel = (diff) => {
  const labels = {
    'youth': '청소년',
    'adult_basic': '성인 기본',
    'adult_advanced': '성인 심화'
  }
  return labels[diff] || diff
}

const getCategoryIcon = (categoryName) => {
  const icons = {
    '청소년 금융': '🎓',
    '성인 기본 금융': '💼',
    '성인 심화 금융': '📈',
    '투자': '💰',
    '보험': '🛡️',
    '세금': '📋',
    '대출': '🏦',
    '예적금': '💳',
    '카드': '💳'
  }
  return icons[categoryName] || '📚'
}

const fetchCategories = async () => {
  try {
    loading.value = true
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/finance-academy/concept-study/${difficulty.value}/categories/`)
    categories.value = response.data.categories
  } catch (error) {
    console.error('카테고리 조회 실패:', error)
    alert('카테고리를 불러오는데 실패했습니다.')
  } finally {
    loading.value = false
  }
}

const selectCategory = (category) => {
  router.push({
    name: 'concept-study',
    params: {
      difficulty: difficulty.value,
      categoryId: category.id
    }
  })
}

const goBack = () => {
  router.push({ name: 'financeAcademy' })
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.concept-category-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
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

.back-button {
  position: absolute;
  left: 0;
  top: 0;
  background: #95a5a6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
}

.loading {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #ecf0f1;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
}

.category-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
  border-color: #3498db;
}

.category-icon {
  font-size: 3rem;
  flex-shrink: 0;
}

.category-content {
  flex: 1;
}

.category-content h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.category-content p {
  color: #7f8c8d;
  margin-bottom: 15px;
  line-height: 1.5;
}

.question-count {
  background: #e3f2fd;
  color: #1976d2;
  padding: 8px 12px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: 500;
  display: inline-block;
}

.arrow {
  font-size: 1.5rem;
  color: #3498db;
  flex-shrink: 0;
}

.no-categories {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

@media (max-width: 768px) {
  .concept-category-container {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .categories-grid {
    grid-template-columns: 1fr;
  }
  
  .category-card {
    padding: 20px;
  }
  
  .category-icon {
    font-size: 2.5rem;
  }
  
  .category-content h3 {
    font-size: 1.3rem;
  }
  
  .back-button {
    position: static;
    margin-bottom: 20px;
  }
}
</style>