<template>
  <div class="video-detail" v-if="video">
    <div class="video-player-container">
      <iframe 
        class="video-player"
        :src="`https://www.youtube.com/embed/${getVideoId()}`"
        frameborder="0"
        allowfullscreen
      ></iframe>
    </div>
    
    <div class="video-info">
      <h2 class="video-title">{{ video.snippet.title }}</h2>
      
      <div class="video-meta">
        <div class="channel-info">
          <span class="channel-name">{{ video.snippet.channelTitle }}</span>
          <button 
            @click="saveChannel(video)" 
            class="action-button"
            :disabled="!isAuthenticated"
          >
            채널 저장
          </button>
        </div>
        
        <div class="video-stats" v-if="video.statistics">
          <span>조회수 {{ formatNumber(video.statistics.viewCount) }}회</span>
          <span>좋아요 {{ formatNumber(video.statistics.likeCount) }}</span>
        </div>
      </div>
      
      <div class="video-description">
        <p>{{ video.snippet.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useYoutubeStore } from '../../stores/youtube';
import { useAlertStore } from '../../stores/alert';

const props = defineProps({
  video: {
    type: Object,
    default: null
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  }
});

const youtubeStore = useYoutubeStore();
const alertStore = useAlertStore();

// 비디오 ID 추출
const getVideoId = () => {
  if (!props.video) return '';
  return props.video.id;
};

const saveChannel = async (video) => {
  if (!props.isAuthenticated) {
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

// 숫자 포맷팅 함수
const formatNumber = (num) => {
  if (!num) return '0';
  return new Intl.NumberFormat().format(num);
};
</script>

<style scoped>
.video-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.video-player-container {
  position: relative;
  padding-bottom: 56.25%;
  height: 0;
  overflow: hidden;
  max-width: 100%;
  border-radius: 8px;
  overflow: hidden;
}

.video-player {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-title {
  margin-top: 10px;
  margin-bottom: 15px;
  font-size: 22px;
  line-height: 1.4;
  color: #333;
}

.video-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.channel-name {
  font-weight: 500;
  color: #333;
}

.video-stats {
  display: flex;
  gap: 20px;
  color: #666;
}

.video-description {
  white-space: pre-line;
  color: #444;
  line-height: 1.6;
  font-size: 15px;
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

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .video-meta {
    flex-direction: column;
    gap: 10px;
  }
}
</style>