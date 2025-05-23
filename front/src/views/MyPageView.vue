<template>
  <div class="mypage-container">
    <h1>마이페이지</h1>
    
    <div v-if="isLoading" class="loading">
      로딩 중...
    </div>
    
    <div v-else-if="!isAuthenticated" class="not-authenticated">
      <p>마이페이지를 이용하시려면 <router-link to="/login">로그인</router-link>이 필요합니다.</p>
    </div>
    
    <div v-else>
      <div class="profile-section">
        <h2>내 정보</h2>
        <div class="info-item">
          <strong>아이디:</strong> {{ userInfo.username }}
        </div>
        <div class="info-item">
          <strong>이메일:</strong> {{ userInfo.email }}
        </div>
      </div>
      
      <div class="subscriptions-section">
        <h2>가입한 정기예금 상품</h2>
        
        <div v-if="!userInfo.subscribed_deposits?.length" class="no-data">
          가입한 예금 상품이 없습니다.
        </div>
        
        <div v-else class="deposit-cards">
          <div 
            v-for="deposit in userInfo.subscribed_deposits" 
            :key="deposit.id" 
            class="deposit-card"
            @click="goToDepositDetail(deposit.id)"
          >
            <div class="card-header">
              <div class="bank-name">{{ deposit.bank.kor_co_nm }}</div>
              <div class="product-name">{{ deposit.fin_prdt_nm }}</div>
            </div>
            <div class="card-body">
              <div class="rate">최대 {{ deposit.max_rate }}%</div>
              <div class="join-method">
                <strong>가입방법:</strong> {{ deposit.join_way }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 저장된 영상/채널 섹션 -->
      <div class="youtube-saved-section">
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
              <div class="thumbnail-container" @click="watchVideo(video)">
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
    </div>

    <!-- 영상 모달 -->
    <div v-if="showVideoModal && selectedVideo" class="video-modal">
      <div class="modal-content">
        <button @click="closeModal" class="close-btn">&times;</button>
        <div class="video-player">
          <iframe 
            :src="'https://www.youtube.com/embed/' + getVideoId(selectedVideo)" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen
          ></iframe>
        </div>
        <div class="video-info">
          <h3>{{ getVideoTitle(selectedVideo) }}</h3>
          <p>{{ getChannelTitle(selectedVideo) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useYoutubeStore } from '../stores/youtube';
import api from '../api';

const router = useRouter();
const authStore = useAuthStore();
const youtubeStore = useYoutubeStore();

const userInfo = ref({});
const isLoading = ref(true);
const activeTab = ref('videos');
const showVideoModal = ref(false);
const selectedVideo = ref(null);

// 인증 상태 확인
const isAuthenticated = computed(() => authStore.isAuthenticated);

// 저장된 영상과 채널 가져오기
const savedVideos = computed(() => youtubeStore.savedVideos);
const savedChannels = computed(() => youtubeStore.savedChannels);

const fetchUserProfile = async () => {
  try {
    isLoading.value = true;
    // 사용자 프로필 정보 가져오기 (가입한 상품 정보 포함)
    const response = await api.get('/accounts/profile/');
    
    console.log('사용자 프로필 정보:', response.data);
    userInfo.value = response.data;
  } catch (e) {
    console.error('프로필 로드 실패:', e);
    if (e.response && e.response.status === 401) {
      // 로그인 페이지로 리다이렉트
      router.push({ name: 'login' });
    }
  } finally {
    isLoading.value = false;
  }
};

const goToDepositDetail = (id) => {
  router.push({ name: 'depositDetail', params: { id } });
};

// 영상 ID 가져오기
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

// 영상 보기 (모달에 표시)
const watchVideo = (video) => {
  selectedVideo.value = video;
  showVideoModal.value = true;
};

// 모달 닫기
const closeModal = () => {
  showVideoModal.value = false;
  selectedVideo.value = null;
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

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchUserProfile();
    cleanupSavedData(); // 저장된 데이터 정리
  } else {
    // 로그인 상태가 아니라면 로딩 완료
    isLoading.value = false;
  }
});
</script>

<style scoped>
.mypage-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

h2 {
  color: #4a90e2;
  margin: 30px 0 15px;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

h3 {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.loading, .not-authenticated {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
}

.not-authenticated a {
  color: #4a90e2;
  text-decoration: underline;
}

.profile-section {
  background-color: #f5f8ff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.info-item {
  margin-bottom: 10px;
}

.info-item strong {
  display: inline-block;
  width: 100px;
}

.subscriptions-section {
  margin-top: 30px;
}

.deposit-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.deposit-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.deposit-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px;
  background-color: #f5f8ff;
  border-bottom: 1px solid #e0e0e0;
}

.bank-name {
  font-size: 14px;
  color: #666;
}

.product-name {
  font-size: 18px;
  font-weight: bold;
  margin-top: 5px;
}

.card-body {
  padding: 15px;
}

.rate {
  font-size: 20px;
  color: #ff5722;
  font-weight: bold;
  margin-bottom: 10px;
}

.join-method {
  font-size: 14px;
  color: #666;
}

.youtube-saved-section {
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

.empty-message {
  text-align: center;
  padding: 30px;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #606060;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
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

/* 비디오 모달 스타일 */
.video-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 800px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: white;
  z-index: 10;
}

.video-player {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 비율 */
  height: 0;
}

.video-player iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-info {
  padding: 15px;
}

.no-data {
  text-align: center;
  padding: 40px;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #606060;
  margin-top: 20px;
}
</style>