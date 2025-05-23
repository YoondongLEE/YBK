import { defineStore } from 'pinia'
import { ref, onMounted } from 'vue'
import axios from 'axios'

export const useYoutubeStore = defineStore('youtube', () => {
  // 상태 정의
  const videos = ref([])
  const selectedVideo = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const savedVideos = ref([])
  const savedChannels = ref([])

  // 초기화 함수 - 저장된 비디오와 채널 불러오기
  onMounted(() => {
    try {
      const savedVideosData = localStorage.getItem('savedVideos')
      const savedChannelsData = localStorage.getItem('savedChannels')
      
      if (savedVideosData) {
        const parsedVideos = JSON.parse(savedVideosData)
        // 유효한 형식의 비디오만 필터링
        savedVideos.value = parsedVideos.filter(video => 
          video && video.snippet && typeof video.snippet === 'object'
        )
        // 필터링 결과가 다르면 로컬스토리지 업데이트
        if (savedVideos.value.length !== parsedVideos.length) {
          localStorage.setItem('savedVideos', JSON.stringify(savedVideos.value))
        }
      }
      
      if (savedChannelsData) {
        savedChannels.value = JSON.parse(savedChannelsData)
      }
    } catch (err) {
      console.error('저장된 데이터를 불러오는 중 오류 발생:', err)
      // 오류 발생 시 초기화
      savedVideos.value = []
      savedChannels.value = []
      localStorage.removeItem('savedVideos')
      localStorage.removeItem('savedChannels')
    }
  })
  
  // 검색어로 영상 검색
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
  
  // 영상 상세 정보 가져오기
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
  
  // 영상 저장하기
  function saveVideo(video) {
    if (!video || !video.snippet) {
      console.error('유효하지 않은 비디오 데이터입니다:', video)
      return
    }
    
    // 이미 저장된 영상인지 확인
    const exists = savedVideos.value.some(v => {
      if (v.id && v.id.videoId && video.id && video.id.videoId) {
        return v.id.videoId === video.id.videoId
      }
      if (typeof v.id === 'string' && typeof video.id === 'string') {
        return v.id === video.id
      }
      return false
    })
    
    if (!exists) {
      savedVideos.value.push(video)
      // 로컬 스토리지에 저장
      localStorage.setItem('savedVideos', JSON.stringify(savedVideos.value))
    }
  }
  
  // 채널 저장하기
  function saveChannel(video) {
    if (!video || !video.snippet || !video.snippet.channelId || !video.snippet.channelTitle) {
      console.error('유효하지 않은 채널 데이터입니다:', video)
      return
    }
    
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
  
  // 영상 삭제하기
  function removeVideo(videoId) {
    if (!videoId) return
    
    savedVideos.value = savedVideos.value.filter(v => {
      if (v.id && v.id.videoId) {
        return v.id.videoId !== videoId
      }
      if (typeof v.id === 'string') {
        return v.id !== videoId
      }
      return true // 식별할 수 없는 형식은 유지
    })
    localStorage.setItem('savedVideos', JSON.stringify(savedVideos.value))
  }
  
  // 채널 삭제하기
  function removeChannel(channelId) {
    savedChannels.value = savedChannels.value.filter(c => c.id !== channelId)
    localStorage.setItem('savedChannels', JSON.stringify(savedChannels.value))
  }
  
  // 저장 데이터 초기화
  function resetSavedData() {
    savedVideos.value = []
    savedChannels.value = []
    localStorage.removeItem('savedVideos')
    localStorage.removeItem('savedChannels')
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
    resetSavedData
  }
})