<!-- filepath: c:\Users\SSAFY\LYD\final-pjt\front\src\components\youtube\VideoDetail.vue -->
<template>
  <div v-if="video" class="video-detail">
    <div class="video-player">
      <iframe 
        :src="'https://www.youtube.com/embed/' + video.id" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen
      ></iframe>
    </div>
    <div class="video-info">
      <h2>{{ video.snippet.title }}</h2>
      <div class="channel-info">
        <strong>{{ video.snippet.channelTitle }}</strong>
        <button @click="saveChannel(video)" class="save-channel-btn">채널 저장</button>
      </div>
      <div class="stats">
        <span>조회수: {{ formatNumber(video.statistics.viewCount) }}</span>
        <span>좋아요: {{ formatNumber(video.statistics.likeCount) }}</span>
      </div>
      <div class="description">
        <p>{{ video.snippet.description }}</p>
      </div>
    </div>
  </div>
  <div v-else class="no-video">
    <p>선택된 영상이 없습니다.</p>
  </div>
</template>

<script setup>
import { useYoutubeStore } from '../../stores/youtube';

const props = defineProps({
  video: {
    type: Object,
    default: null
  }
});

const youtubeStore = useYoutubeStore();

const saveChannel = (video) => {
  youtubeStore.saveChannel(video);
  alert('채널이 저장되었습니다!');
};

// 숫자 포맷팅 함수
const formatNumber = (num) => {
  if (!num) return '0';
  return new Intl.NumberFormat().format(num);
};
</script>

<style scoped>
.video-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.video-player {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 비율 */
  height: 0;
  overflow: hidden;
  margin-bottom: 20px;
}

.video-player iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-info {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

h2 {
  margin-bottom: 15px;
}

.channel-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.save-channel-btn {
  padding: 8px 15px;
  background-color: #34a853;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  color: #666;
}

.description {
  white-space: pre-line;
  color: #333;
  line-height: 1.5;
}

.no-video {
  text-align: center;
  padding: 50px;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #666;
}
</style>