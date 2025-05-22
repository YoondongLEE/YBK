<!-- filepath: c:\Users\SSAFY\LYD\final-pjt\front\src\components\youtube\VideoSearch.vue -->
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
          <div class="action-buttons">
            <button @click.stop="saveVideo(video)" class="save-btn">영상 저장</button>
            <button @click.stop="saveChannel(video)" class="save-channel-btn">채널 저장</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useYoutubeStore } from '../../stores/youtube';

const youtubeStore = useYoutubeStore();
const searchQuery = ref('');
const searched = ref(false);

// 스토어에서 상태 가져오기
const videos = computed(() => youtubeStore.videos);
const loading = computed(() => youtubeStore.loading);
const error = computed(() => youtubeStore.error);

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
  // 상세 페이지로 이동할 수도 있음
};

// 영상 저장
const saveVideo = (video) => {
  youtubeStore.saveVideo(video);
  alert('영상이 저장되었습니다!');
};

// 채널 저장
const saveChannel = (video) => {
  youtubeStore.saveChannel(video);
  alert('채널이 저장되었습니다!');
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
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s;
  cursor: pointer;
}

.video-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.thumbnail {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.video-info {
  padding: 15px;
}

h3 {
  margin-bottom: 10px;
  font-size: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.save-btn, .save-channel-btn {
  padding: 8px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.save-channel-btn {
  background-color: #34a853;
}
</style>