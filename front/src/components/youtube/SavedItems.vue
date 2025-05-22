<!-- filepath: c:\Users\SSAFY\LYD\final-pjt\front\src\components\youtube\SavedItems.vue -->
<template>
  <div class="saved-items">
    <div class="tabs">
      <button 
        :class="{ 'active': activeTab === 'videos' }"
        @click="activeTab = 'videos'"
      >
        저장된 영상
      </button>
      <button 
        :class="{ 'active': activeTab === 'channels' }"
        @click="activeTab = 'channels'"
      >
        저장된 채널
      </button>
    </div>
    
    <div v-if="activeTab === 'videos'" class="saved-videos">
      <h3>저장된 영상</h3>
      <div v-if="savedVideos.length === 0" class="empty-message">
        <p>저장된 영상이 없습니다.</p>
      </div>
      <div v-else class="video-grid">
        <div 
          v-for="video in savedVideos" 
          :key="video.id.videoId"
          class="saved-video-item"
          @click="selectVideo(video)"
        >
          <img 
            :src="video.snippet.thumbnails.medium.url" 
            :alt="video.snippet.title" 
            class="thumbnail"
          />
          <div class="video-info">
            <h4>{{ video.snippet.title }}</h4>
            <p>{{ video.snippet.channelTitle }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="activeTab === 'channels'" class="saved-channels">
      <h3>저장된 채널</h3>
      <div v-if="savedChannels.length === 0" class="empty-message">
        <p>저장된 채널이 없습니다.</p>
      </div>
      <div v-else class="channel-list">
        <div 
          v-for="channel in savedChannels" 
          :key="channel.id"
          class="channel-item"
        >
          <h4>{{ channel.title }}</h4>
          <a 
            :href="`https://www.youtube.com/channel/${channel.id}`" 
            target="_blank"
            class="channel-link"
          >
            채널 방문하기
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useYoutubeStore } from '../../stores/youtube';

const youtubeStore = useYoutubeStore();
const activeTab = ref('videos');

const savedVideos = computed(() => youtubeStore.savedVideos);
const savedChannels = computed(() => youtubeStore.savedChannels);

onMounted(() => {
  youtubeStore.initializeStore();
});

const selectVideo = (video) => {
  youtubeStore.getVideoDetails(video.id.videoId);
  // 상세 페이지로 이동할 수도 있음
};
</script>

<style scoped>
.saved-items {
  margin-top: 30px;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 20px;
  background-color: #f0f0f0;
  border: none;
  cursor: pointer;
  flex: 1;
}

.tabs button.active {
  background-color: #4a90e2;
  color: white;
}

h3 {
  margin-bottom: 20px;
}

.empty-message {
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.saved-video-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s;
}

.saved-video-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.thumbnail {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.video-info {
  padding: 10px;
}

h4 {
  margin-bottom: 5px;
  font-size: 14px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.channel-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.channel-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
}

.channel-link {
  margin-top: 10px;
  padding: 8px;
  background-color: #4a90e2;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  text-align: center;
}
</style>