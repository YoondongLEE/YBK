<template>
  <div class="post-list-container">
    <div class="post-list-header">
      <div class="post-filters">
        <select v-model="currentCategory" class="category-filter">
          <option value="">전체 카테고리</option>
          <option value="경제뉴스">경제뉴스</option>
          <option value="투자정보">투자정보</option>
          <option value="자유게시판">자유게시판</option>
          <option value="질문답변">질문답변</option>
        </select>
        
        <div class="search-bar">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="검색어를 입력하세요"
            @keyup.enter="searchPosts"
          >
          <button @click="searchPosts" class="search-btn">
            <i class="fas fa-search"></i>
          </button>
        </div>
      </div>
      
      <router-link 
        v-if="authStore.isAuthenticated" 
        :to="{ name: 'post-create' }" 
        class="create-post-btn"
      >
        <i class="fas fa-pen"></i> 글 작성하기
      </router-link>
    </div>
    
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <p>게시글을 불러오는 중입니다...</p>
    </div>
    
    <div v-else-if="!posts.length" class="no-posts">
      <p>{{ currentCategory ? `${currentCategory} 카테고리에 ` : '' }}게시글이 없습니다.</p>
      <p v-if="authStore.isAuthenticated">첫 번째 게시글을 작성해보세요!</p>
    </div>
    
    <div v-else class="post-list">
      <div 
        v-for="post in posts" 
        :key="post.id" 
        class="post-item"
        @click="goToPostDetail(post.id)"
      >
        <div class="post-meta">
          <span class="post-category">{{ post.category }}</span>
          <span class="post-date">
            {{ formatDate(post.created_at) }}
            <!-- <span v-if="isPostEdited(post)" class="updated-indication">
              (수정됨)
            </span> -->
          </span>
        </div>
        <h3 class="post-title">{{ post.title }}</h3>
        <p class="post-preview">
          {{ post.content.substring(0, 100) }}{{ post.content.length > 100 ? '...' : '' }}
        </p>
        <div class="post-footer">
          <div class="post-author">
            <i class="fas fa-user"></i> {{ post.author.username }}
          </div>
          <div class="post-stats">
            <span class="post-views">
              <i class="fas fa-eye"></i> {{ post.view_count }}
            </span>
            <span class="post-comments">
              <i class="fas fa-comment"></i> {{ post.comment_count }}
            </span>
            <span class="post-likes">
              <i class="fas fa-heart"></i> {{ post.like_count }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="pagination" v-if="totalPages > 1">
      <button 
        :disabled="currentPage === 1" 
        @click="changePage(currentPage - 1)" 
        class="page-btn"
      >
        <i class="fas fa-chevron-left"></i>
      </button>
      
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      
      <button 
        :disabled="currentPage === totalPages" 
        @click="changePage(currentPage + 1)" 
        class="page-btn"
      >
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useCommunityStore } from '@/stores/community';

const router = useRouter();
const authStore = useAuthStore();
const communityStore = useCommunityStore();

const posts = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const totalPages = ref(1);
const currentCategory = ref('');
const searchQuery = ref('');

// 게시글 불러오기 함수에 디버깅 코드 추가
const fetchPosts = async () => {
  loading.value = true;
  try {
    const data = await communityStore.getPosts({
      page: currentPage.value,
      category: currentCategory.value,
      search: searchQuery.value
    });

    console.log('API 응답 전체 구조:', data);

    if (data && Array.isArray(data.results) && data.results.length > 0) {
      const firstPost = data.results[0];
      console.log('첫번째 게시글:', firstPost);
      console.log('created_at:', firstPost.created_at);
      console.log('updated_at:', firstPost.updated_at);
      console.log('두 날짜가 같은지:', firstPost.created_at === firstPost.updated_at);
      
      // ISO 문자열을 Date 객체로 변환하여 비교
      const createdDate = new Date(firstPost.created_at);
      const updatedDate = new Date(firstPost.updated_at);
      const diffMs = updatedDate - createdDate;
      console.log('날짜 차이(밀리초):', diffMs);
      console.log('수정되었는지(차이가 있는지):', diffMs > 0);
    }

    // 배열만 리턴되는 경우
    else if (Array.isArray(data)) {
      posts.value = data;
      totalPages.value = 1;
    }
    // 그 외
    else {
      posts.value = [];
      totalPages.value = 1;
    }
  } catch (err) {
    console.error('게시글을 불러오는 중 오류가 발생했습니다:', err);
    posts.value = [];
    totalPages.value = 1;
  } finally {
    loading.value = false;
  }
};

// 페이지 변경
const changePage = (page) => {
  currentPage.value = page;
};

// 검색 실행
const searchPosts = () => {
  currentPage.value = 1;
  fetchPosts();
};

// 상세 페이지 이동
const goToPostDetail = (id) => {
  router.push({ name: 'post-detail', params: { id } });
};

// 날짜 포맷 함수 - 더 강건한 버전
const formatDate = (dateString) => {
  if (!dateString) return '날짜 없음';
  
  try {
    const date = new Date(dateString);
    
    // 유효하지 않은 날짜인 경우
    if (isNaN(date.getTime())) {
      console.error('유효하지 않은 날짜:', dateString);
      return '날짜 오류';
    }
    
    // 현재 시간 (로컬 시간대)
    const now = new Date();
    
    // 차이 계산 (밀리초)
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    // 결과 포맷팅
    if (minutes < 1) {
      return '방금 전';
    } else if (hours < 1) {
      return `${minutes}분 전`;
    } else if (days < 1) {
      return `${hours}시간 전`;
    } else if (days < 7) {
      return `${days}일 전`;
    } else {
      return date.toLocaleString('ko-KR', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    }
  } catch (error) {
    console.error('날짜 변환 중 오류:', error);
    return '날짜 오류';
  }
};

// 수정 여부 판단 함수 (정확한 방법)
const isPostEdited = (post) => {
  // 날짜 정보가 없으면 수정되지 않은 것으로 간주
  if (!post || !post.created_at || !post.updated_at) return false;
  
  // 날짜 문자열을 그대로 비교해서 다른 경우 수정된 것으로 간주
  if (post.created_at !== post.updated_at) {
    // 눈에 보이는 차이가 있는지 확인 (초 단위 이상)
    const created = new Date(post.created_at);
    const updated = new Date(post.updated_at);
    const diffSeconds = Math.abs(updated - created) / 1000;
    
    // 1초 이상 차이가 있으면 수정된 것으로 간주
    return diffSeconds >= 1;
  }
  
  return false;
};

watch([currentCategory, currentPage], fetchPosts);
onMounted(fetchPosts);
</script>

<style scoped>
.post-list-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.post-filters {
  display: flex;
  gap: 15px;
  align-items: center;
}

.category-filter {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-bar {
  display: flex;
  position: relative;
}

.search-bar input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 250px;
}

.search-btn {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
}

.create-post-btn {
  background-color: #4a90e2;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.3s;
}

.create-post-btn:hover {
  background-color: #3a80d2;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #4a90e2;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-posts {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.post-item {
  padding: 15px;
  border-radius: 8px;
  background-color: #fff;
  border: 1px solid #eee;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.post-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.post-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 13px;
}

.post-category {
  background-color: #f0f4f8;
  padding: 2px 8px;
  border-radius: 12px;
  color: #4a90e2;
  font-weight: 500;
}

.post-date {
  color: #999;
}

.updated-indication {
  font-size: 12px;
  color: #4a90e2;
  margin-left: 5px;
}

.post-title {
  margin: 0 0 10px;
  font-size: 18px;
  color: #333;
}

.post-preview {
  font-size: 14px;
  color: #666;
  margin: 0 0 15px;
  line-height: 1.5;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.post-author {
  color: #666;
}

.post-stats {
  display: flex;
  gap: 15px;
}

.post-views, .post-comments, .post-likes {
  color: #888;
  display: flex;
  align-items: center;
  gap: 5px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.page-btn {
  background-color: #f0f4f8;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}


.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .post-list-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .post-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-bar input {
    width: 100%;
  }
}
</style>