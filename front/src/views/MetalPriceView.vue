<!-- filepath: /Users/iyundong/Desktop/SSAFY/1학기_관통/final-pjt-v1/final-pjt/front/src/views/MetalPriceView.vue -->
<template>
  <div class="metal-price-container">
    <h1>금/은 가격 변동 추이</h1>
    
    <p class="page-description">
      금과 은의 시간에 따른 가격 변동을 확인하고 분석해보세요. 
      원하는 기간을 설정하여 특정 시점의 가격 변화를 살펴볼 수 있습니다.
    </p>
    
    <MetalPriceChart />
    
    <div class="metal-info">
      <div class="info-card">
        <h2>금(Gold)이란?</h2>
        <p>
          금은 역사적으로 가치 저장 수단으로 사용되어 왔으며, 경제적 불확실성이 높을 때 안전 자산으로 여겨집니다.
          화폐로서의 역할, 보석류, 전자 산업 등 다양한 분야에서 활용됩니다.
        </p>
        <h3>투자 특성</h3>
        <ul>
          <li>인플레이션 헤지 효과</li>
          <li>달러 약세 시 가격 상승 경향</li>
          <li>장기적 가치 보존</li>
          <li>포트폴리오 다각화 도구</li>
        </ul>
      </div>
      
      <div class="info-card">
        <h2>은(Silver)이란?</h2>
        <p>
          은은 금보다 더 많은 산업적 용도를 가지고 있으며, 전기 전도성이 우수해 전자 제품, 태양 전지판, 의료 기기 등에 활용됩니다.
          또한 보석 및 장신구 제작에도 널리 사용됩니다.
        </p>
        <h3>투자 특성</h3>
        <ul>
          <li>산업 수요에 영향 받음</li>
          <li>금보다 변동성이 높음</li>
          <li>경제 회복기에 강세</li>
          <li>금/은 비율로 상대적 가치 평가</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import MetalPriceChart from '@/components/finance/MetalPriceChart.vue';

export default {
  name: 'MetalPriceView',
  components: {
    MetalPriceChart
  }
};
</script>

<style scoped>
.metal-price-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

.page-description {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
  line-height: 1.5;
}

.metal-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.info-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.info-card h2 {
  color: #444;
  margin-bottom: 15px;
  font-size: 20px;
}

.info-card h3 {
  color: #555;
  margin: 15px 0 10px;
  font-size: 16px;
}

.info-card p {
  color: #666;
  margin-bottom: 15px;
  line-height: 1.5;
}

.info-card ul {
  padding-left: 20px;
  color: #666;
}

.info-card li {
  margin-bottom: 5px;
}

@media (max-width: 768px) {
  .metal-info {
    grid-template-columns: 1fr;
  }
}
</style>