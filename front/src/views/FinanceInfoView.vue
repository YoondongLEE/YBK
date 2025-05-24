<!-- filepath: /Users/iyundong/Desktop/SSAFY/1학기_관통/final-pjt-v1/final-pjt/front/src/views/FinanceInfoView.vue -->
<template>
  <div class="finance-info-container">
    <h1>금융 정보 길잡이</h1>
    
    <div class="tabs">
      <button 
        @click="activeTab = 'info'" 
        :class="{ active: activeTab === 'info' }"
        class="tab-btn"
      >
        금융 정보
      </button>
      <button 
        @click="activeTab = 'youtube'" 
        :class="{ active: activeTab === 'youtube' }"
        class="tab-btn"
      >
        금융 영상
      </button>
    </div>
    
    <!-- 금융 정보 탭 -->
    <div v-if="activeTab === 'info'" class="finance-content">
      <div class="info-cards">
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
        
        <!-- 현물 상품 비교 카드 (신규 추가) -->
        <div class="info-card" @click="goToMetalPrices">
          <div class="info-image-placeholder">
            <div class="placeholder-text">금/은 가격</div>
          </div>
          <div class="info-content">
            <h3>금/은 가격 변동</h3>
            <p>금과 은의 가격 변동 추이를 확인하고 투자 판단에 활용해보세요.</p>
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
      
      <!-- 기존 내용 유지 -->
    </div>
    
    <!-- YouTube 탭 -->
    <div v-else-if="activeTab === 'youtube'" class="youtube-section">
      <!-- 영상 검색 컴포넌트 -->
      <VideoSearch />
      
      <!-- 저장된 영상/채널은 마이페이지로 이동함을 안내 -->
      <div class="saved-info">
        <p>
          <strong>알림:</strong> 저장한 영상과 채널은 마이페이지에서 확인할 수 있습니다.
          <router-link to="/mypage" class="saved-link">마이페이지로 이동</router-link>
        </p>
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

// 금리비교 페이지로 이동
const goToInterestRateCompare = () => {
  router.push({ name: 'interest-rate-compare' });
};

// 금/은 가격 변동 페이지로 이동 (신규 추가)
const goToMetalPrices = () => {
  router.push({ name: 'metal-prices' });
};
</script>

<style scoped>
.finance-info-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 30px;
  color: #333;
}

.tabs {
  display: flex;
  margin-bottom: 30px;
  border-bottom: 2px solid #e0e0e0;
}

.tab-btn {
  padding: 12px 24px;
  background: none;
  border: none;
  font-size: 16px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  position: relative;
  transition: color 0.3s;
}

.tab-btn.active {
  color: #4a90e2;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: #4a90e2;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.info-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  background-color: white;
}

.info-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.info-image-placeholder {
  height: 160px;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-text {
  font-size: 18px;
  color: #666;
  font-weight: 500;
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
  line-height: 1.5;
}

.youtube-section {
  margin-top: 20px;
}

.saved-info {
  margin-top: 30px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #4a90e2;
}

.saved-link {
  color: #4a90e2;
  text-decoration: none;
  margin-left: 5px;
  font-weight: 500;
}

.saved-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .info-cards {
    grid-template-columns: 1fr;
  }
  
  .tabs {
    flex-direction: column;
    border-bottom: none;
  }
  
  .tab-btn {
    padding: 10px;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .tab-btn.active::after {
    display: none;
  }
}
</style>