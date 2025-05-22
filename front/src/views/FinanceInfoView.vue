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
        <!-- 저장된 항목 탭 제거 -->
      </div>
      
      <!-- 금융 정보 탭 -->
      <div v-if="activeTab === 'info'" class="info-section">
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
      
      <!-- YouTube 검색 탭 -->
      <div v-if="activeTab === 'youtube'" class="youtube-section">
        <VideoSearch />
        <VideoDetail v-if="selectedVideo" :video="selectedVideo" />
      </div>
      
      <!-- 저장된 항목 탭 제거 -->
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import VideoSearch from '../components/youtube/VideoSearch.vue';
import VideoDetail from '../components/youtube/VideoDetail.vue';
// import SavedItems from '../components/youtube/SavedItems.vue'; // 제거
import { useYoutubeStore } from '../stores/youtube';

const activeTab = ref('info');
const youtubeStore = useYoutubeStore();

const selectedVideo = computed(() => youtubeStore.selectedVideo);

function setActiveTab(tab) {
  activeTab.value = tab;
}
</script>

<style scoped>
.finance-info-container {
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

.info-tabs {
  display: flex;
  margin-bottom: 30px;
  border-bottom: 1px solid #e0e0e0;
}

.info-tabs button {
  padding: 10px 20px;
  background-color: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  margin-right: 20px;
  font-size: 16px;
}

.info-tabs button.active {
  border-bottom: 3px solid #4a90e2;
  color: #4a90e2;
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

.youtube-section {
  margin-top: 20px;
}
</style>