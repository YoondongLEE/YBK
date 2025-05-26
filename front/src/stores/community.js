import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';

const API_URL = 'http://localhost:8000/api/community';

export const useCommunityStore = defineStore('community', {
  state: () => ({
    posts: [],
    currentPost: null,
    loading: false,
    error: null,
  }),

  actions: {
    // 인증 헤더 생성 함수 추가
    getAuthHeaders() {
    const authStore = useAuthStore();
    const headers = {};
    
    if (authStore.token) {
      // 토큰 형식을 명확히 표시 (Bearer vs Token)
      headers['Authorization'] = `Token ${authStore.token}`;
      console.log('토큰 설정됨:', authStore.token.substring(0, 10) + '...');
    } else {
      console.log('토큰 없음!');
    }
    
    return { headers, withCredentials: true };
  },

    // 게시글 목록 가져오기
    async getPosts({ page = 1, category = '', search = '' }) {
      this.loading = true;
      try {
        let url = `${API_URL}/posts/?page=${page}`;
        if (category) url += `&category=${category}`;
        if (search) url += `&search=${search}`;

        const response = await axios.get(url, this.getAuthHeaders());
        return response.data;
      } catch (error) {
        this.error = '게시글을 불러오는 중 오류가 발생했습니다';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 게시글 상세 가져오기
    async getPostDetail(id) {
      this.loading = true;
      try {
        console.log('게시글 상세 요청 ID:', id);
        const authHeaders = this.getAuthHeaders();
        console.log('요청 헤더:', authHeaders);
        
        const response = await axios.get(`${API_URL}/posts/${id}/`, authHeaders);
        console.log('게시글 상세 응답:', response.data);
        
        this.currentPost = response.data;
        return response.data;
      } catch (error) {
        console.error('게시글 상세 요청 오류:', error.response || error);
        this.error = '게시글을 불러오는 중 오류가 발생했습니다';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 게시글 작성
    async createPost(postData) {
      this.loading = true;
      try {
        const response = await axios.post(`${API_URL}/posts/`, postData, this.getAuthHeaders());
        return response.data;
      } catch (error) {
        this.error = '게시글 작성 중 오류가 발생했습니다';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 게시글 수정
    async updatePost(id, postData) {
    this.loading = true;
    try {
      const authHeaders = this.getAuthHeaders();
      console.log('수정 요청 헤더:', JSON.stringify(authHeaders));
      console.log('수정 요청 URL:', `${API_URL}/posts/${id}/`);
      console.log('수정 데이터:', postData);
      
      const response = await axios.put(`${API_URL}/posts/${id}/`, postData, authHeaders);
      console.log('수정 응답:', response.data);
      return response.data;
    } catch (error) {
      console.error('게시글 수정 오류:', error.response?.data || error);
      this.error = '게시글 수정 중 오류가 발생했습니다';
      throw error;
    } finally {
      this.loading = false;
    }
  },

    // 게시글 삭제
    async deletePost(id) {
      this.loading = true;
      try {
        await axios.delete(`${API_URL}/posts/${id}/`, this.getAuthHeaders());
        return true;
      } catch (error) {
        this.error = '게시글 삭제 중 오류가 발생했습니다';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // --- 추가: 특정 게시글의 댓글 목록 조회 API ---
    async getComments(postId) {
      this.loading = true;
      try {
        const response = await axios.get(
          `${API_URL}/posts/${postId}/comments/`,
          this.getAuthHeaders()
        );
        return response.data;  // [{ id, content, author, created_at, is_liked }, …]
      } catch (error) {
        this.error = '댓글 목록을 불러오는 중 오류가 발생했습니다';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 댓글 작성
    async addComment(postId, commentData) {
      this.loading = true;
      try {
        const response = await axios.post(
          `${API_URL}/posts/${postId}/comments/`,
          commentData,
          this.getAuthHeaders()
        );
        return response.data;   // 단일 comment 오브젝트
      } catch (error) {
        this.error = '댓글 작성 중 오류가 발생했습니다';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 댓글 삭제
    async deleteComment(postId, commentId) {
      this.loading = true;
      try {
        await axios.delete(
          `${API_URL}/posts/${postId}/comments/${commentId}/`,
          this.getAuthHeaders()
        );
        return true;
      } catch (error) {
        this.error = '댓글 삭제 중 오류가 발생했습니다';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 좋아요 토글
    async toggleLike(postId) {
      try {
        const response = await axios.post(`${API_URL}/posts/${postId}/like/`, {}, this.getAuthHeaders());
        return response.data;
      } catch (error) {
        this.error = '좋아요 처리 중 오류가 발생했습니다';
        throw error;
      }
    },

    // 오류 초기화
    clearError() {
      this.error = null;
    }
  },
});