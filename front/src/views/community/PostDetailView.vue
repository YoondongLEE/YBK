<template>
  <div class="post-detail-container">
    <!-- 로딩 표시 -->
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <p>게시글을 불러오는 중입니다...</p>
    </div>

    <!-- 게시글 없음 -->
    <div v-else-if="!post" class="not-found">
      <h2>게시글을 찾을 수 없습니다</h2>
      <p>요청하신 게시글이 존재하지 않거나 삭제되었습니다.</p>
      <router-link :to="{ name: 'post-list' }" class="back-btn">
        게시글 목록으로 돌아가기
      </router-link>
    </div>

    <!-- 게시글 상세 -->
    <template v-else>
      <div class="post-header">
        <div class="post-category">{{ post.category }}</div>
        <div class="post-title-container">
          <h1 class="post-title">{{ post.title }}</h1>
        </div>
        <div class="post-meta">
          <div class="post-author">
            <i class="fas fa-user"></i> {{ post.author.username }}
          </div>
          <div class="post-date">
            <div>
              <i class="fas fa-clock"></i> 
              <span class="date-label">작성:</span> 
              {{ formatDate(post.created_at) }}
            </div>
            <!-- <div v-if="isPostEdited(post)" class="updated-date">
              <i class="fas fa-edit"></i> 
              <span class="date-label">수정:</span> 
              {{ formatDate(post.updated_at) }}
            </div> -->
          </div>
        </div>
      </div>

      <div class="post-content">
        {{ post.content }}
      </div>

      <div class="post-actions">
        <div class="post-stats">
          <div class="stat-item">
            <i class="fas fa-eye"></i> {{ post.view_count }}
          </div>
          <div 
            class="stat-item like-btn"
            :class="{ liked: post.is_liked }"
            @click="handleLike"
          >
            <i class="fas fa-heart"></i> {{ post.like_count }}
          </div>
          <div class="stat-item">
            <i class="fas fa-comment"></i> {{ post.comments?.length || 0 }}
          </div>
        </div>

        <!-- 본인 작성글에만 표시 -->
        <div v-if="!loading && isAuthor" class="author-actions">
          <router-link 
            :to="{ name: 'post-edit', params: { id: post.id } }"
            class="edit-btn"
          >
            <i class="fas fa-edit"></i> 수정
          </router-link>
          <button @click="confirmDelete" class="delete-btn">
            <i class="fas fa-trash"></i> 삭제
          </button>
        </div>
      </div>

      <!-- 댓글 섹션 -->
      <div class="comments-section">
        <h3>댓글 {{ post.comments?.length || 0 }}개</h3>

        <!-- 댓글 작성 폼 -->
        <div v-if="authStore.isAuthenticated" class="comment-form">
          <textarea
            v-model="commentText"
            placeholder="댓글을 작성해주세요..."
            rows="3"
          ></textarea>
          <button
            @click="addComment"
            class="submit-comment-btn"
            :disabled="!commentText.trim() || commentLoading"
          >
            <span v-if="commentLoading" class="spinner small"></span>
            <span v-else>댓글 등록</span>
          </button>
        </div>
        <div v-else class="login-prompt">
          <p>
            댓글을 작성하려면
            <router-link to="/login">로그인</router-link>이 필요합니다.
          </p>
        </div>

        <!-- 댓글 목록 -->
        <div
          v-if="post.comments && post.comments.length > 0"
          class="comment-list"
        >
          <div
            v-for="comment in post.comments"
            :key="comment.id"
            class="comment-item"
          >
            <div class="comment-header">
              <div class="comment-author">
                <i class="fas fa-user"></i> {{ comment.author.username }}
              </div>
              <div class="comment-date">
                <div>
                  <span class="date-label">작성:</span> {{ formatDate(comment.created_at) }}
                </div>
              </div>
            </div>
            <div class="comment-content">
              {{ comment.content }}
            </div>
            <!-- 본인 댓글에만 표시 -->
            <div v-if="isCommentAuthor(comment)" class="comment-actions">
              <button @click="deleteComment(comment.id)" class="delete-comment-btn">
                삭제
              </button>
            </div>
          </div>
        </div>
        <div v-else class="no-comments">
          <p>아직 댓글이 없습니다. 첫 댓글을 작성해보세요!</p>
        </div>
      </div>

      <!-- 목록으로 돌아가기 -->
      <div class="back-container">
        <router-link :to="{ name: 'post-list' }" class="back-btn">
          <i class="fas fa-arrow-left"></i> 목록으로 돌아가기
        </router-link>
      </div>
    </template>

    <!-- 삭제 확인 모달 -->
    <div v-if="showDeleteModal" class="delete-modal">
      <div class="delete-modal-content">
        <h3>게시글 삭제</h3>
        <p>게시글을 정말 삭제하시겠습니까?</p>
        <p class="modal-warning">삭제된 게시글은 복구할 수 없습니다.</p>
        <div class="modal-actions">
          <button @click="showDeleteModal = false" class="cancel-modal-btn">
            취소
          </button>
          <button
            @click="deletePost"
            class="confirm-delete-btn"
            :disabled="deleteLoading"
          >
            <span v-if="deleteLoading" class="spinner small"></span>
            <span v-else>삭제</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCommunityStore } from '@/stores/community'
import { useAuthStore } from '@/stores/auth'
import { useAlertStore } from '@/stores/alert'

const route          = useRoute()
const router         = useRouter()
const communityStore = useCommunityStore()
const authStore      = useAuthStore()
const alertStore     = useAlertStore()

const post            = ref(null)
const loading         = ref(false)
const commentText     = ref('')
const commentLoading  = ref(false)
const showDeleteModal = ref(false)
const deleteLoading   = ref(false)

// ★ 본인 게시글인지 확인 (id → pk 로 변경) ★
const isAuthor = computed(() => {
  if (!post.value || !authStore.user) return false
  return Number(post.value.author.id) === Number(authStore.user.pk)
})

// ★ 본인 댓글인지 확인 ★
const isCommentAuthor = (comment) => {
  if (!authStore.user) return false
  return Number(comment.author.id) === Number(authStore.user.pk)
}

// 날짜 포맷 함수 - 분 단위 표시 적용
const formatDate = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  // 유효한 날짜인지 확인
  if (isNaN(date.getTime())) {
    return '날짜 정보 없음';
  }
  
  // 현재 시간
  const now = new Date();
  
  // 차이 계산 (밀리초)
  const diff = now - date;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  // 1분 이내면 '방금 전'으로 표시
  if (minutes < 1) {
    return '방금 전';
  }
  // 1시간 이내면 '분 전'으로 표시
  else if (hours < 1) {
    return `${minutes}분 전`;
  } 
  // 24시간 이내면 '시간 전'으로 표시 
  else if (days < 1) {
    return `${hours}시간 전`;
  }
  // 7일 이내면 '일 전'으로 표시
  else if (days < 7) {
    return `${days}일 전`;
  } else {
    // 그 외는 날짜와 시간 표시
    return date.toLocaleString('ko-KR', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }
};


// 게시글 상세 로드
const loadPost = async () => {
  loading.value = true
  try {
    post.value = await communityStore.getPostDetail(route.params.id)
  } catch {
    alertStore.showAlert({
      title: '불러오기 실패',
      message: '게시글을 가져오는 중 오류가 발생했습니다.',
      type: 'error'
    })
  } finally {
    loading.value = false
  }
}

// 좋아요 토글
const handleLike = async () => {
  if (!authStore.isAuthenticated) {
    alertStore.showAlert({
      title: '로그인 필요',
      message: '좋아요를 누르려면 로그인이 필요합니다.',
      type: 'warning'
    })
    return
  }
  try {
    const result = await communityStore.toggleLike(post.value.id)
    post.value.is_liked   = result.liked
    post.value.like_count = result.like_count
  } catch {
    alertStore.showAlert({
      title: '오류',
      message: '좋아요 처리 중 문제가 발생했습니다.',
      type: 'error'
    })
  }
}

// 댓글 작성
const addComment = async () => {
  if (!commentText.value.trim()) return
  commentLoading.value = true
  try {
    await communityStore.addComment(post.value.id, { content: commentText.value })
    commentText.value = ''
    await loadPost()
  } catch {
    alertStore.showAlert({
      title: '댓글 작성 실패',
      message: '댓글 작성 중 문제가 발생했습니다.',
      type: 'error'
    })
  } finally {
    commentLoading.value = false
  }
}

// 댓글 삭제
const deleteComment = async (commentId) => {
  if (!confirm('댓글을 삭제하시겠습니까?')) return
  commentLoading.value = true
  try {
    await communityStore.deleteComment(post.value.id, commentId)
    await loadPost()
  } catch {
    alertStore.showAlert({
      title: '댓글 삭제 실패',
      message: '댓글 삭제 중 문제가 발생했습니다.',
      type: 'error'
    })
  } finally {
    commentLoading.value = false
  }
}

// 게시글 삭제 모달 열기
const confirmDelete = () => { showDeleteModal.value = true }

// 게시글 삭제
const deletePost = async () => {
  deleteLoading.value = true
  try {
    await communityStore.deletePost(post.value.id)
    alertStore.showAlert({
      title: '삭제 성공',
      message: '게시글이 삭제되었습니다.',
      type: 'success'
    })
    router.push({ name: 'post-list' })
  } catch {
    alertStore.showAlert({
      title: '삭제 실패',
      message: '게시글 삭제 중 오류가 발생했습니다.',
      type: 'error'
    })
  } finally {
    deleteLoading.value   = false
    showDeleteModal.value = false
  }
}

// 게시글이 실제로 수정되었는지 확인
const isPostEdited = (post) => {
  if (!post || !post.created_at || !post.updated_at) return false;
  
  return post.created_at !== post.updated_at;
};

onMounted(loadPost)
</script>


<style scoped>
.post-detail-container {
  position: relative;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.loading-indicator,
.not-found {
  text-align: center;
  padding: 40px 0;
}

.spinner {
  border: 4px solid rgba(0,0,0,0.1);
  border-left-color: #4a90e2;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

.spinner.small {
  width: 16px;
  height: 16px;
  border-width: 2px;
  margin: 0;
}

@keyframes spin {
  0%   { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.post-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.post-category {
  display: inline-block;
  background-color: #f0f4f8;
  padding: 4px 10px;
  border-radius: 12px;
  color: #4a90e2;
  font-weight: 500;
  font-size: 14px;
  margin-bottom: 10px;
}

.post-title {
  margin: 0 0 15px;
  font-size: 24px;
  color: #333;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  color: #777;
  font-size: 14px;
}

.updated-indication {
  font-style: italic;
  margin-left: 5px;
}

.post-content {
  margin-bottom: 30px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}

.post-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 15px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
}

.post-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  color: #666;
  display: flex;
  align-items: center;
  gap: 5px;
}

.like-btn {
  cursor: pointer;
  transition: color 0.2s;
}
.like-btn:hover,
.like-btn.liked {
  color: #e74c3c;
}

.author-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.edit-btn,
.delete-btn {
  padding: 6px 12px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  text-decoration: none;
  cursor: pointer;
}

.edit-btn {
  background-color: #4a90e2;
  color: white;
  border: none;
}

.delete-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
}

.comments-section {
  margin: 30px 0;
}

.comments-section h3 {
  margin-bottom: 15px;
  color: #333;
}

.comment-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-bottom: 10px;
  resize: vertical;
}

.submit-comment-btn {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.submit-comment-btn:disabled {
  background-color: #a0c0e8;
  cursor: not-allowed;
}

.login-prompt {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
  margin-bottom: 20px;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.comment-item {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 500;
  color: #333;
}

.comment-date {
  color: #777;
  font-size: 0.9em;
}

.comment-content {
  color: #333;
  line-height: 1.5;
  white-space: pre-wrap;
}

.comment-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.delete-comment-btn {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  padding: 0;
  font-size: 0.9em;
}
.delete-comment-btn:hover {
  text-decoration: underline;
}

.no-comments {
  text-align: center;
  color: #777;
  padding: 20px 0;
}

.back-container {
  display: flex;
  justify-content: center;
  margin: 30px 0;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #f0f4f8;
  color: #333;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.2s;
}
.back-btn:hover {
  background-color: #e0e9f2;
}

/* Delete Confirmation Modal */
.delete-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.delete-modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.modal-warning {
  color: #e74c3c;
  font-weight: 500;
  margin: 15px 0;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.cancel-modal-btn,
.confirm-delete-btn {
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 100px;
}

.cancel-modal-btn {
  background-color: #f1f1f1;
  border: none;
  color: #333;
}

.confirm-delete-btn {
  background-color: #e74c3c;
  border: none;
  color: white;
}
.confirm-delete-btn:disabled {
  background-color: #f5ada6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .post-title { font-size: 20px; }
  .post-meta { flex-direction: column; gap: 5px; }
  .post-actions { flex-direction: column; gap: 15px; }
  .author-actions {
    width: 100%;
    justify-content: center;
  }
  .edit-btn,
  .delete-btn {
    flex: 1;
    justify-content: center;
  }
}

.post-date {
  display: flex;
  flex-direction: column;
  gap: 5px;
  color: #777;
  font-size: 14px;
}

.date-label {
  font-weight: 500;
  color: #666;
  margin-right: 4px;
}

.updated-date {
  color: #4a90e2;
}
</style>
