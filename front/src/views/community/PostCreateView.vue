<template>
  <div class="post-create-container">
    <h2>새 게시글 작성</h2>
    
    <form @submit.prevent="submitPost" class="post-form">
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
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner small"></span>
          <span v-else>게시글 등록</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useCommunityStore } from '@/stores/community';
import { useAlertStore } from '@/stores/alert';

const router = useRouter();
const communityStore = useCommunityStore();
const alertStore = useAlertStore();

const postData = ref({
  title: '',
  content: '',
  category: '자유게시판'
});

const loading = ref(false);

const submitPost = async () => {
  if (!postData.value.title || !postData.value.content || !postData.value.category) {
    alertStore.showAlert({
      title: '입력 오류',
      message: '모든 필드를 입력해주세요.',
      type: 'error'
    });
    return;
  }
  
  loading.value = true;
  
  try {
    const newPost = await communityStore.createPost(postData.value);
    alertStore.showAlert({
      title: '게시글 등록 성공',
      message: '게시글이 성공적으로 등록되었습니다.',
      type: 'success'
    });
    router.push({ name: 'post-detail', params: { id: newPost.id } });
  } catch (error) {
    console.error('게시글 작성 중 오류 발생:', error);
    alertStore.showAlert({
      title: '게시글 등록 실패',
      message: '게시글 등록 중 오류가 발생했습니다. 다시 시도해주세요.',
      type: 'error'
    });
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  router.go(-1);
};
</script>

<style scoped>
.post-create-container {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 20px;
  color: #333;
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

.spinner.small {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin: 0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>