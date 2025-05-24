<template>
  <div class="deposit-list-container">
    <!-- 필터링 및 정렬 옵션 -->
    <div class="filters">
      <div class="filter-group">
        <label>은행:</label>
        <select v-model="selectedBank">
          <option value="">모든 금융기관</option>
          <option v-for="bank in banks" :key="bank.fin_co_no" :value="bank.fin_co_no">
            {{ bank.kor_co_nm }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>가입기간:</label>
        <select v-model="selectedTerm">
          <option value="">모든 기간</option>
          <option v-for="term in displayPeriods" :key="term" :value="term">
            {{ term }}개월
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>정렬:</label>
        <select v-model="sortBy">
          <option value="rate">금리 높은순</option>
          <option value="name">상품명</option>
          <option value="bank">은행명</option>
        </select>
      </div>

      <!-- 관리자용 새로고침 버튼 -->
      <button 
        v-if="isAdmin" 
        @click="refreshData" 
        class="refresh-btn"
        :disabled="loading"
      >
        {{ loading ? '갱신 중...' : '최신 데이터로 갱신' }}
      </button>
    </div>
    
    <!-- 상태 메시지 (성공/에러) -->
    <div 
      v-if="message" 
      class="status-message" 
      :class="message.type"
    >
      {{ message.text }}
    </div>
    
    <div v-if="loading" class="loading">
      <p>예금 상품 데이터를 불러오는 중...</p>
    </div>
    
    <div v-else-if="filteredProducts.length === 0" class="no-products">
      <p>조건에 맞는 예금 상품이 없습니다.</p>
    </div>
    
    <!-- 상품 테이블 -->
    <table v-else class="products-table">
      <thead>
        <tr>
          <th>금융기관</th>
          <th>상품명</th>
          <th v-for="period in displayPeriods" :key="period">{{ period }}개월</th>
          <th>우대조건</th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="product in filteredProducts" 
          :key="product.fin_prdt_cd"
          @click="goToDetail(product.fin_prdt_cd)"
          class="product-row"
        >
          <td>{{ product.kor_co_nm }}</td>
          <td>{{ product.fin_prdt_nm }}</td>
          <td 
            v-for="period in displayPeriods" 
            :key="period"
            :class="{ 'best-rate': isBestRate(product, period) }"
          >
            {{ getRateForPeriod(product, period) }}
          </td>
          <td>
            <span v-if="product.spcl_cnd" class="benefits-preview">
              {{ getBenefitsPreview(product.spcl_cnd) }}
            </span>
            <span v-else>-</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import api from '@/api';

const router = useRouter();
const authStore = useAuthStore();
const products = ref([]);
const banks = ref([]);
const loading = ref(true);
const selectedBank = ref('');
const selectedTerm = ref('');
const sortBy = ref('rate');
const message = ref(null);

// 가능한 기간들 - 더 많은 기간 추가
const displayPeriods = [1, 3, 6, 12, 24, 36];

// 관리자 권한 확인
const isAdmin = computed(() => authStore.user?.is_staff || false);

// 필터링된 상품 목록
const filteredProducts = computed(() => {
  let result = [...products.value];
  
  // 은행 필터링
  if (selectedBank.value) {
    result = result.filter(product => product.bank?.fin_co_no === selectedBank.value);
  }
  
  // 가입기간 필터링
  if (selectedTerm.value) {
    result = result.filter(product => {
      const options = product.options || [];
      return options.some(option => 
        parseInt(option.save_trm) === parseInt(selectedTerm.value)
      );
    });
  }
  
  // 정렬
  result.sort((a, b) => {
    if (sortBy.value === 'rate') {
      const aMaxRate = getMaxRate(a);
      const bMaxRate = getMaxRate(b);
      return bMaxRate - aMaxRate; // 내림차순 (높은 금리부터)
    } else if (sortBy.value === 'name') {
      return a.fin_prdt_nm.localeCompare(b.fin_prdt_nm);
    } else if (sortBy.value === 'bank') {
      return a.kor_co_nm.localeCompare(b.kor_co_nm);
    }
    return 0;
  });
  
  return result;
});

// 최대 금리 계산
const getMaxRate = (product) => {
  if (!product.options || product.options.length === 0) return 0;
  
  let maxRate = 0;
  product.options.forEach(option => {
    const rate = parseFloat(option.intr_rate2) || parseFloat(option.intr_rate) || 0;
    if (rate > maxRate) maxRate = rate;
  });
  
  return maxRate;
};

// 특정 기간의 금리 표시
const getRateForPeriod = (product, period) => {
  if (!product.options) return '-';
  
  const option = product.options.find(opt => parseInt(opt.save_trm) === period);
  if (!option) return '-';
  
  // 우대금리가 있으면 우대금리, 없으면 기본금리 표시
  const rate = option.intr_rate2 ? option.intr_rate2 : option.intr_rate;
  return rate ? `${rate}%` : '-';
};

// 특정 기간에 대해 최고 금리인지 확인
const isBestRate = (product, period) => {
  if (!product.options) return false;
  
  const option = product.options.find(opt => parseInt(opt.save_trm) === period);
  if (!option) return false;
  
  const rate = parseFloat(option.intr_rate2) || parseFloat(option.intr_rate) || 0;
  if (rate === 0) return false;
  
  // 모든 상품 중 해당 기간의 최고 금리 찾기
  let maxRate = 0;
  products.value.forEach(p => {
    if (!p.options) return;
    const opt = p.options.find(o => parseInt(o.save_trm) === period);
    if (opt) {
      const r = parseFloat(opt.intr_rate2) || parseFloat(opt.intr_rate) || 0;
      if (r > maxRate) maxRate = r;
    }
  });
  
  return rate === maxRate && maxRate > 0;
};

// 우대조건 미리보기 (너무 길면 잘라서 보여줌)
const getBenefitsPreview = (text) => {
  if (!text) return '-';
  return text.length > 30 ? text.substring(0, 30) + '...' : text;
};

// 데이터 불러오기
const fetchData = async () => {
  loading.value = true;
  message.value = null;
  
  try {
    // 은행 정보 로드
    const banksResponse = await api.get('/banks/');
    banks.value = banksResponse.data;
    
    // 예금 상품 로드
    const productsResponse = await api.get('/deposits/');
    
    // 데이터가 없으면 API에서 새로 가져오기
    if (productsResponse.data.length === 0) {
      await api.get('/save-deposit-products/');
      const newProductsResponse = await api.get('/deposits/');
      products.value = newProductsResponse.data;
    } else {
      products.value = productsResponse.data;
    }
    
  } catch (error) {
    console.error('예금 상품 데이터 로딩 실패:', error);
    message.value = {
      type: 'error',
      text: '예금 상품 데이터를 불러오는데 실패했습니다.'
    };
    
    // 데이터 불러오기 실패 시 API 호출 시도
    try {
      await api.get('/save-deposit-products/');
      const newProductsResponse = await api.get('/deposits/');
      products.value = newProductsResponse.data;
    } catch (e) {
      console.error('API 호출 실패:', e);
    }
  } finally {
    loading.value = false;
  }
};

// 데이터 갱신 (관리자용)
const refreshData = async (showMessage = true) => {
  try {
    loading.value = true;
    if (showMessage) {
      message.value = {
        type: 'info',
        text: '금융 상품 데이터를 갱신 중입니다...'
      };
    }
    
    // 강제 새로고침 옵션 추가
    const response = await api.get('/save-deposit-products/', {
      params: { force_refresh: true }
    });
    
    // 데이터 갱신 여부 확인
    if (response.data.refresh) {
      // 새로 불러온 데이터가 있으면 목록 다시 불러오기
      const productsResponse = await api.get('/deposits/');
      products.value = productsResponse.data;
      
      message.value = {
        type: 'success',
        text: `최신 데이터로 업데이트 완료 (${response.data.count || 0}개 상품)`
      };
    } else {
      // 이미 데이터가 있어서 갱신하지 않은 경우
      message.value = {
        type: 'info',
        text: response.data.message
      };
    }
    
    // 3초 후 메시지 자동 제거
    setTimeout(() => {
      message.value = null;
    }, 3000);
  } catch (e) {
    console.error('데이터 갱신 실패:', e);
    
    message.value = {
      type: 'error',
      text: e.response?.data?.error || '데이터 갱신에 실패했습니다.'
    };
  } finally {
    loading.value = false;
  }
};


// 상세 페이지 이동
const goToDetail = (finPrdtCd) => {
  router.push({ name: 'deposit-detail', params: { id: finPrdtCd } });
};

// 컴포넌트 초기화
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.deposit-list-container {
  margin-bottom: 40px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
}

.filter-group label {
  margin-right: 8px;
  font-weight: 500;
  color: #495057;
}

select {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: white;
  min-width: 150px;
}

.products-table {
  width: 100%;
  border-collapse: collapse;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
}

.products-table th,
.products-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.products-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
}

.product-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.product-row:hover {
  background-color: #f1f8ff;
}

.best-rate {
  color: #28a745;
  font-weight: bold;
  position: relative;
}

.benefits-preview {
  display: block;
  max-width: 250px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.loading, .no-products {
  padding: 30px;
  text-align: center;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: 20px;
  color: #6c757d;
}

.refresh-btn {
  padding: 8px 12px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  margin-left: auto;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #43a047;
}

.refresh-btn:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.status-message {
  padding: 12px 15px;
  margin-bottom: 15px;
  border-radius: 4px;
}

.status-message.success {
  background-color: #d4edda;
  color: #155724;
  border-left: 4px solid #28a745;
}

.status-message.error {
  background-color: #f8d7da;
  color: #721c24;
  border-left: 4px solid #dc3545;
}

.status-message.info {
  background-color: #cce5ff;
  color: #004085;
  border-left: 4px solid #007bff;
}
</style>