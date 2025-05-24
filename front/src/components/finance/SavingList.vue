<template>
  <div class="product-detail-container">
    <div v-if="loading" class="loading">
      상품 정보를 불러오는 중...
    </div>
    <div v-else class="detail-content">
      <div class="product-header">
        <div class="bank-logo">
          <img v-if="bank && bank.logo_url" :src="bank.logo_url" alt="은행 로고" />
          <div v-else class="bank-name-placeholder">{{ bank ? bank.kor_co_nm : '정보 없음' }}</div>
        </div>
        <div>
          <h1>{{ product.fin_prdt_nm }}</h1>
          <p class="bank-name">{{ bank ? bank.kor_co_nm : '정보 없음' }}</p>
        </div>
      </div>

      <!-- subscription-action 부분 -->
      <div class="subscription-action">
        <div v-if="isAuthenticated">
          <button 
            v-if="isSubscribed"
            @click="cancelSubscription"
            class="subscribe-btn cancel-btn"
          >
            가입취소
          </button>
          <button 
            v-else
            @click="subscribe"
            class="subscribe-btn"
          >
            가입하기
          </button>
        </div>
        <button v-else @click="goToLogin" class="subscribe-btn">
          로그인 후 가입하기
        </button>
      </div>

      <section class="product-section">
        <h2>상품 정보</h2>
        <div class="detail-grid">
          <div class="detail-item">
            <div class="label">가입방법</div>
            <div class="value">{{ product.join_way || '정보 없음' }}</div>
          </div>
          <div class="detail-item">
            <div class="label">가입대상</div>
            <div class="value">{{ product.join_member || '제한 없음' }}</div>
          </div>
          <div class="detail-item">
            <div class="label">가입제한</div>
            <div class="value">{{ product.join_deny ? product.join_deny : '없음' }}</div>
          </div>
          <div class="detail-item">
            <div class="label">최고금리</div>
            <div class="value highlight">{{ getMaxRate() }}%</div>
          </div>
          <div class="detail-item">
            <div class="label">금리유형</div>
            <div class="value">{{ product.intr_rate_type_nm || '정보 없음' }}</div>
          </div>
          <div class="detail-item">
            <div class="label">적립유형</div>
            <div class="value">{{ product.rsrv_type_nm || '정보 없음' }}</div>
          </div>
        </div>
      </section>

      <section class="product-section">
        <h2>가입기간별 금리</h2>
        <div class="rate-table-container">
          <table v-if="product.options && product.options.length > 0" class="rate-table">
            <thead>
              <tr>
                <th>가입기간</th>
                <th>기본금리</th>
                <th v-if="hasIntrRate2">우대금리</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="option in sortedOptions" :key="option.save_trm" :class="{'best-rate': isBestRate(option)}">
                <td>{{ option.save_trm }}개월</td>
                <td>{{ formatRate(option.intr_rate) }}%</td>
                <td v-if="hasIntrRate2">{{ option.intr_rate2 ? formatRate(option.intr_rate2) + '%' : '-' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="no-data">
            가입기간별 금리 정보가 없습니다.
          </div>
        </div>
      </section>

      <section class="product-section">
        <h2>상품 설명</h2>
        <div class="product-description">
          <p>{{ product.etc_note || '추가 정보가 없습니다.' }}</p>
        </div>
      </section>

      <section class="product-section">
        <h2>만기 후 이자율</h2>
        <div class="product-etc">
          <p>{{ product.mtrt_int || '정보 없음' }}</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import api from '../api';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);

const productId = route.params.id;
const loading = ref(true);
const product = ref({});
const bank = ref(null);
const isSubscribed = ref(false);

// 우대금리 여부 확인
const hasIntrRate2 = computed(() => {
  if (!product.value.options) return false;
  return product.value.options.some(opt => opt.intr_rate2 && parseFloat(opt.intr_rate2) > 0);
});

// 옵션을 기간순으로 정렬
const sortedOptions = computed(() => {
  if (!product.value.options) return [];
  return [...product.value.options].sort((a, b) => {
    return parseInt(a.save_trm) - parseInt(b.save_trm);
  });
});

// 최고금리 옵션인지 확인
const isBestRate = (option) => {
  if (!product.value.options) return false;
  
  const maxRateOption = product.value.options.reduce((max, curr) => {
    const maxRate = parseFloat(max.intr_rate2 || max.intr_rate || 0);
    const currRate = parseFloat(curr.intr_rate2 || curr.intr_rate || 0);
    return currRate > maxRate ? curr : max;
  }, { intr_rate: '0', intr_rate2: '0' });
  
  const optionRate = parseFloat(option.intr_rate2 || option.intr_rate || 0);
  const maxRate = parseFloat(maxRateOption.intr_rate2 || maxRateOption.intr_rate || 0);
  
  return optionRate >= maxRate;
};

// 상품의 최고금리 계산
const getMaxRate = () => {
  if (!product.value.options || !product.value.options.length) return '정보 없음';
  
  let maxRate = 0;
  product.value.options.forEach(opt => {
    const rate = parseFloat(opt.intr_rate2) || parseFloat(opt.intr_rate) || 0;
    if (rate > maxRate) maxRate = rate;
  });
  
  return formatRate(maxRate);
};

// 금리 소수점 형식화
const formatRate = (rate) => {
  if (!rate) return '0.00';
  return parseFloat(rate).toFixed(2);
};

// 상품 정보 로드
const fetchProductDetail = async () => {
  try {
    loading.value = true;
    const response = await api.get(`/savings/${productId}/`);
    product.value = response.data;
    console.log('적금 상품 정보:', product.value);
    
    if (product.value.fin_co_no) {
      await fetchBankInfo(product.value.fin_co_no);
    }
    
    if (isAuthenticated.value) {
      await checkSubscriptionStatus();
    }
  } catch (error) {
    console.error('상품 정보 로드 실패:', error);
  } finally {
    loading.value = false;
  }
};

// 은행 정보 로드
const fetchBankInfo = async (bankId) => {
  try {
    const response = await api.get(`/banks/${bankId}/`);
    bank.value = response.data;
  } catch (error) {
    console.error('은행 정보 로드 실패:', error);
  }
};

// 가입 상태 확인
const checkSubscriptionStatus = async () => {
  try {
    const response = await api.get(`/savings/${productId}/check-subscription/`);
    isSubscribed.value = response.data.is_subscribed;
  } catch (error) {
    console.error('가입 상태 확인 실패:', error);
    isSubscribed.value = false;
  }
};

// 가입 함수
const subscribe = async () => {
  try {
    const response = await api.post(`/savings/${productId}/subscribe/`);
    if (response.data && response.data.product_id) {
      isSubscribed.value = true;
      alert('상품 가입이 완료되었습니다!');
    } else {
      alert('가입 처리 중 오류가 발생했습니다.');
    }
  } catch (error) {
    console.error('가입 처리 실패:', error);
    let errorMsg = '가입 처리 중 오류가 발생했습니다.';
    if (error.response && error.response.data && error.response.data.error) {
      errorMsg = error.response.data.error;
    }
    alert(errorMsg);
  }
};

// 가입 취소 함수
const cancelSubscription = async () => {
  try {
    if (confirm('정말로 가입을 취소하시겠습니까?')) {
      const response = await api.post(`/savings/${productId}/subscribe/`);
      if (response.status === 200) {
        isSubscribed.value = false;
        alert('가입이 취소되었습니다.');
      } else {
        alert('취소 처리 중 오류가 발생했습니다.');
      }
    }
  } catch (error) {
    console.error('가입 취소 처리 실패:', error);
    alert('취소 처리 중 오류가 발생했습니다.');
  }
};

// 로그인 페이지로 이동
const goToLogin = () => {
  router.push({ 
    name: 'login',
    query: { redirect: route.fullPath }
  });
};

onMounted(() => {
  fetchProductDetail();
});
</script>

<style scoped>
.product-detail-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.loading {
  text-align: center;
  padding: 50px;
  font-size: 18px;
  color: #666;
}

.detail-content {
  margin-top: 20px;
}

.product-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.bank-logo {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 20px;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bank-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.bank-name-placeholder {
  font-weight: bold;
  color: #555;
  font-size: 14px;
  text-align: center;
}

h1 {
  margin: 0 0 5px;
  color: #333;
  font-size: 24px;
}

.bank-name {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.subscription-action {
  text-align: right;
  margin-bottom: 30px;
}

.subscribe-btn {
  padding: 10px 25px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.subscribe-btn:hover {
  background-color: #3a7bc8;
}

.subscribe-btn.subscribed {
  background-color: #28a745;
}

.product-section {
  margin-bottom: 40px;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.detail-item {
  display: flex;
  background-color: #f9f9f9;
  border-radius: 4px;
  overflow: hidden;
}

.label {
  width: 120px;
  padding: 15px;
  background-color: #f0f0f0;
  font-weight: 500;
}

.value {
  flex: 1;
  padding: 15px;
}

.highlight {
  color: #e74c3c;
  font-weight: bold;
  font-size: 18px;
}

.rate-table-container {
  overflow-x: auto;
}

.rate-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}

.rate-table th {
  background-color: #f8f9fa;
  padding: 12px;
  font-weight: 600;
  border-bottom: 2px solid #ddd;
}

.rate-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.rate-table tr.best-rate {
  background-color: #e8f4fc;
}

.rate-table tr.best-rate td:nth-child(2),
.rate-table tr.best-rate td:nth-child(3) {
  color: #e74c3c;
  font-weight: bold;
}

.product-description, .product-etc {
  line-height: 1.6;
  color: #444;
}

.no-data {
  text-align: center;
  padding: 30px;
  color: #999;
  background-color: #f9f9f9;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .product-header {
    flex-direction: column;
    text-align: center;
  }
  
  .bank-logo {
    margin: 0 auto 20px;
  }
}

.subscribe-btn.cancel-btn {
  background-color: #dc3545;
}

.subscribe-btn.cancel-btn:hover {
  background-color: #c82333;
}
</style>