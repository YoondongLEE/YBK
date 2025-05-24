<template>
  <div class="deposit-list-page">
    <h1>정기예금 상품 목록</h1>
    <p class="description">다양한 은행의 정기예금 상품들의 금리를 확인해보세요.</p>
    
    <!-- 컴포넌트 사용 -->
    <DepositList />
  </div>
</template>

<script setup>
import DepositList from '@/components/finance/DepositList.vue';
</script>

<style scoped>
.deposit-list-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 10px;
}

.description {
  color: #666;
  margin-bottom: 30px;
}
</style>