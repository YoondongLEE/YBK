<template>
  <div class="deposit-detail-container">
    <div v-if="isDataReady">
      <div class="header">
        <button @click="goBack" class="back-button">
          ← 목록으로 돌아가기
        </button>
        
        <div class="product-header">
          <div class="bank-name">{{ product.bank.kor_co_nm }}</div>
          <div class="product-name">{{ product.fin_prdt_nm }}</div>
          <div class="max-rate">최대 금리 {{ product.max_rate }}%</div>
        </div>
      </div>
      
      <div class="product-info">
        <h3>상품 정보</h3>
        <div><strong>가입방법:</strong> {{ product.join_way }}</div>
        <div><strong>만기 후 이자율:</strong> {{ product.mtrt_int }}</div>
        <div v-if="product.spcl_cnd"><strong>우대조건:</strong> {{ product.spcl_cnd }}</div>
      </div>

      <h3>가입기간별 금리</h3>
      <table v-if="etcList.length > 0" class="detail-table">
        <thead>
          <tr>
            <th v-for="opt in etcList" :key="opt.save_trm">
              {{ opt.save_trm }}개월
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td v-for="opt in etcList" :key="opt.save_trm" :class="{'best-rate': isBestRate(opt)}">
              {{ opt.intr_rate }}%
            </td>
          </tr>
          <tr v-if="hasIntrRate2">
            <td v-for="opt in etcList" :key="opt.save_trm">
              {{ opt.intr_rate2 ? `(우대 ${opt.intr_rate2}%)` : '' }}
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="no-data">
        상세 금리 정보가 없습니다.
      </div>

      <div class="buttons">
        <button
          v-if="isAuthenticated"
          :class="['subscribe-btn', { 'subscribed': subscribed }]"
          @click="subscribeProduct"
          :disabled="subscribed"
        >
          {{ subscribed ? '가입 완료' : '가입하기' }}
        </button>
        <p v-else class="auth-message">가입하려면 로그인이 필요합니다.</p>
        <p v-if="message" class="message" :class="{ 'error': message.includes('실패') }">
          {{ message }}
        </p>
      </div>
    </div>
    <div v-else-if="loading" class="loading">로딩 중...</div>
    <div v-else class="error">
      상품 정보를 불러오는데 실패했습니다.
      <button @click="goBack" class="back-button">
        ← 목록으로 돌아가기
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const product = ref(null)
const message = ref('')
const subscribed = ref(false)

// 로그인 여부 확인
const isAuthenticated = computed(() => authStore.isAuthenticated)

// 상품 금리 정보를 배열로 정리
const etcList = computed(() => {
  if (!product.value || !product.value.etc) return [];
  
  // etc가 배열인지 단일 객체인지 확인하여 안전하게 처리
  const etc = product.value.etc;
  return Array.isArray(etc) ? etc : [etc];
});

// 상세 정보 조회 전 페이지에 etcList 오류가 발생하지 않도록 방어적 렌더링
const isDataReady = computed(() => {
  return !loading.value && product.value !== null;
});

// 우대금리가 있는지 확인
const hasIntrRate2 = computed(() => {
  return etcList.value.some(opt => opt.intr_rate2 && opt.intr_rate2 !== '0');
});

// 최고 금리인지 확인하는 함수
const isBestRate = (opt) => {
  if (!etcList.value.length) return false;
  
  const rates = etcList.value
    .map(item => parseFloat(item.intr_rate) || 0)
    .filter(rate => rate > 0);
  
  const maxRate = Math.max(...rates);
  return parseFloat(opt.intr_rate) === maxRate && maxRate > 0;
};

// 페이지 로드 시 가입 상태 확인
const checkSubscription = async () => {
  if (!isAuthenticated.value) return
  
  try {
    const response = await api.get(`/deposits/${route.params.id}/check-subscription/`);
    subscribed.value = response.data.is_subscribed;
  } catch (e) {
    console.error('가입 상태 확인 실패:', e);
    // 401 오류는 조용히 무시 (로그인 상태가 아니므로)
  }
};

// 상품 상세 조회
const fetchDetail = async () => {
  try {
    loading.value = true
    console.log('Fetching detail for ID:', route.params.id)
    const res = await api.get(`/deposits/${route.params.id}/`)
    console.log('API Response:', res.data)
    product.value = res.data
    
    // 상세 정보 로드 후 가입 상태 확인
    if (isAuthenticated.value) {
      await checkSubscription()
    }
  } catch (e) {
    console.error('상세조회 실패:', e)
  } finally {
    loading.value = false
  }
}

// 가입하기
const subscribeProduct = async () => {
  try {
    if (!isAuthenticated.value) {
      message.value = '로그인이 필요합니다.';
      return;
    }
    
    // 이미 가입한 경우
    if (subscribed.value) {
      message.value = '이미 가입한 상품입니다.';
      return;
    }
    
    // 가입 API 호출 - 직접 토큰을 포함하지 않음 (인터셉터가 처리)
    const response = await api.post(`/deposits/${route.params.id}/subscribe/`);
    
    message.value = response.data.message || '가입 완료!';
    subscribed.value = true;
    
    // 3초 후 메시지 숨기기
    setTimeout(() => {
      message.value = '';
    }, 3000);
  } catch (e) {
    console.error('가입 실패:', e);
    
    // 서버 에러 메시지 표시
    if (e.response && e.response.data) {
      message.value = e.response.data.error || e.response.data.message || '가입에 실패했습니다';
    } else {
      message.value = '가입에 실패했습니다';
    }
  }
}

// 목록으로 돌아가기
const goBack = () => {
  router.push({name: 'deposits'});
}

onMounted(fetchDetail);
</script>

<style scoped>
.deposit-detail-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.back-button {
  align-self: flex-start;
  background: none;
  border: none;
  color: #4a90e2;
  cursor: pointer;
  font-size: 16px;
  padding: 5px 0;
  margin-bottom: 10px;
}

.product-header {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f8ff;
  border-radius: 8px;
  border-left: 5px solid #4a90e2;
}

.bank-name {
  font-size: 16px;
  color: #666;
}

.product-name {
  font-size: 24px;
  font-weight: bold;
  margin: 5px 0;
}

.max-rate {
  font-size: 20px;
  color: #ff5722;
  font-weight: bold;
}

.product-info {
  margin-bottom: 30px;
  line-height: 1.6;
}

.product-info div {
  margin-bottom: 10px;
}

h3 {
  color: #333;
  margin: 25px 0 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 30px;
}

.detail-table th,
.detail-table td {
  padding: 12px;
  border: 1px solid #ddd;
  text-align: center;
}

.detail-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.best-rate {
  font-weight: bold;
  color: #ff5722;
  background-color: #fff8e1;
}

.buttons {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.subscribe-btn {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.subscribe-btn.subscribed {
  background-color: #4caf50;
  cursor: not-allowed;
}

.subscribe-btn:not(.subscribed):hover {
  background-color: #3a7bc8;
}

.message {
  margin-top: 10px;
  color: #4caf50;
  font-weight: bold;
}

.message.error {
  color: #f44336;
}

.auth-message {
  margin-top: 10px;
  color: #f44336;
}

.loading, .no-data, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f44336;
}
</style>