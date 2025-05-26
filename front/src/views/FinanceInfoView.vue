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
      <button 
        @click="activeTab = 'bankmap'" 
        :class="{ active: activeTab === 'bankmap' }"
        class="tab-btn"
      >
        가까운 은행 찾기
      </button>
    </div>
    
    <!-- 금융 정보 탭 -->
    <div v-if="activeTab === 'info'" class="finance-content">
      <div class="info-cards">
        <!-- 예적금 금리비교 카드 -->
        <div class="info-card" @click="goToInterestRateCompare">
          <div class="info-image">
            <img src="@/assets/icons/interest_rate.png" alt="금리 비교">
          </div>
          <div class="info-content">
            <h3>금리 비교</h3>
            <p>다양한 은행의 예금/적금 상품들의 금리를 한눈에 비교해보세요.</p>
          </div>
        </div>
        
        <!-- 현물 상품 비교 카드 (신규 추가) -->
        <div class="info-card" @click="goToMetalPrices">
          <div class="info-image">
            <img src="@/assets/icons/gold_silver.png" alt="금/은 가격">
          </div>
          <div class="info-content">
            <h3>금/은 가격 변동</h3>
            <p>금과 은의 가격 변동 추이를 확인하고 투자 판단에 활용해보세요.</p>
          </div>
        </div>

        <!-- 추후 기능(빈칸 채우기 용) -->
        <div class="info-card">
          <div class="info-image">
            <img src="@/assets/icons/exchange_rate.png" alt="추후 구현">
          </div>
          <div class="info-content">
            <h3>환율</h3>
            <p>추후 업데이트 예정</p>
          </div>
        </div>
      </div>
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
    <!-- 가까운 은행 찾기 탭 -->
    <div v-else-if="activeTab === 'bankmap'" class="bankmap-section">
      <BankMapSearch />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import VideoSearch from '../components/youtube/VideoSearch.vue';
import BankMapSearch from '../components/map/BankMapSearch.vue'; 

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
  font-family: 'Noto Sans KR', sans-serif;
}

h1 {
  margin-bottom: 30px;
  color: #333;
  font-weight: 700;
  position: relative;
  display: inline-block;
  padding-bottom: 8px;
}

h1::after {
  content: '';
  position: absolute;
  width: 60px;
  height: 3px;
  background-color: #4a90e2;
  bottom: 0;
  left: 0;
}

.tabs {
  display: flex;
  margin-bottom: 40px;
  border-bottom: none;
  gap: 5px;
}

.tab-btn {
  padding: 12px 24px;
  background: #f5f7fa;
  border: none;
  border-radius: 30px;
  font-size: 15px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn.active {
  color: white;
  background-color: #4a90e2;
  box-shadow: 0 4px 10px rgba(74, 144, 226, 0.3);
}

/* 탭 버튼 활성화 상태 스타일 수정 (밑줄 제거) */
.tab-btn.active::after {
  display: none;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.info-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  cursor: pointer;
  background-color: white;
  height: 280px; /* 고정 높이 설정 */
}

.info-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.info-image {
  height: 180px;
  width: 100%;
  position: relative;
  overflow: hidden;
}

.info-image::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 50%, rgba(0, 0, 0, 0.5) 100%);
  z-index: 1;
  opacity: 0;
  transition: opacity 0.3s;
}

.info-card:hover .info-image::before {
  opacity: 1;
}

.info-image img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 이미지가 여백 없이 꽉 채우도록 설정 */
  transition: transform 0.5s;
}

.info-card:hover .info-image img {
  transform: scale(1.08);
}

.info-content {
  padding: 20px;
  position: relative;
  z-index: 2;
}

.info-content h3 {
  margin: 0 0 8px;
  color: #222;
  font-size: 18px;
  font-weight: 600;
}

.info-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

/* 트렌디한 카드 액션 버튼 추가 */
.info-card::after {
  content: '→';
  position: absolute;
  top: 20px; /* 하단에서 상단으로 변경 */
  right: 20px;
  width: 30px;
  height: 30px;
  background-color: #4a90e2;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
  z-index: 5; /* 이미지 그라데이션 오버레이보다 위에 표시되도록 z-index 추가 */
}

.info-card:hover::after {
  opacity: 1;
  transform: translateX(0);
}

/* 카드 타입별 색상 다르게 적용 */
.info-card:nth-child(1)::after {
  background-color: #4a90e2; /* 파란색 - 금리 비교 */
}

.info-card:nth-child(2)::after {
  background-color: #f5b700; /* 노란색/금색 - 금/은 가격 */
}

.info-card:nth-child(3)::after {
  background-color: #27ae60; /* 녹색 - 환율 */
}

.youtube-section {
  margin-top: 20px;
}

.saved-info {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #4a90e2;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
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

/* 부드러운 트랜지션 효과 추가 */
* {
  transition-property: transform, box-shadow, opacity, background-color, color;
  transition-duration: 0.3s;
  transition-timing-function: ease;
}

@media (max-width: 768px) {
  .info-cards {
    grid-template-columns: 1fr;
  }
  
  .tabs {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .tab-btn {
    margin-bottom: 10px;
  }
  
  .bankmap-section {
    margin-top: 20px;
  }
}
</style>