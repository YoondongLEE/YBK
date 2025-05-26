<template>
  <div class="post-edit-container">
    <h2>게시글 수정</h2>
    
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <p>게시글을 불러오는 중입니다...</p>
    </div>
    
    <form v-else @submit.prevent="updatePost" class="post-form">
      <div class="form-group">
        <label for="category">카테고리:</label>
        <select id="category" v-model="postData.category" required>
          <option value="">카테고리 선택</option>
          <option value="경제뉴스">경제뉴스</option>
          <option value="투자정보">투자정보</option>
          <option value="자유게시판">자유게시판</option>
          <option value="질문답변">질문답변</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="title">제목:</label>
        <input 
          type="text" 
          id="title" 
          v-model="postData.title"
          placeholder="제목을 입력하세요" 
          required
        />
      </div>
      
      <div class="form-group">
        <label for="content">내용:</label>
        <textarea 
          id="content" 
          v-model="postData.content"
          rows="10" 
          placeholder="게시글 내용을 입력하세요" 
          required
        ></textarea>
      </div>
      
      <div class="form-actions">
        <button type="button" class="cancel-btn" @click="goBack">취소</button>
        <button type="submit" class="submit-btn" :disabled="submitting">
          <span v-if="submitting" class="spinner small"></span>
          <span v-else>저장하기</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCommunityStore } from '@/stores/community';
import { useAuthStore } from '@/stores/auth';
import { useAlertStore } from '@/stores/alert';

const route = useRoute();
const router = useRouter();
const communityStore = useCommunityStore();
const authStore = useAuthStore();
const alertStore = useAlertStore();

const postId = route.params.id;
const postData = ref({
  title: '',
  content: '',
  category: ''
});

const loading = ref(true);
const submitting = ref(false);

// 게시글 데이터 불러오기
const loadPost = async () => {
  try {
    const post = await communityStore.getPostDetail(postId);
    
    // 문자열 변환을 통해 ID 비교
    const currentUserId = String(authStore.user?.id || authStore.user?.pk);
    const authorId = String(post.author?.id);
    
    console.log('현재 사용자 ID:', currentUserId);
    console.log('게시글 작성자 ID:', authorId);
    console.log('ID 일치 여부:', currentUserId === authorId);
    
    // 작성자 확인 - ID가 일치하지 않으면 권한 거부
    if (currentUserId !== authorId) {
      alertStore.showAlert({
        title: '권한 없음',
        message: '이 게시글을 수정할 권한이 없습니다.',
        type: 'error'
      });
      router.push({ name: 'post-detail', params: { id: postId } });
      return;
    }
    
    // 게시글 데이터 설정
    postData.value = {
      title: post.title,
      content: post.content,
      category: post.category
    };
  } catch (error) {
    console.error('게시글을 불러오는 중 오류가 발생했습니다:', error);
    alertStore.showAlert({
      title: '게시글 로드 실패',
      message: '게시글을 불러오는 중 오류가 발생했습니다.',
      type: 'error'
    });
    router.push({ name: 'post-list' });
  } finally {
    loading.value = false;
  }
};

// 게시글 수정
const updatePost = async () => {
  if (!postData.value.title || !postData.value.content || !postData.value.category) {
    alertStore.showAlert({
      title: '입력 오류',
      message: '모든 필드를 입력해주세요.',
      type: 'error'
    });
    return;
  }
  
  submitting.value = true;
  
  try {
    await communityStore.updatePost(postId, postData.value);
    alertStore.showAlert({
      title: '수정 성공',
      message: '게시글이 수정되었습니다.',
      type: 'success'
    });
    router.push({ name: 'post-detail', params: { id: postId } });
  } catch (error) {
    console.error('게시글 수정 중 오류 발생:', error);
    alertStore.showAlert({
      title: '게시글 수정 실패',
      message: '게시글 수정 중 오류가 발생했습니다. 다시 시도해주세요.',
      type: 'error'
    });
  } finally {
    submitting.value = false;
  }
};

// 취소 시 상세 페이지로 이동
const goBack = () => {
  router.push({ name: 'post-detail', params: { id: postId } });
};

// 게시글 불러오기 전에 인증 상태 확인
onMounted(async () => {
  try {
    // 인증 토큰이 있으면 사용자 정보 다시 로드
    if (authStore.token) {
      await authStore.fetchUserInfo();
      console.log('사용자 정보 새로 로드:', authStore.user);
    }
    
    // 그 후 게시글 로드
    await loadPost();
  } catch (error) {
    console.error('초기화 오류:', error);
  }
});
</script>

<style scoped>
.post-edit-container {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
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

.spinner.small {
  width: 18px;
  height: 18px;
  border-width: 2px;
  margin: 0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.post-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: 500;
  color: #333;
}

input, textarea, select {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
}

input:focus, textarea:focus, select:focus {
  border-color: #4a90e2;
  outline: none;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.cancel-btn, .submit-btn {
  padding: 10px 20px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cancel-btn {
  background-color: #f1f1f1;
  border: none;
  color: #333;
}

.submit-btn {
  background-color: #4a90e2;
  border: none;
  color: white;
  font-weight: 500;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.submit-btn:hover {
  background-color: #3a80d2;
}

.submit-btn:disabled {
  background-color: #a0c0e8;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .post-edit-container {
    padding: 0 15px;
  }
}
</style>