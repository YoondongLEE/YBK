<template>
  <div class="finance-info-container">
    <h1>금융 정보 길잡이</h1>
    <p class="description">유용한 금융 정보와 관심 종목 영상을 확인하세요</p>
    
    <!-- 기존 금융 정보 컨텐츠 -->
    <div class="finance-content">
      <div class="info-tabs">
        <button 
          :class="{ 'active': activeTab === 'info' }"
          @click="setActiveTab('info')"
        >
          금융 정보
        </button>
        <button 
          :class="{ 'active': activeTab === 'youtube' }"
          @click="setActiveTab('youtube')"
        >
          관심 종목 영상 검색
        </button>
      </div>
      
      <!-- 금융 정보 탭 -->
      <div v-if="activeTab === 'info'" class="info-section">
        <div class="info-list">
          <!-- 예적금 금리비교 카드 -->
          <div class="info-card" @click="goToInterestRateCompare">
            <div class="info-image-placeholder">
              <!-- 이미지 로딩 실패시 대체 텍스트로 표시 -->
              <div class="placeholder-text">금리비교</div>
            </div>
            <div class="info-content">
              <h3>금리비교</h3>
              <p>다양한 은행의 예금/적금 상품들의 금리를 한눈에 비교해보세요.</p>
            </div>
          </div>
          
          <!-- 다른 금융 정보 카드들은 기존과 동일하게 유지 -->
          <div class="info-card">
            <div class="info-image-placeholder">
              <div class="placeholder-text">금융 트렌드</div>
            </div>
            <div class="info-content">
              <h3>최신 금융 트렌드</h3>
              <p>금융 시장의 최신 동향과 투자 트렌드를 알아보세요.</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- YouTube 탭: SavedItems 제거하고 VideoSearch만 표시 -->
      <div v-else-if="activeTab === 'youtube'" class="youtube-section">
        <!-- 영상 검색 컴포넌트 -->
        <VideoSearch />
        
        <!-- 저장된 영상/채널은 마이페이지로 이동함을 안내 -->
        <div class="saved-info">
          <p>
            <strong>알림:</strong> 저장한 영상과 채널은 마이페이지에서 확인할 수 있습니다.
            <router-link to="/mypage" class="mypage-link">마이페이지로 이동</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import VideoSearch from '../components/youtube/VideoSearch.vue';

const router = useRouter();
const activeTab = ref('info');

const setActiveTab = (tab) => {
  activeTab.value = tab;
};

// 금리비교 페이지로 이동하는 함수
const goToInterestRateCompare = () => {
  router.push({ name: 'interest-compare' });
};
</script>

<style scoped>
.finance-info-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 10px;
}

.description {
  color: #666;
  margin-bottom: 30px;
}

.info-tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
}

.info-tabs button {
  background: none;
  border: none;
  padding: 12px 20px;
  font-size: 16px;
  cursor: pointer;
  margin-right: 10px;
  color: #666;
}

.info-tabs button.active {
  color: #4a90e2;
  border-bottom: 3px solid #4a90e2;
  font-weight: bold;
}

.info-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.info-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  background-color: #fff;
}

.info-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.info-image-placeholder {
  height: 150px;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-image-placeholder img {
  max-width: 100%;
  max-height: 100%;
}

.info-content {
  padding: 15px;
}

.info-content h3 {
  margin: 0 0 10px;
  color: #333;
}

.info-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.youtube-section {
  margin-top: 20px;
}

.placeholder-text {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 18px;
  font-weight: bold;
  color: #555;
  background-color: #f0f0f0;
}

.saved-info {
  margin-top: 30px;
  padding: 15px;
  background-color: #f5f8ff;
  border-radius: 8px;
  border-left: 4px solid #4a90e2;
}

.mypage-link {
  display: inline-block;
  margin-left: 10px;
  color: #4a90e2;
  font-weight: bold;
  text-decoration: underline;
}
</style>