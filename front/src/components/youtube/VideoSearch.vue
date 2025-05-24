<template>
  <div class="video-search-container">
    <div class="search-form">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="금융 관련 강의, 뉴스 검색..."
        @keyup.enter="performSearch"
      />
      <button @click="performSearch" class="search-button">검색</button>
    </div>
    
    <div class="search-results-container">
      <div v-if="loading" class="loading">검색 중...</div>
      
      <div v-else-if="error" class="error-message">{{ error }}</div>
      
      <div v-else-if="selectedVideo" class="video-detail-container">
        <VideoDetail :video="selectedVideo" :isAuthenticated="isAuthenticated" />
      </div>
      
      <div v-else-if="videos.length" class="video-list">
        <div v-for="video in videos" :key="video.id.videoId" class="video-item">
          <div class="video-thumbnail" @click="selectVideo(video)">
            <img :src="video.snippet.thumbnails.medium.url" :alt="video.snippet.title">
          </div>
          <div class="video-info">
            <h3 @click="selectVideo(video)">{{ video.snippet.title }}</h3>
            <p>{{ video.snippet.channelTitle }}</p>
            <div class="video-actions">
              <button @click="saveVideo(video)" class="action-button">
                영상 저장
              </button>
              <button @click="saveChannel(video)" class="action-button">
                채널 저장
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="no-results">
        <p>검색 결과가 없습니다. 다른 키워드로 검색해보세요.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useYoutubeStore } from '../../stores/youtube';
import { useAuthStore } from '../../stores/auth';
import { useAlertStore } from '../../stores/alert';
import VideoDetail from './VideoDetail.vue';

const youtubeStore = useYoutubeStore();
const authStore = useAuthStore();
const alertStore = useAlertStore();

const searchQuery = ref('');
const isAuthenticated = computed(() => authStore.isAuthenticated);
const videos = computed(() => youtubeStore.videos);
const selectedVideo = computed(() => youtubeStore.selectedVideo);
const loading = computed(() => youtubeStore.loading);
const error = computed(() => youtubeStore.error);

// 검색 실행
const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    alertStore.showWarning('검색어 필요', '검색어를 입력하세요.');
    return;
  }
  await youtubeStore.searchVideos(searchQuery.value);
};

// 영상 선택
const selectVideo = (video) => {
  youtubeStore.getVideoDetails(video.id.videoId);
};

// 영상 저장
const saveVideo = async (video) => {
  if (!isAuthenticated.value) {
    alertStore.showWarning('로그인 필요', '영상을 저장하려면 로그인이 필요합니다.');
    return;
  }
  
  const result = await youtubeStore.saveVideo(video);
  if (result.success) {
    alertStore.showSuccess('저장 완료', result.message);
  } else {
    alertStore.showError('저장 실패', result.message);
  }
};

// 채널 저장
const saveChannel = async (video) => {
  if (!isAuthenticated.value) {
    alertStore.showWarning('로그인 필요', '채널을 저장하려면 로그인이 필요합니다.');
    return;
  }
  
  const result = await youtubeStore.saveChannel(video);
  if (result.success) {
    alertStore.showSuccess('저장 완료', result.message);
  } else {
    alertStore.showError('저장 실패', result.message);
  }
};
</script>

<style scoped>
.video-search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-form input {
  flex: 1;
  padding: 12px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 4px;
}

.search-button {
  padding: 0 20px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.search-button:hover {
  background-color: #3a7bc8;
}

.loading {
  text-align: center;
  padding: 50px;
  font-size: 18px;
  color: #666;
}

.error-message {
  text-align: center;
  padding: 30px;
  color: #e74c3c;
}

.video-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.video-item {
  display: flex;
  gap: 15px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.video-thumbnail {
  flex: 0 0 200px;
  cursor: pointer;
}

.video-thumbnail img {
  width: 100%;
  border-radius: 4px;
}

.video-info {
  flex: 1;
}

.video-info h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 18px;
  cursor: pointer;
  color: #333;
}

.video-info h3:hover {
  color: #4a90e2;
}

.video-info p {
  color: #666;
  margin-bottom: 15px;
}

.video-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.action-button {
  padding: 8px 12px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  color: #333;
  font-size: 14px;
  transition: background-color 0.2s;
}

.action-button:hover {
  background-color: #e0e0e0;
}

.no-results {
  text-align: center;
  padding: 50px 20px;
  color: #666;
}

/* 반응형 스타일 */
@media (max-width: 768px) {
  .video-item {
    flex-direction: column;
  }
  
  .video-thumbnail {
    flex: 0 0 auto;
    width: 100%;
  }
}
</style>