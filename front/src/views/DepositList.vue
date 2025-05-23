<template>
  <div class="deposit-list-container">
    <h1>정기예금 금리비교</h1>
    
    <div class="filters">
      <!-- 권역 필터는 제거 -->
      
      <div class="filter-group">
        <label>은행:</label>
        <select v-model="selectedBank">
          <option value="">모든 금융기관</option>
          <option v-for="bank in filteredBanks" :key="bank.id" :value="bank.id">
            {{ bank.kor_co_nm }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>가입기간:</label>
        <select v-model="selectedTerm">
          <option value="">모든 기간</option>
          <option v-for="term in availableTerms" :key="term" :value="term">
            {{ term }}개월
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>정렬:</label>
        <select v-model="sortField">
          <option value="">정렬 기준 선택</option>
          <option v-for="term in availableTerms" :key="term" :value="term">
            {{ term }}개월 금리순
          </option>
        </select>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading">데이터를 불러오는 중...</div>
    
    <div v-else>
      <!-- 성공/에러 메시지 표시 영역 -->
      <div v-if="message" :class="['status-message', message.type]">
        {{ message.text }}
      </div>
      
      <div class="action-buttons">
        <button @click="refreshData" class="refresh-btn">
          최신 데이터 가져오기
        </button>
      </div>
      
      <table class="deposit-table" v-if="products.length">
        <thead>
          <tr>
            <th>권역</th>
            <th>금융기관</th>
            <th>상품명</th>
            <th v-for="period in tablePeriods" :key="period">
              {{ period }}개월
            </th>
            <th>가입방법</th>
            <th>상세보기</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in sortedProducts" :key="product.id">
            <td>{{ getSectorName(product.bank.sector_code) }}</td>
            <td>{{ product.bank.kor_co_nm }}</td>
            <td>{{ product.fin_prdt_nm }}</td>
            <td v-for="period in tablePeriods" :key="period" :class="{'best-rate': isBestRate(product, period)}">
              {{ getRate(product, period) || '-' }}%
            </td>
            <td>{{ product.join_way }}</td>
            <td>
              <router-link :to="{ name: 'depositDetail', params: { id: product.id } }">
                상세보기
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-else class="no-data">
        표시할 상품이 없습니다.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const banks = ref([])
const products = ref([])
const selectedBank = ref('')
const selectedTerm = ref('')
const sortField = ref('')
const isLoading = ref(true)
const message = ref(null)
const sectors = ref({})  // 권역코드 목록은 유지 (테이블 표시용)

// etc가 배열인지 단일 객체인지 안전하게 리스트로 변환
const safeList = (data) => Array.isArray(data) ? data : data ? [data] : []

// 은행 필터링 (이제 모든 은행이 표시됨)
const filteredBanks = computed(() => banks.value)

// 테이블에 표시할 전체 가입기간 목록
const tablePeriods = computed(() => {
  const set = new Set()
  products.value.forEach(p => {
    safeList(p.etc).forEach(o => set.add(Number(o.save_trm)))
  })
  return Array.from(set).sort((a, b) => a - b)
})

// 필터 선택용 가입기간 목록
const availableTerms = computed(() => {
  return tablePeriods.value
})

// 권역 이름 조회 함수
const getSectorName = (code) => {
  return sectors.value[code] || '기타'
}

// API에서 권역코드 목록 가져오기
const fetchSectors = async () => {
  try {
    const response = await api.get('/sectors/')
    sectors.value = response.data
  } catch (e) {
    console.error('권역코드 로딩 실패:', e)
  }
}

// API에서 은행 & 상품 데이터 불러오기
const fetchData = async () => {
  try {
    isLoading.value = true
    const [bRes, pRes] = await Promise.all([
      api.get('/banks/'),
      api.get('/deposits/'),
    ])
    banks.value = bRes.data
    products.value = pRes.data
  } catch (e) {
    console.error('데이터 로딩 실패:', e)
  } finally {
    isLoading.value = false
  }
}

// 최신 데이터 가져오기 (금감원 API 호출)
const refreshData = async () => {
  try {
    isLoading.value = true
    
    // 모든 권역의 데이터 가져오기
    const response = await api.get('/save-deposit-products/')
    console.log('API 응답:', response.data)
    
    // 데이터 갱신 후 목록 다시 불러오기
    await fetchData()
    
    // 성공 메시지를 알림창 대신 상태 메시지로 표시
    message.value = {
      type: 'success',
      text: `최신 데이터로 업데이트 완료 (${response.data.count || 0}개 상품)`
    }
    
    // 3초 후 메시지 자동 제거
    setTimeout(() => {
      message.value = null
    }, 3000)
  } catch (e) {
    console.error('데이터 갱신 실패:', e)
    
    // 에러 발생 시에만 알림창 표시
    let errorMessage = '데이터 갱신에 실패했습니다.'
    
    // 서버에서 보낸 에러 메시지가 있으면 표시
    if (e.response && e.response.data && e.response.data.error) {
      errorMessage += `\n원인: ${e.response.data.error}`
    }
    
    alert(errorMessage)
  } finally {
    isLoading.value = false
  }
}

// 가입기간(term)에 해당하는 금리 꺼내기
const getRate = (product, term) => {
  const opt = safeList(product.etc).find(x => Number(x.save_trm) === term)
  return opt?.intr_rate
}

// 해당 기간의 최고 금리 상품인지 확인
const isBestRate = (product, term) => {
  const currentRate = getRate(product, term)
  if (!currentRate) return false
  
  // 현재 선택된 필터에 맞는 상품들 중에서 최고 금리 찾기
  const maxRate = Math.max(...sortedProducts.value
    .map(p => getRate(p, term) || 0)
    .filter(rate => rate > 0)
  )
  
  return Number(currentRate) === maxRate && maxRate > 0
}

// 필터·정렬 적용된 리스트
const sortedProducts = computed(() => {
  let list = products.value

  // 은행 필터 적용
  if (selectedBank.value) {
    list = list.filter(p => p.bank.id === Number(selectedBank.value))
  }
  
  // 가입기간 필터 적용
  if (selectedTerm.value) {
    const term = Number(selectedTerm.value)
    list = list.filter(p =>
      safeList(p.etc).some(o => Number(o.save_trm) === term)
    )
  }
  
  // 금리 기준 정렬
  if (sortField.value) {
    const term = Number(sortField.value)
    list = [...list].sort((a, b) => {
      const rateA = getRate(a, term) || 0
      const rateB = getRate(b, term) || 0
      return Number(rateB) - Number(rateA) // 내림차순 정렬
    })
  }
  
  return list
})

onMounted(async () => {
  await fetchSectors()  // 권역코드 먼저 가져오기
  await fetchData()     // 데이터 로드
})
</script>

<style scoped>
.deposit-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: bold;
  min-width: 80px;
}

select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 200px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.sector-select {
  min-width: 150px;
  margin-left: 10px;
}

.deposit-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.deposit-table th, 
.deposit-table td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: center;
}

.deposit-table th {
  background-color: #f0f0f0;
}

.deposit-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.best-rate {
  font-weight: bold;
  color: #ff5722;
  background-color: #fff8e1;
}

.loading, .no-data {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}

.refresh-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.refresh-btn:hover {
  background-color: #388e3c;
}

/* 상태 메시지 스타일 */
.status-message {
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 15px;
  animation: fadeIn 0.3s;
  transition: opacity 0.3s;
}

.status-message.success {
  background-color: #e8f5e9;
  color: #2e7d32;
  border-left: 4px solid #4caf50;
}

.status-message.error {
  background-color: #ffebee;
  color: #c62828;
  border-left: 4px solid #f44336;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 반응형 스타일 */
@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    gap: 10px;
  }
  
  .deposit-table {
    font-size: 14px;
  }
  
  .deposit-table th,
  .deposit-table td {
    padding: 8px 5px;
  }
}
</style>