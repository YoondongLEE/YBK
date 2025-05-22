<template>
  <div class="mypage-container">
    <h1>마이페이지</h1>
    
    <div v-if="isLoading" class="loading">
      <p>로딩 중...</p>
    </div>
    
    <div v-else class="user-info-section">
      <div class="user-profile">
        <h2>내 정보</h2>
        <div class="info-item">
          <span class="label">아이디:</span>
          <span class="value">{{ authStore.user?.username }}</span>
        </div>
        <div class="info-item">
          <span class="label">이메일:</span>
          <span class="value">{{ authStore.user?.email }}</span>
        </div>
        <div class="info-item">
          <span class="label">가입일:</span>
          <span class="value">{{ formatDate(authStore.user?.date_joined) }}</span>
        </div>
      </div>
      
      <!-- 마이페이지에 추가할 다른 섹션들은 나중에 구현 -->
      <div class="placeholder-section">
        <h3>마이페이지 추가 정보</h3>
        <p>이 부분에 마이페이지의 추가 정보가 들어갈 예정입니다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const isLoading = ref(true);

// 날짜 포맷팅 함수
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR');
};

onMounted(async () => {
  try {
    // 사용자 정보 가져오기
    await authStore.fetchUserProfile();
  } catch (error) {
    console.error('사용자 정보를 불러오는 중 오류 발생:', error);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.mypage-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 30px;
  color: #333;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.user-info-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.user-profile {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

h2 {
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.info-item {
  margin-bottom: 15px;
  display: flex;
}

.label {
  font-weight: 600;
  width: 100px;
  color: #555;
}

.value {
  color: #333;
}

.placeholder-section {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 25px;
  border: 1px dashed #ddd;
}

h3 {
  color: #555;
  margin-bottom: 15px;
}

@media (max-width: 768px) {
  .info-item {
    flex-direction: column;
  }
  
  .label {
    margin-bottom: 5px;
  }
}
</style>