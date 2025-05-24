<template>
  <div class="saved-items">
    <!-- 탭 네비게이션 -->
    <div class="tabs">
      <button 
        class="tab-btn" 
        :class="{ 'active': activeTab === 'videos' }"
        @click="activeTab = 'videos'"
      >
        저장한 영상
      </button>
      <button 
        class="tab-btn" 
        :class="{ 'active': activeTab === 'channels' }"
        @click="activeTab = 'channels'"
      >
        저장한 채널
      </button>
    </div>
    
    <!-- 저장한 영상 목록 -->
    <div v-if="activeTab === 'videos'" class="tab-content">
      <div v-if="savedVideos.length === 0" class="empty-state">
        저장한 영상이 없습니다.
      </div>
      <div v-else class="video-grid">
        <div v-for="video in savedVideos" :key="getVideoId(video)" class="video-card">
          <div class="video-thumbnail" @click="selectVideo(video)">
            <img 
              v-if="hasThumbnail(video)" 
              :src="getThumbnailUrl(video)" 
              :alt="getVideoTitle(video)"
            >
            <div v-else class="no-thumbnail">
              <i class="fas fa-video"></i>
            </div>
          </div>
          <div class="video-info">
            <h3 class="video-title" @click="selectVideo(video)">{{ getVideoTitle(video) }}</h3>
            <p class="channel-title">{{ getChannelTitle(video) }}</p>
          </div>
          <button class="remove-btn" @click="removeVideo(getVideoId(video))">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 저장한 채널 목록 -->
    <div v-if="activeTab === 'channels'" class="tab-content">
      <div v-if="savedChannels.length === 0" class="empty-state">
        저장한 채널이 없습니다.
      </div>
      <div v-else class="channel-grid">
        <div v-for="channel in savedChannels" :key="channel.id" class="channel-card">
          <div class="channel-info">
            <h3 class="channel-title">{{ channel.title }}</h3>
          </div>
          <div class="channel-actions">
            <a 
              :href="`https://www.youtube.com/channel/${channel.id}`" 
              target="_blank" 
              rel="noopener noreferrer"
              class="visit-btn"
            >
              <i class="fas fa-external-link-alt"></i> 채널 방문
            </a>
            <button class="remove-btn" @click="removeChannel(channel.id)">
              <i class="fas fa-trash"></i>
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
import { useAlertStore } from '../../stores/alert';

const youtubeStore = useYoutubeStore();
const alertStore = useAlertStore();
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
    window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank');
  }
};

// 영상 삭제
const removeVideo = async (videoId) => {
  if (videoId === 'unknown') {
    alertStore.showError("삭제 실패", "삭제할 영상 ID를 찾을 수 없습니다");
    return;
  }
  
  if (confirm('정말로 이 영상을 삭제하시겠습니까?')) {
    const result = await youtubeStore.removeVideo(videoId);
    if (result.success) {
      alertStore.showSuccess('삭제 완료', result.message);
    } else {
      alertStore.showError('삭제 실패', result.message);
    }
  }
};

// 채널 삭제
const removeChannel = async (channelId) => {
  if (confirm('정말로 이 채널을 삭제하시겠습니까?')) {
    const result = await youtubeStore.removeChannel(channelId);
    if (result.success) {
      alertStore.showSuccess('삭제 완료', result.message);
    } else {
      alertStore.showError('삭제 실패', result.message);
    }
  }
};

onMounted(() => {
  // 컴포넌트 마운트 시 저장된 영상 및 채널 로드
  youtubeStore.initialize();
});
</script>

<style scoped>
.saved-items {
  margin-top: 10px;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #555;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.tab-btn.active {
  color: #4a90e2;
  border-bottom-color: #4a90e2;
  font-weight: 500;
}

.tab-btn:hover {
  color: #4a90e2;
}

.tab-content {
  margin-top: 20px;
}

.empty-state {
  text-align: center;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  color: #666;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.video-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: white;
  position: relative;
}

.video-thumbnail {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9 비율 */
  overflow: hidden;
  cursor: pointer;
}

.video-thumbnail img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.video-thumbnail:hover img {
  transform: scale(1.05);
}

.no-thumbnail {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #eee;
}

.no-thumbnail i {
  font-size: 40px;
  color: #999;
}

.video-info {
  padding: 15px;
}

.video-title {
  font-size: 16px;
  margin: 0 0 5px;
  line-height: 1.4;
  font-weight: 500;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  cursor: pointer;
}

.video-title:hover {
  color: #4a90e2;
}

.channel-title {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.remove-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.remove-btn:hover {
  opacity: 1;
}

/* 채널 카드 스타일링 */
.channel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.channel-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  background-color: white;
  display: flex;
  flex-direction: column;
}

.channel-info {
  margin-bottom: 15px;
}

.channel-title {
  font-size: 18px;
  margin: 0;
  color: #333;
}

.channel-actions {
  display: flex;
  justify-content: space-between;
  margin-top: auto;
}

.visit-btn {
  padding: 8px 15px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  transition: background-color 0.3s;
}

.visit-btn:hover {
  background-color: #3a7bc8;
}

.channel-card .remove-btn {
  position: relative;
  top: 0;
  right: 0;
  margin-left: 10px;
  background-color: #dc3545;
}
</style>