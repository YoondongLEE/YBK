<template>
  <div class="interest-compare-container">
    <h1>금리 비교</h1>
    
    <div class="tabs">
      <div 
        @click="activeTab = 'deposits'" 
        :class="{ active: activeTab === 'deposits' }"
        class="tab"
      >
        정기예금
      </div>
      <div 
        @click="activeTab = 'savings'" 
        :class="{ active: activeTab === 'savings' }"
        class="tab"
      >
        정기적금
      </div>
    </div>
    
    <!-- 정기예금 데이터 -->
    <div v-if="activeTab === 'deposits'" class="tab-content">
      <div v-if="loadingDeposits" class="loading">
        정기예금 상품 정보를 불러오는 중...
      </div>
      <div v-else>
        <h2>정기예금 금리 비교</h2>
        
        <!-- 필터 및 정렬 옵션 -->
        <div class="filter-row">
          <div class="filter-group">
            <label for="deposit-bank">은행:</label>
            <select id="deposit-bank" v-model="selectedDepositBank">
              <option value="">전체</option>
              <option v-for="bank in bankList" :key="bank.fin_co_no" :value="bank.fin_co_no">
                {{ bank.kor_co_nm }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="deposit-term">가입기간:</label>
            <select id="deposit-term" v-model="selectedDepositTerm">
              <option value="">전체</option>
              <option v-for="term in depositTerms" :key="term" :value="term">
                {{ term }}개월
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="deposit-sort">정렬:</label>
            <select id="deposit-sort" v-model="depositSortBy">
              <option value="rate">금리 높은순</option>
              <option value="bank">은행명</option>
              <option value="name">상품명</option>
            </select>
          </div>
        </div>
        
        <!-- 정기예금 상품 테이블 -->
        <table class="rate-table">
          <thead>
            <tr>
              <th>은행명</th>
              <th>상품명</th>
              <th>6개월</th>
              <th>12개월</th>
              <th>24개월</th>
              <th>36개월</th>
              <th>가입방법</th>
              <th>상세보기</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in filteredDepositProducts" :key="product.fin_prdt_cd">
              <td>{{ getBankName(product) }}</td>
              <td class="product-name-cell">{{ product.fin_prdt_nm }}</td>
              <td>{{ getInterestRateForTerm(product, '6') }}</td>
              <td>{{ getInterestRateForTerm(product, '12') }}</td>
              <td>{{ getInterestRateForTerm(product, '24') }}</td>
              <td>{{ getInterestRateForTerm(product, '36') }}</td>
              <td class="join-way-cell">{{ product.join_way }}</td>
              <td>
                <router-link :to="{ name: 'deposit-detail', params: { id: product.fin_prdt_cd } }" class="detail-btn">
                  상세보기
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 정기적금 데이터 -->
    <div v-if="activeTab === 'savings'" class="tab-content">
      <div v-if="loadingSavings" class="loading">
        정기적금 상품 정보를 불러오는 중...
      </div>
      <div v-else>
        <h2>정기적금 금리 비교</h2>
        
        <!-- 필터 및 정렬 옵션 -->
        <div class="filter-row">
          <div class="filter-group">
            <label for="saving-bank">은행:</label>
            <select id="saving-bank" v-model="selectedSavingBank">
              <option value="">전체</option>
              <option v-for="bank in bankList" :key="bank.fin_co_no" :value="bank.fin_co_no">
                {{ bank.kor_co_nm }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="saving-term">가입기간:</label>
            <select id="saving-term" v-model="selectedSavingTerm">
              <option value="">전체</option>
              <option v-for="term in savingTerms" :key="term" :value="term">
                {{ term }}개월
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="saving-sort">정렬:</label>
            <select id="saving-sort" v-model="savingSortBy">
              <option value="rate">금리 높은순</option>
              <option value="bank">은행명</option>
              <option value="name">상품명</option>
            </select>
          </div>
        </div>
        
        <!-- 정기적금 상품 테이블 -->
        <table class="rate-table">
          <thead>
            <tr>
              <th>은행명</th>
              <th>상품명</th>
              <th>6개월</th>
              <th>12개월</th>
              <th>24개월</th>
              <th>36개월</th>
              <th>가입방법</th>
              <th>상세보기</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in filteredSavingProducts" :key="product.fin_prdt_cd">
              <td>{{ getBankName(product) }}</td>
              <td class="product-name-cell">{{ product.fin_prdt_nm }}</td>
              <td>{{ getInterestRateForTerm(product, '6') }}</td>
              <td>{{ getInterestRateForTerm(product, '12') }}</td>
              <td>{{ getInterestRateForTerm(product, '24') }}</td>
              <td>{{ getInterestRateForTerm(product, '36') }}</td>
              <td class="join-way-cell">{{ product.join_way }}</td>
              <td>
                <router-link :to="{ name: 'saving-detail', params: { id: product.fin_prdt_cd } }" class="detail-btn">
                  상세보기
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../api';

// 상태 관리
const activeTab = ref('deposits');
const loadingDeposits = ref(true);
const loadingSavings = ref(true);
const depositProducts = ref([]);
const savingProducts = ref([]);
const banks = ref([]);

// 은행 필터링 상태 추가
const selectedDepositBank = ref('');
const selectedSavingBank = ref('');

// 필터 및 정렬 상태
const selectedDepositTerm = ref('');
const depositSortBy = ref('rate');
const selectedSavingTerm = ref('');
const savingSortBy = ref('rate');

// 은행 목록
const bankList = computed(() => {
  return banks.value.sort((a, b) => a.kor_co_nm.localeCompare(b.kor_co_nm));
});

// 은행 정보 로드
const fetchBanks = async () => {
  try {
    const response = await api.get('/banks/');
    banks.value = response.data;
    console.log('은행 정보 로드 완료:', banks.value.length);
  } catch (error) {
    console.error('은행 정보 로드 실패:', error);
  }
};

// 은행명 가져오기
const getBankName = (product) => {
  if (!product) return '정보 없음';
  
  // 1. bank가 객체인 경우
  if (product.bank && typeof product.bank === 'object' && product.bank.kor_co_nm) {
    return product.bank.kor_co_nm;
  }
  
  // 2. bank가 ID 문자열인 경우 (bank 객체에서 찾기)
  if (product.bank && typeof product.bank === 'string') {
    const bankObj = banks.value.find(b => b.fin_co_no === product.bank);
    if (bankObj) return bankObj.kor_co_nm;
  }
  
  // 3. bank_name 속성이 있는 경우
  if (product.bank_name) {
    return product.bank_name;
  }
  
  // 4. fin_co_no로 직접 검색
  if (product.fin_co_no) {
    const bankObj = banks.value.find(b => b.fin_co_no === product.fin_co_no);
    if (bankObj) return bankObj.kor_co_nm;
  }
  
  return '정보 없음';
};

// 특정 기간에 대한 금리 정보 가져오기
const getInterestRateForTerm = (product, term) => {
  if (!product || !product.options) return '-';
  
  // 해당 기간의 옵션 찾기
  const option = product.options.find(opt => opt.save_trm === term);
  if (!option) return '-';
  
  // 우대금리가 있으면 "기본금리 (우대금리)" 형식으로 표시
  const baseRate = parseFloat(option.intr_rate || 0).toFixed(2);
  const primeRate = option.intr_rate2 && parseFloat(option.intr_rate2) > 0 
    ? parseFloat(option.intr_rate2).toFixed(2) 
    : null;
  
  return primeRate 
    ? `${baseRate}% (${primeRate}%)`
    : `${baseRate}%`;
};

// 정기예금 상품 로드
const fetchDepositProducts = async () => {
  try {
    loadingDeposits.value = true;
    const response = await api.get('/deposits/');
    
    // 데이터가 없으면 API에서 새로 가져오기
    if (response.data.length === 0) {
      console.log('정기예금 데이터가 없어 API에서 불러옵니다...');
      await api.get('/save-deposit-products/');
      const newResponse = await api.get('/deposits/');
      depositProducts.value = newResponse.data;
    } else {
      depositProducts.value = response.data;
    }
  } catch (error) {
    console.error('정기예금 상품 로드 실패:', error);
    
    // 오류 발생 시 API에서 직접 데이터 가져오기 시도
    try {
      await api.get('/save-deposit-products/');
      const newResponse = await api.get('/deposits/');
      depositProducts.value = newResponse.data;
    } catch (e) {
      console.error('정기예금 데이터 복구 실패:', e);
    }
  } finally {
    loadingDeposits.value = false;
  }
};

// 정기적금 상품 로드
const fetchSavingProducts = async () => {
  try {
    loadingSavings.value = true;
    const response = await api.get('/savings/');
    
    // 데이터가 없으면 API에서 새로 가져오기
    if (response.data.length === 0) {
      console.log('정기적금 데이터가 없어 API에서 불러옵니다...');
      await api.get('/save-saving-products/');
      const newResponse = await api.get('/savings/');
      savingProducts.value = newResponse.data;
    } else {
      savingProducts.value = response.data;
    }
  } catch (error) {
    console.error('정기적금 상품 로드 실패:', error);
    
    // 오류 발생 시 API에서 직접 데이터 가져오기 시도
    try {
      await api.get('/save-saving-products/');
      const newResponse = await api.get('/savings/');
      savingProducts.value = newResponse.data;
    } catch (e) {
      console.error('정기적금 데이터 복구 실패:', e);
    }
  } finally {
    loadingSavings.value = false;
  }
};

// 정기예금 가입기간 옵션
const depositTerms = computed(() => {
  const terms = new Set();
  depositProducts.value.forEach(product => {
    if (product.options) {
      product.options.forEach(option => {
        if (option.save_trm) {
          terms.add(option.save_trm);
        }
      });
    }
  });
  return [...terms].sort((a, b) => a - b);
});

// 정기적금 가입기간 옵션
const savingTerms = computed(() => {
  const terms = new Set();
  savingProducts.value.forEach(product => {
    if (product.options) {
      product.options.forEach(option => {
        if (option.save_trm) {
          terms.add(option.save_trm);
        }
      });
    }
  });
  return [...terms].sort((a, b) => a - b);
});

// 선택된 옵션에 따른 정기예금 상품 필터링
const selectedOptions = (product) => {
  if (!product.options) return [];
  
  if (selectedDepositTerm.value) {
    return product.options.filter(option => option.save_trm === selectedDepositTerm.value);
  }
  
  // 모든 기간 중 최고금리 옵션 선택
  const maxRateOption = product.options.reduce((max, current) => {
    const currentRate = parseFloat(current.intr_rate2) || parseFloat(current.intr_rate) || 0;
    const maxRate = parseFloat(max.intr_rate2) || parseFloat(max.intr_rate) || 0;
    return currentRate > maxRate ? current : max;
  }, { intr_rate: '0', intr_rate2: '0' });
  
  return [maxRateOption];
};

// 선택된 옵션에 따른 정기적금 상품 필터링
const selectedSavingOptions = (product) => {
  if (!product.options) return [];
  
  if (selectedSavingTerm.value) {
    return product.options.filter(option => option.save_trm === selectedSavingTerm.value);
  }
  
  // 모든 기간 중 최고금리 옵션 선택
  const maxRateOption = product.options.reduce((max, current) => {
    const currentRate = parseFloat(current.intr_rate2) || parseFloat(current.intr_rate) || 0;
    const maxRate = parseFloat(max.intr_rate2) || parseFloat(max.intr_rate) || 0;
    return currentRate > maxRate ? current : max;
  }, { intr_rate: '0', intr_rate2: '0' });
  
  return [maxRateOption];
};

// 정기예금 상품 필터링 및 정렬
const filteredDepositProducts = computed(() => {
  // 필터링 함수
  const filterProducts = () => {
    return depositProducts.value.filter(product => {
      // 은행 필터
      if (selectedDepositBank.value && product.fin_co_no !== selectedDepositBank.value) {
        // bank가 문자열인 경우
        if (typeof product.bank === 'string' && product.bank !== selectedDepositBank.value) {
          return false;
        }
        // bank가 객체인 경우
        if (product.bank && typeof product.bank === 'object' && product.bank.fin_co_no !== selectedDepositBank.value) {
          return false;
        }
      }
      
      // 기간 필터
      if (selectedDepositTerm.value) {
        if (!product.options) return false;
        return product.options.some(option => 
          option.save_trm === selectedDepositTerm.value
        );
      }
      return true;
    });
  };
  
  // 정렬 함수
  const sortProducts = (products) => {
    return [...products].sort((a, b) => {
      // 금리 높은순
      if (depositSortBy.value === 'rate') {
        const aRate = getMaxRate(a);
        const bRate = getMaxRate(b);
        return bRate - aRate;
      } 
      // 은행명순
      else if (depositSortBy.value === 'bank') {
        return getBankName(a).localeCompare(getBankName(b));
      } 
      // 상품명순
      else if (depositSortBy.value === 'name') {
        return a.fin_prdt_nm.localeCompare(b.fin_prdt_nm);
      }
      return 0;
    });
  };
  
  return sortProducts(filterProducts());
});

// 정기적금 상품 필터링 및 정렬
const filteredSavingProducts = computed(() => {
  // 필터링 함수
  const filterProducts = () => {
    return savingProducts.value.filter(product => {
      // 은행 필터
      if (selectedSavingBank.value && product.fin_co_no !== selectedSavingBank.value) {
        // bank가 문자열인 경우
        if (typeof product.bank === 'string' && product.bank !== selectedSavingBank.value) {
          return false;
        }
        // bank가 객체인 경우
        if (product.bank && typeof product.bank === 'object' && product.bank.fin_co_no !== selectedSavingBank.value) {
          return false;
        }
      }
      
      // 기간 필터
      if (selectedSavingTerm.value) {
        if (!product.options) return false;
        return product.options.some(option => 
          option.save_trm === selectedSavingTerm.value
        );
      }
      return true;
    });
  };
  
  // 정렬 함수
  const sortProducts = (products) => {
    return [...products].sort((a, b) => {
      // 금리 높은순
      if (savingSortBy.value === 'rate') {
        const aRate = getMaxRate(a);
        const bRate = getMaxRate(b);
        return bRate - aRate;
      } 
      // 은행명순
      else if (savingSortBy.value === 'bank') {
        return getBankName(a).localeCompare(getBankName(b));
      } 
      // 상품명순
      else if (savingSortBy.value === 'name') {
        return a.fin_prdt_nm.localeCompare(b.fin_prdt_nm);
      }
      return 0;
    });
  };
  
  return sortProducts(filterProducts());
});

// 최대금리 계산 (정렬용)
const getMaxRate = (product) => {
  if (!product.options || !product.options.length) return 0;
  
  let maxRate = 0;
  product.options.forEach(option => {
    const rate = parseFloat(option.intr_rate2) || parseFloat(option.intr_rate) || 0;
    if (rate > maxRate) maxRate = rate;
  });
  
  return maxRate;
};

// 기본금리 표시
const getBaseRate = (option) => {
  if (!option || !option.intr_rate) return '-';
  return parseFloat(option.intr_rate).toFixed(2);
};

// 우대금리 여부 확인
const hasPrimeRate = (option) => {
  return option && option.intr_rate2 && parseFloat(option.intr_rate2) > 0;
};

// 우대금리 표시
const getPrimeRate = (option) => {
  if (!hasPrimeRate(option)) return '-';
  return parseFloat(option.intr_rate2).toFixed(2);
};

onMounted(async () => {
  // 은행 정보 먼저 로드
  await fetchBanks();
  
  // 상품 정보 로드
  fetchDepositProducts();
  fetchSavingProducts();
});
</script>

<style scoped>
.interest-compare-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 30px;
  color: #333;
}

h2 {
  margin: 30px 0 20px;
  color: #444;
}

.tabs {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 30px;
}

.tab {
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
  margin-right: 10px;
  font-weight: 500;
}

.tab:hover {
  color: #4a90e2;
}

.tab.active {
  color: #4a90e2;
  border-bottom: 3px solid #4a90e2;
}

.tab-content {
  animation: fadeIn 0.3s ease-in;
  width: 100%;
  overflow-x: hidden; /* 가로 스크롤 방지 */
}

.filter-row {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-group {
  display: flex;
  align-items: center;
  margin-right: 20px;
}

.filter-group label {
  margin-right: 10px;
  font-weight: 500;
  white-space: nowrap;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  min-width: 150px;
}

/* 테이블 스타일 수정 */
.rate-table {
  width: 100%; /* 테이블 너비 100% */
  border-collapse: collapse;
  margin: 20px 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background: white;
  table-layout: fixed; /* 고정된 테이블 레이아웃 */
  display: table; /* block에서 table로 변경 */
}

.rate-table th {
  background-color: #f8f9fa;
  padding: 12px 8px; /* 좌우 패딩 줄임 */
  text-align: left;
  border-bottom: 2px solid #ddd;
  font-weight: 600;
  color: #444;
  font-size: 14px; /* 폰트 사이즈 작게 */
}

.rate-table td {
  padding: 12px 8px; /* 좌우 패딩 줄임 */
  border-bottom: 1px solid #eee;
  word-wrap: break-word; /* 단어 중간에도 줄바꿈 허용 */
  overflow-wrap: break-word; /* 브라우저 호환성 */
  font-size: 14px; /* 폰트 사이즈 작게 */
  vertical-align: top; /* 상단 정렬 */
}

/* 각 열의 너비 조정 */
.rate-table th:nth-child(1), 
.rate-table td:nth-child(1) { /* 은행명 */
  width: 15%;
}

.rate-table th:nth-child(2), 
.rate-table td:nth-child(2) { /* 상품명 */
  width: 20%;
  white-space: normal; /* 줄바꿈 허용 */
}

.rate-table th:nth-child(3), 
.rate-table th:nth-child(4), 
.rate-table th:nth-child(5), 
.rate-table th:nth-child(6),
.rate-table td:nth-child(3), 
.rate-table td:nth-child(4), 
.rate-table td:nth-child(5), 
.rate-table td:nth-child(6) { /* 금리 열 */
  width: 10%;
  text-align: center;
}

.rate-table th:nth-child(7), 
.rate-table td:nth-child(7) { /* 가입방법 */
  width: 15%;
  white-space: normal; /* 줄바꿈 허용 */
}

.rate-table th:nth-child(8), 
.rate-table td:nth-child(8) { /* 상세보기 */
  width: 10%;
  text-align: center;
}

.rate-table tr:hover {
  background-color: #f8f9fa;
}

.detail-btn {
  display: inline-block;
  padding: 6px 12px;
  background-color: #4a90e2;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  font-size: 13px; /* 버튼 텍스트 사이즈 작게 */
  transition: background-color 0.3s;
  white-space: nowrap;
}

.detail-btn:hover {
  background-color: #3a7bc8;
}

.loading {
  text-align: center;
  padding: 50px;
  color: #666;
  font-size: 16px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
  }
  
  .filter-group {
    margin-bottom: 10px;
  }
  
  /* 모바일 테이블 조정 */
  .rate-table th,
  .rate-table td {
    font-size: 12px;
    padding: 8px 4px;
  }
  
  .detail-btn {
    padding: 4px 8px;
    font-size: 12px;
  }
}

.product-name-cell {
  white-space: normal !important;
  word-break: keep-all;
  hyphens: auto;
  max-width: 200px;
  line-height: 1.4;
}

.join-way-cell {
  white-space: normal !important;
  word-break: keep-all;
  line-height: 1.4;
}
</style>