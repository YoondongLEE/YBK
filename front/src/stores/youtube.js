import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useYoutubeStore = defineStore('youtube', () => {
  const videos = ref([])
  const selectedVideo = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const savedVideos = ref([])
  const savedChannels = ref([])
  
  // 검색어로 영상 검색
  async function searchVideos(query) {
    if (!query) return
    
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get('https://www.googleapis.com/youtube/v3/search', {
        params: {
          part: 'snippet',
          maxResults: 10,
          q: query + ' 주식 투자 금융',
          type: 'video',
          key: import.meta.env.VITE_API_KEY
        }
      })
      
      videos.value = response.data.items
      return response.data.items
    } catch (err) {
      console.error('비디오 검색 중 오류가 발생했습니다:', err)
      error.value = '영상을 검색하는 동안 오류가 발생했습니다.'
      return []
    } finally {
      loading.value = false
    }
  }
  
  // 영상 상세 정보 가져오기
  async function getVideoDetails(videoId) {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get('https://www.googleapis.com/youtube/v3/videos', {
        params: {
          part: 'snippet,statistics',
          id: videoId,
          key: import.meta.env.VITE_API_KEY
        }
      })
      
      if (response.data.items.length > 0) {
        selectedVideo.value = response.data.items[0]
        return response.data.items[0]
      } else {
        error.value = '해당 영상을 찾을 수 없습니다.'
        return null
      }
    } catch (err) {
      console.error('비디오 상세정보 가져오는 중 오류가 발생했습니다:', err)
      error.value = '영상 상세정보를 불러오는 중 오류가 발생했습니다.'
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 영상 저장하기
  function saveVideo(video) {
    // 이미 저장된 영상인지 확인
    const exists = savedVideos.value.some(v => v.id.videoId === video.id.videoId)
    
    if (!exists) {
      savedVideos.value.push(video)
      // 로컬 스토리지에 저장
      localStorage.setItem('savedVideos', JSON.stringify(savedVideos.value))
    }
  }
  
  // 채널 저장하기
  function saveChannel(video) {
    const channelId = video.snippet.channelId
    const channelTitle = video.snippet.channelTitle
    
    // 이미 저장된 채널인지 확인
    const exists = savedChannels.value.some(c => c.id === channelId)
    
    if (!exists) {
      savedChannels.value.push({
        id: channelId,
        title: channelTitle
      })
      // 로컬 스토리지에 저장
      localStorage.setItem('savedChannels', JSON.stringify(savedChannels.value))
    }
  }
  
  // 저장된 데이터 초기화 (로컬 스토리지에서 불러오기)
  function initializeStore() {
    const storedVideos = localStorage.getItem('savedVideos')
    const storedChannels = localStorage.getItem('savedChannels')
    
    if (storedVideos) {
      savedVideos.value = JSON.parse(storedVideos)
    }
    
    if (storedChannels) {
      savedChannels.value = JSON.parse(storedChannels)
    }
  }
  
  return { 
    videos, 
    selectedVideo, 
    loading, 
    error, 
    savedVideos, 
    savedChannels, 
    searchVideos, 
    getVideoDetails, 
    saveVideo, 
    saveChannel, 
    initializeStore 
  }
}, {
  persist: true
})