<template>
  <div class="video-search">
    <h2>관심 종목 영상 검색</h2>
    <div class="search-container">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="관심 종목 또는 금융 키워드를 입력하세요" 
        @keyup.enter="searchVideos"
      />
      <button @click="searchVideos">검색</button>
    </div>
    
    <div v-if="loading" class="loading">
      <p>검색 중...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="videos.length === 0 && searched" class="no-results">
      <p>검색 결과가 없습니다.</p>
    </div>
    
    <div v-else class="video-list">
      <div 
        v-for="video in videos" 
        :key="video.id.videoId"
        class="video-item"
        @click="selectVideo(video)"
      >
        <img 
          :src="video.snippet.thumbnails.medium.url" 
          :alt="video.snippet.title" 
          class="thumbnail"
        />
        <div class="video-info">
          <h3>{{ video.snippet.title }}</h3>
          <p>{{ video.snippet.channelTitle }}</p>
          
          <!-- 로그인한 경우에만 저장 버튼 표시 -->
          <div v-if="isAuthenticated" class="action-buttons">
            <button @click.stop="saveVideo(video)" class="save-btn">영상 저장</button>
            <button @click.stop="saveChannel(video)" class="save-channel-btn">채널 저장</button>
          </div>
          <p v-else class="login-info">
            저장 기능을 사용하려면 <router-link to="/login">로그인</router-link>이 필요합니다.
          </p>
        </div>
      </div>
    </div>
    
    <!-- 선택한 영상 상세 정보 -->
    <div v-if="selectedVideo" class="video-detail-container">
      <VideoDetail :video="selectedVideo" :isAuthenticated="isAuthenticated" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useYoutubeStore } from '../../stores/youtube';
import { useAuthStore } from '../../stores/auth';
import VideoDetail from './VideoDetail.vue';

const youtubeStore = useYoutubeStore();
const authStore = useAuthStore();
const searchQuery = ref('');
const searched = ref(false);

// 스토어에서 상태 가져오기
const videos = computed(() => youtubeStore.videos);
const loading = computed(() => youtubeStore.loading);
const error = computed(() => youtubeStore.error);
const selectedVideo = computed(() => youtubeStore.selectedVideo);
const isAuthenticated = computed(() => authStore.isAuthenticated);

// 영상 검색
const searchVideos = async () => {
  if (searchQuery.value.trim()) {
    searched.value = true;
    await youtubeStore.searchVideos(searchQuery.value);
  }
};

// 영상 선택
const selectVideo = (video) => {
  youtubeStore.getVideoDetails(video.id.videoId);
};

// 영상 저장
const saveVideo = (video) => {
  youtubeStore.saveVideo(video);
  alert('영상이 저장되었습니다! 마이페이지에서 확인하세요.');
};

// 채널 저장
const saveChannel = (video) => {
  youtubeStore.saveChannel(video);
  alert('채널이 저장되었습니다! 마이페이지에서 확인하세요.');
};
</script>

<style scoped>
.video-search {
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 20px;
}

.search-container {
  display: flex;
  margin-bottom: 20px;
}

input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
}

button {
  padding: 10px 20px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

button:hover {
  background-color: #3a7bd5;
}

.loading, .error, .no-results {
  text-align: center;
  padding: 20px;
}

.error {
  color: red;
}

.video-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.video-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  background-color: white;
}

.video-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.thumbnail {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.video-info {
  padding: 15px;
}

.video-info h3 {
  margin: 0 0 10px;
  font-size: 16px;
  line-height: 1.4;
  max-height: 44px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.video-info p {
  margin: 0 0 10px;
  font-size: 14px;
  color: #666;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.save-btn, .save-channel-btn {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 4px;
}

.save-btn {
  background-color: #4a90e2;
}

.save-channel-btn {
  background-color: #34a853;
}

.login-info {
  font-size: 13px;
  color: #666;
  margin-top: 10px;
}

.login-info a {
  color: #4a90e2;
  text-decoration: underline;
}

.video-detail-container {
  margin-top: 40px;
}
</style>