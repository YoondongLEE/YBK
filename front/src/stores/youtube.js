import { defineStore } from 'pinia'
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from './auth'
import api from '../api'

export const useYoutubeStore = defineStore('youtube', () => {
  // 상태 정의
  const videos = ref([])
  const selectedVideo = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const savedVideos = ref([])
  const savedChannels = ref([])
  
  const authStore = useAuthStore()

  // 초기화 함수 - 저장된 비디오와 채널 불러오기
  async function initialize() {
    try {
      // 로그인 상태일 때만 서버에서 데이터 가져오기
      if (authStore.isAuthenticated) {
        await fetchSavedVideos()
        await fetchSavedChannels()
      } else {
        // 로그인 상태가 아니면 빈 배열로 초기화
        savedVideos.value = []
        savedChannels.value = []
      }
    } catch (err) {
      console.error('저장된 데이터를 불러오는 중 오류 발생:', err)
      savedVideos.value = []
      savedChannels.value = []
    }
  }
  
  // 서버에서 저장된 영상 가져오기
  async function fetchSavedVideos() {
    try {
      const response = await api.get('/accounts/youtube/videos/')
      savedVideos.value = response.data || []
    } catch (error) {
      console.error('저장된 영상을 불러오는 중 오류 발생:', error)
      savedVideos.value = []
    }
  }
  
  // 서버에서 저장된 채널 가져오기
  async function fetchSavedChannels() {
    try {
      const response = await api.get('/accounts/youtube/channels/')
      savedChannels.value = response.data || []
    } catch (error) {
      console.error('저장된 채널을 불러오는 중 오류 발생:', error)
      savedChannels.value = []
    }
  }
  
  // 검색어로 영상 검색 (기존 함수 유지)
  async function searchVideos(query) {
    if (!query) return
    
    loading.value = true
    error.value = null
    
    try {
      const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY
      
      if (!API_KEY) {
        throw new Error('YouTube API 키가 설정되지 않았습니다.')
      }
      
      const response = await axios.get('https://www.googleapis.com/youtube/v3/search', {
        params: {
          part: 'snippet',
          maxResults: 10,
          q: query + ' 주식 투자 금융',
          type: 'video',
          key: API_KEY
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
  
  // 영상 상세 정보 가져오기 (기존 함수 유지)
  async function getVideoDetails(videoId) {
    if (!videoId) return null
    
    loading.value = true
    error.value = null
    
    try {
      const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY
      
      if (!API_KEY) {
        throw new Error('YouTube API 키가 설정되지 않았습니다.')
      }
      
      const response = await axios.get('https://www.googleapis.com/youtube/v3/videos', {
        params: {
          part: 'snippet,statistics',
          id: videoId,
          key: API_KEY
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
  
  // 영상 저장하기 (서버 API 사용)
  async function saveVideo(video) {
    if (!video || !video.snippet) {
      console.error('유효하지 않은 비디오 데이터입니다:', video)
      return { success: false, message: '유효하지 않은 영상 데이터입니다.' }
    }
    
    // 로그인 상태 확인
    if (!authStore.isAuthenticated) {
      return { success: false, message: '영상 저장을 위해 로그인이 필요합니다.' }
    }
    
    try {
      const response = await api.post('/accounts/youtube/videos/', video)
      
      // 저장 성공 시 로컬 상태 업데이트
      if (response.status === 201) {
        await fetchSavedVideos() // 서버에서 최신 목록 다시 가져오기
        return { success: true, message: '영상이 저장되었습니다!' }
      } else {
        return { success: true, message: response.data.message }
      }
    } catch (error) {
      console.error('영상 저장 중 오류 발생:', error)
      return { 
        success: false, 
        message: error.response?.data?.error || '영상을 저장하는 중 오류가 발생했습니다.' 
      }
    }
  }
  
  // 채널 저장하기 (서버 API 사용)
  async function saveChannel(video) {
    if (!video || !video.snippet || !video.snippet.channelId || !video.snippet.channelTitle) {
      console.error('유효하지 않은 채널 데이터입니다:', video)
      return { success: false, message: '유효하지 않은 채널 데이터입니다.' }
    }
    
    // 로그인 상태 확인
    if (!authStore.isAuthenticated) {
      return { success: false, message: '채널 저장을 위해 로그인이 필요합니다.' }
    }
    
    const channelId = video.snippet.channelId
    const channelTitle = video.snippet.channelTitle
    
    try {
      const response = await api.post('/accounts/youtube/channels/', {
        id: channelId,
        title: channelTitle,
        snippet: video.snippet
      })
      
      // 저장 성공 시 로컬 상태 업데이트
      if (response.status === 201) {
        await fetchSavedChannels() // 서버에서 최신 목록 다시 가져오기
        return { success: true, message: '채널이 저장되었습니다!' }
      } else {
        return { success: true, message: response.data.message }
      }
    } catch (error) {
      console.error('채널 저장 중 오류 발생:', error)
      return { 
        success: false, 
        message: error.response?.data?.error || '채널을 저장하는 중 오류가 발생했습니다.' 
      }
    }
  }
  
  // 영상 삭제하기 (서버 API 사용)
  async function removeVideo(videoId) {
    if (!videoId) return { success: false, message: '영상 ID가 필요합니다.' }
    
    // 로그인 상태 확인
    if (!authStore.isAuthenticated) {
      return { success: false, message: '로그인이 필요합니다.' }
    }
    
    try {
      await api.delete(`/accounts/youtube/videos/${videoId}/`)
      await fetchSavedVideos() // 서버에서 최신 목록 다시 가져오기
      return { success: true, message: '영상이 삭제되었습니다.' }
    } catch (error) {
      console.error('영상 삭제 중 오류 발생:', error)
      return { 
        success: false, 
        message: error.response?.data?.error || '영상을 삭제하는 중 오류가 발생했습니다.' 
      }
    }
  }
  
  // 채널 삭제하기 (서버 API 사용)
  async function removeChannel(channelId) {
    if (!channelId) return { success: false, message: '채널 ID가 필요합니다.' }
    
    // 로그인 상태 확인
    if (!authStore.isAuthenticated) {
      return { success: false, message: '로그인이 필요합니다.' }
    }
    
    try {
      await api.delete(`/accounts/youtube/channels/${channelId}/`)
      await fetchSavedChannels() // 서버에서 최신 목록 다시 가져오기
      return { success: true, message: '채널이 삭제되었습니다.' }
    } catch (error) {
      console.error('채널 삭제 중 오류 발생:', error)
      return { 
        success: false, 
        message: error.response?.data?.error || '채널을 삭제하는 중 오류가 발생했습니다.' 
      }
    }
  }
  
  // 저장 데이터 초기화 (로컬 상태만)
  function resetSavedData() {
    savedVideos.value = []
    savedChannels.value = []
  }
  
  // 인증 상태 변경 감시 (로그인/로그아웃 시 데이터 초기화)
  function refreshOnAuthChange() {
    if (authStore.isAuthenticated) {
      initialize()
    } else {
      resetSavedData()
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
    removeVideo,
    removeChannel,
    resetSavedData,
    initialize,
    refreshOnAuthChange
  }
})