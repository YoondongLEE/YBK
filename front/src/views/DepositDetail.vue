<template>
  <div v-if="product && product.bank" class="deposit-detail">
    <h1>정기예금 상세</h1>
    <div class="info-grid">
      <div><strong>공시 제출월:</strong> {{ product.dcls_month }}</div>
      <div><strong>금융회사:</strong> {{ product.bank.kor_co_nm }}</div>
      <div><strong>상품명:</strong> {{ product.fin_prdt_nm }}</div>
      <div><strong>가입 제한:</strong> {{ product.join_way }}</div>
      <div><strong>이자 지급 방식:</strong> {{ product.mtrt_int }}</div>
    </div>

    <!-- 가입기간별 금리 테이블 -->
    <table class="detail-table">
      <thead>
        <tr>
          <th v-for="opt in etcList" :key="opt.save_trm">
            {{ opt.save_trm }}개월
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td v-for="opt in etcList" :key="opt.save_trm">
            {{ opt.intr_rate }}%
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 가입하기 버튼 -->
    <button
      v-if="isLogin"
      class="subscribe-btn"
      @click="subscribeProduct"
      :disabled="subscribed"
    >
      {{ subscribed ? '이미 가입됨' : '가입하기' }}
    </button>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
  <div v-else class="loading">로딩중…</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute }      from 'vue-router'
import api                from '../api'

const route      = useRoute()
const product    = ref(null)
const message    = ref('')
const subscribed = ref(false)

// 로그인 여부 확인
const isLogin = computed(() => !!localStorage.getItem('token'))

// etc가 배열 혹은 객체일 때 모두 리스트로 변환
const etcList = computed(() => {
  const data = product.value?.etc
  if (Array.isArray(data)) return data
  return data ? [data] : []
})

// 상품 상세 조회
const fetchDetail = async () => {
  try {
    console.log('Fetching detail for ID:', route.params.id)
    // /api/ 제거
    const res = await api.get(`/deposits/${route.params.id}/`)
    console.log('API Response:', res.data)
    product.value = res.data
  } catch (e) {
    console.error('상세조회 실패:', e.response?.data || e.message)
  }
}

// 가입하기
const subscribeProduct = async () => {
  try {
    // /api/ 제거
    await api.post(`/deposits/${route.params.id}/subscribe/`)
    message.value = '가입 완료!'
    subscribed.value = true
  } catch (e) {
    console.error('가입 실패:', e)
    message.value = '가입에 실패했습니다'
  }
}

onMounted(fetchDetail)
</script>

<style scoped>
.deposit-detail {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px 20px;
  margin-bottom: 20px;
}
.detail-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}
.detail-table th,
.detail-table td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: center;
}
.subscribe-btn {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}
.subscribe-btn[disabled] {
  background-color: #ccc;
  cursor: default;
}
.message {
  margin-top: 10px;
  color: green;
}
.loading {
  text-align: center;
  padding: 50px;
  font-size: 1.2rem;
  color: #666;
}
</style>
