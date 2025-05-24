<template>
  <div class="mypage-container">
    <h1>내 정보</h1>
    
    <!-- 사용자 정보 섹션 -->
    <div class="user-info-section">
      <h2>회원 정보</h2>
      <div class="user-info">
        <p><strong>아이디:</strong> {{ user.username }}</p>
        <p><strong>이메일:</strong> {{ user.email || '이메일 정보 없음' }}</p>
      </div>
    </div>
    
    <!-- 정기예금 목록 섹션 -->
    <div class="subscription-section">
      <h2>가입한 정기예금 상품</h2>
      <div v-if="depositLoading" class="loading">
        정기예금 상품 정보를 불러오는 중...
      </div>
      <div v-else-if="!depositProducts.length" class="empty-state">
        가입한 정기예금 상품이 없습니다.
      </div>
      <div v-else class="product-list">
        <!-- 정기예금 상품 목록 -->
        <div v-for="product in depositProducts" :key="product.fin_prdt_cd" class="product-card"
          @click="goToDetail('deposit', product.fin_prdt_cd)">
          <div class="bank-name">{{ product.bank_name || getBankName(product) || '정보 없음' }}</div>
          <div class="product-name">{{ product.fin_prdt_nm }}</div>
          <div class="rate">최고금리: {{ getMaxRate(product) }}%</div>
        </div>
      </div>
    </div>

    <!-- 정기적금 목록 섹션 -->
    <div class="subscription-section">
      <h2>가입한 정기적금 상품</h2>
      <div v-if="savingLoading" class="loading">
        정기적금 상품 정보를 불러오는 중...
      </div>
      <div v-else-if="!savingProducts.length" class="empty-state">
        가입한 정기적금 상품이 없습니다.
      </div>
      <div v-else class="product-list">
        <!-- 정기적금 상품 목록 -->
        <div v-for="product in savingProducts" :key="product.fin_prdt_cd" class="product-card"
          @click="goToDetail('saving', product.fin_prdt_cd)">
          <div class="bank-name">{{ product.bank_name || getBankName(product) || '정보 없음' }}</div>
          <div class="product-name">{{ product.fin_prdt_nm }}</div>
          <div class="rate">최고금리: {{ getMaxRate(product) }}%</div>
        </div>
      </div>
    </div>
    
    <!-- 저장된 영상 섹션 -->
    <div v-if="isAuthenticated" class="saved-items-section">
      <h2>저장된 금융 콘텐츠</h2>
      <SavedItems />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useYoutubeStore } from '../stores/youtube';
import api from '../api';
import SavedItems from '../components/youtube/SavedItems.vue';

const router = useRouter();
const authStore = useAuthStore();
const youtubeStore = useYoutubeStore();
const user = ref(authStore.user || {});
const isAuthenticated = computed(() => authStore.isAuthenticated);

// 정기예금 상품 관련 상태
const depositLoading = ref(true);
const depositProducts = ref([]);

// 정기적금 상품 관련 상태
const savingLoading = ref(true);
const savingProducts = ref([]);

// 은행 정보
const banks = ref([]);

// 은행 정보 불러오기
const fetchBanks = async () => {
  try {
    const response = await api.get('/banks/');
    banks.value = response.data;
    console.log('은행 정보 로드:', banks.value.length);
  } catch (error) {
    console.error('은행 정보 로드 실패:', error);
  }
};

// 은행명 가져오기
const getBankName = (product) => {
  if (product.bank && typeof product.bank === 'object' && product.bank.kor_co_nm) {
    return product.bank.kor_co_nm;
  }
  
  if (product.bank && typeof product.bank === 'string') {
    const bankObj = banks.value.find(b => b.fin_co_no === product.bank);
    return bankObj ? bankObj.kor_co_nm : '정보 없음';
  }
  
  return '정보 없음';
};

// 최대 금리 계산 함수
const getMaxRate = (product) => {
  if (!product.options || !product.options.length) return '정보 없음';
  
  let maxRate = 0;
  product.options.forEach(option => {
    const rate = parseFloat(option.intr_rate2) || parseFloat(option.intr_rate) || 0;
    if (rate > maxRate) maxRate = rate;
  });
  
  return maxRate.toFixed(2);
};

// 상세 페이지로 이동하는 함수
const goToDetail = (type, id) => {
  router.push({ name: `${type}-detail`, params: { id } });
};

// 정기예금 상품 정보 불러오기
const fetchDepositProducts = async () => {
  try {
    depositLoading.value = true;
    console.log('정기예금 상품 조회 API 호출 시작');
    
    // URL 경로가 백엔드와 일치하는지 확인
    const response = await api.get('/deposits/user-subscriptions/');
    console.log('정기예금 상품 조회 응답:', response.data);
    depositProducts.value = response.data;
  } catch (error) {
    console.error('정기예금 상품 정보 조회 실패:', error);
  } finally {
    depositLoading.value = false;
  }
};

// 정기적금 상품 정보 불러오기
const fetchSavingProducts = async () => {
  try {
    savingLoading.value = true;
    console.log('정기적금 상품 조회 API 호출 시작');
    
    // URL 경로가 백엔드와 일치하는지 확인
    const response = await api.get('/savings/user-subscriptions/');
    console.log('정기적금 상품 조회 응답:', response.data);
    savingProducts.value = response.data;
  } catch (error) {
    console.error('정기적금 상품 정보 조회 실패:', error);
  } finally {
    savingLoading.value = false;
  }
};

onMounted(async () => {
  if (isAuthenticated.value) {
    await fetchBanks();
    fetchDepositProducts();
    fetchSavingProducts();
    
    // YouTube 데이터 초기화
    youtubeStore.initialize();
  } else {
    router.push({ name: 'login' });
  }
});
</script>

<style scoped>
.mypage-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 30px;
  color: #333;
}

.user-info-section,
.subscription-section,
.saved-items-section {
  margin-bottom: 40px;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

h2 {
  margin-bottom: 15px;
  color: #4a4a4a;
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 10px;
}

.user-info {
  padding: 10px;
}

.user-info p {
  margin-bottom: 8px;
}

.product-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.product-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  background-color: #fff;
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.bank-name {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.product-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.rate {
  font-size: 16px;
  color: #ff5722;
  font-weight: bold;
}

.loading, .empty-state {
  padding: 30px;
  text-align: center;
  background-color: #f9f9f9;
  border-radius: 8px;
  color: #666;
}
</style>