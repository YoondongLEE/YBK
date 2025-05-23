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
          :key="getVideoId(video)"
          class="saved-video-item"
        >
          <!-- 안전하게 썸네일과 정보에 접근 -->
          <div class="thumbnail-container" @click="selectVideo(video)">
            <img 
              v-if="hasThumbnail(video)"
              :src="getThumbnailUrl(video)" 
              :alt="getVideoTitle(video)" 
              class="thumbnail"
            />
            <div v-else class="thumbnail-placeholder">
              <span>썸네일 없음</span>
            </div>
          </div>
          <div class="video-info">
            <h4>{{ getVideoTitle(video) }}</h4>
            <p>{{ getChannelTitle(video) }}</p>
            <button @click="removeVideo(getVideoId(video))" class="remove-btn">
              삭제
            </button>
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
          <div class="channel-info">
            <h4>{{ channel.title || '제목 없음' }}</h4>
            <a 
              :href="`https://www.youtube.com/channel/${channel.id}`" 
              target="_blank"
              class="visit-btn"
            >
              채널 방문
            </a>
            <button @click="removeChannel(channel.id)" class="remove-btn">
              삭제
            </button>
          </div>
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

// 저장된 영상과 채널 가져오기
const savedVideos = computed(() => youtubeStore.savedVideos);
const savedChannels = computed(() => youtubeStore.savedChannels);

// 영상 ID 가져오기 (안전하게 처리)
const getVideoId = (video) => {
  if (!video) return 'unknown';
  if (video.id && video.id.videoId) {
    return video.id.videoId;
  }
  if (typeof video.id === 'string') {
    return video.id;
  }
  return 'unknown-' + Math.random().toString(36).substring(2, 9);
};

// 썸네일이 있는지 확인
const hasThumbnail = (video) => {
  return video && 
         video.snippet && 
         video.snippet.thumbnails && 
         video.snippet.thumbnails.medium && 
         video.snippet.thumbnails.medium.url;
};

// 썸네일 URL 가져오기
const getThumbnailUrl = (video) => {
  if (hasThumbnail(video)) {
    return video.snippet.thumbnails.medium.url;
  }
  return '';
};

// 영상 제목 가져오기
const getVideoTitle = (video) => {
  return video && video.snippet && video.snippet.title ? 
         video.snippet.title : '제목 없음';
};

// 채널 제목 가져오기
const getChannelTitle = (video) => {
  return video && video.snippet && video.snippet.channelTitle ? 
         video.snippet.channelTitle : '채널명 없음';
};

// 영상 선택 (상세 정보 표시)
const selectVideo = (video) => {
  const videoId = getVideoId(video);
  if (videoId !== 'unknown') {
    youtubeStore.getVideoDetails(videoId);
  }
};

// 영상 삭제
const removeVideo = (videoId) => {
  if (videoId === 'unknown') {
    console.error("삭제할 영상 ID를 찾을 수 없습니다");
    return;
  }
  
  if (confirm('정말로 이 영상을 삭제하시겠습니까?')) {
    youtubeStore.removeVideo(videoId);
  }
};

// 채널 삭제
const removeChannel = (channelId) => {
  if (confirm('정말로 이 채널을 삭제하시겠습니까?')) {
    youtubeStore.removeChannel(channelId);
  }
};

// 저장된 데이터 정리 (문제가 있는 데이터 제거)
const cleanupSavedData = () => {
  if (savedVideos.value.length > 0) {
    const validVideos = savedVideos.value.filter(video => 
      video && video.snippet && typeof video.snippet === 'object'
    );
    
    if (validVideos.length !== savedVideos.value.length) {
      youtubeStore.$patch({
        savedVideos: validVideos
      });
      localStorage.setItem('savedVideos', JSON.stringify(validVideos));
    }
  }
};

// 컴포넌트 마운트 시 데이터 정리
onMounted(() => {
  cleanupSavedData();
});
</script>

<style scoped>
.saved-items {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #e0e0e0;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 20px;
  margin-right: 10px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.tabs button.active {
  background-color: #4a90e2;
  color: white;
}

h3 {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.empty-message {
  text-align: center;
  padding: 30px;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #606060;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.saved-video-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.thumbnail-container {
  height: 140px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  background-color: #f0f0f0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  color: #666;
  font-size: 14px;
}

.video-info, .channel-info {
  padding: 15px;
}

h4 {
  margin: 0 0 8px;
  font-size: 14px;
  line-height: 1.4;
  max-height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.video-info p {
  font-size: 12px;
  color: #606060;
  margin-bottom: 10px;
}

.channel-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.channel-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.visit-btn, .remove-btn {
  display: inline-block;
  padding: 6px 12px;
  font-size: 12px;
  margin-right: 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: white;
  text-decoration: none;
}

.visit-btn {
  background-color: #4a90e2;
}

.remove-btn {
  background-color: #e53935;
}
</style>