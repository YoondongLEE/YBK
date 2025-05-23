<template>
  <div class="deposit-list">
    <h2>정기예금</h2>
    
    <!-- 검색 필터 섹션 -->
    <div class="search-section">
      <div class="search-box">
        <h3>검색하기</h3>
        <div class="search-filters">
          <div class="filter-item">
            <label>은행을 선택하세요</label>
            <select v-model="selectedBank">
              <option value="">전체은행</option>
              <option v-for="bank in banks" :key="bank.id" :value="bank.id">
                {{ bank.kor_co_nm }}
              </option>
            </select>
          </div>
          <div class="filter-item">
            <label>예치기간</label>
            <select v-model="selectedTerm">
              <option value="">전체기간</option>
              <option v-for="term in tablePeriods" :key="term" :value="term">
                {{ term }}개월
              </option>
            </select>
          </div>
          <button class="search-btn" @click="applyFilters">확인</button>
        </div>
      </div>
    </div>

    <!-- 상품 목록 테이블 -->
    <div class="products-table">
      <table>
        <thead>
          <tr>
            <th>공시 제출월</th>
            <th>금융회사</th>
            <th>상품명</th>
            <th
              v-for="term in tablePeriods"
              :key="term"
              @click="sortByRate(term)"
            >
              {{ term }}개월
              <span v-if="sortField === term">
                {{ sortAsc ? '▲' : '▼' }}
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="product in sortedProducts"
            :key="product.id"
            class="row"
          >
            <td>{{ product.dcls_month }}</td>
            <td>{{ product.bank.kor_co_nm }}</td>
            <td>
              <router-link
                :to="{ name: 'depositDetail', params: { id: product.id } }"
                class="product-link"
              >
                {{ product.fin_prdt_nm }}
              </router-link>
            </td>
            <td
              v-for="term in tablePeriods"
              :key="term"
            >
              {{ getRate(product, term) || '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter }      from 'vue-router'
import api                from '../api'

const banks        = ref([])
const products     = ref([])
const selectedBank = ref('')
const selectedTerm = ref('')
const sortField    = ref(null)
const sortAsc      = ref(false)
const router       = useRouter()

// etc가 배열인지 단일 객체인지 안전하게 리스트로 변환
const safeList = (data) => Array.isArray(data) ? data : data ? [data] : []

// 테이블에 표시할 전체 가입기간 목록
const tablePeriods = computed(() => {
  const set = new Set()
  products.value.forEach(p => {
    safeList(p.etc).forEach(o => set.add(Number(o.save_trm)))
  })
  return Array.from(set).sort((a, b) => a - b)
})

// API에서 은행 & 상품 데이터 불러오기
const fetchData = async () => {
  try {
    const [bRes, pRes] = await Promise.all([
      api.get('banks/'),
      api.get('deposits/'),
    ])
    banks.value    = bRes.data
    products.value = pRes.data
  } catch (e) {
    console.error('데이터 로딩 실패:', e)
  }
}

// 가입기간(term)에 해당하는 금리 꺼내기
const getRate = (product, term) => {
  const opt = safeList(product.etc).find(x => Number(x.save_trm) === term)
  return opt?.intr_rate
}

// 필터·정렬 적용된 리스트
const sortedProducts = computed(() => {
  let list = products.value

  if (selectedBank.value) {
    list = list.filter(p => p.bank.id === Number(selectedBank.value))
  }
  if (selectedTerm.value) {
    list = list.filter(p =>
      safeList(p.etc).some(o => Number(o.save_trm) === Number(selectedTerm.value))
    )
  }
  if (sortField.value != null) {
    list = [...list].sort((a, b) => {
      const ra = getRate(a, sortField.value) || 0
      const rb = getRate(b, sortField.value) || 0
      return sortAsc.value ? ra - rb : rb - ra
    })
  }
  return list
})

// 검색 버튼 클릭 (computed가 자동 반영)
const applyFilters = () => {}

// 컬럼 클릭 시 정렬 토글
const sortByRate = (term) => {
  if (sortField.value === term) {
    sortAsc.value = !sortAsc.value
  } else {
    sortField.value = term
    sortAsc.value   = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.deposit-list { padding: 20px; max-width: 1200px; margin: auto; }

/* 검색 섹션 */
.search-section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
.search-filters { display: flex; gap: 20px; align-items: flex-end; }
.filter-item label { font-weight: bold; }
.search-btn { background: #4a90e2; color: #fff; padding: 8px 20px; border: none; border-radius: 4px; cursor: pointer; }

/* 테이블 */
.products-table { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
th { background: #f8f9fa; cursor: pointer; }
.row:hover { background: #f5f5f5; }
.product-link {
  color: #4a90e2;
  text-decoration: none;
}
.product-link:hover {
  text-decoration: underline;
}
</style>
