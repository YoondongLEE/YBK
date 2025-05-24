<!-- filepath: /Users/iyundong/Desktop/SSAFY/1학기_관통/final-pjt-v1/final-pjt/front/src/components/finance/MetalPriceChart.vue -->
<template>
  <div class="metal-price-chart-container">
    <div class="chart-controls">
      <div class="metal-selector">
        <button 
          @click="selectMetal('gold')" 
          :class="{ active: selectedMetal === 'gold' }"
          class="metal-btn"
        >
          <i class="fas fa-coins"></i> 금
        </button>
        <button 
          @click="selectMetal('silver')" 
          :class="{ active: selectedMetal === 'silver' }"
          class="metal-btn"
        >
          <i class="fas fa-coins"></i> 은
        </button>
      </div>
      
      <div class="date-filters">
        <div class="date-filter">
          <label for="start-date">시작일:</label>
          <input 
            type="date" 
            id="start-date" 
            v-model="startDate"
            @change="fetchData"
          >
        </div>
        <div class="date-filter">
          <label for="end-date">종료일:</label>
          <input 
            type="date" 
            id="end-date" 
            v-model="endDate"
            @change="fetchData"
          >
        </div>
        <button @click="resetDates" class="reset-btn">
          전체 기간
        </button>
      </div>
    </div>
    
    <div class="chart-container">
      <div v-if="loading" class="loading-indicator">
        <p>데이터를 불러오는 중...</p>
      </div>
      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
      </div>
      <div v-else-if="!chartData.labels.length" class="no-data-message">
        <p>선택한 기간에 데이터가 없습니다.</p>
      </div>
      <canvas v-else ref="chartCanvas" class="chart-canvas"></canvas>
    </div>
    
    <div class="price-stats" v-if="chartData.labels.length">
      <div class="stat-item">
        <span class="stat-label">최저가:</span>
        <span class="stat-value">${{ formatPrice(statistics.min_price) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">최고가:</span>
        <span class="stat-value">${{ formatPrice(statistics.max_price) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">평균가:</span>
        <span class="stat-value">${{ formatPrice(statistics.avg_price) }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue';
import Chart from 'chart.js/auto';
import api from '@/api';

export default {
  name: 'MetalPriceChart',
  setup() {
    const chartCanvas = ref(null);
    const chartInstance = ref(null);
    const selectedMetal = ref('gold');
    const startDate = ref('');
    const endDate = ref('');
    const metalPrices = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const statistics = ref({
      min_price: 0,
      max_price: 0,
      avg_price: 0
    });
    
    // 차트 데이터 계산
    const chartData = computed(() => {
      const labels = metalPrices.value.map(item => item.date);
      const data = metalPrices.value.map(item => item.price);
      
      return {
        labels,
        datasets: [
          {
            label: selectedMetal.value === 'gold' ? '금 가격 (USD)' : '은 가격 (USD)',
            data,
            borderColor: selectedMetal.value === 'gold' ? '#FFD700' : '#C0C0C0',
            backgroundColor: selectedMetal.value === 'gold' ? 'rgba(255, 215, 0, 0.2)' : 'rgba(192, 192, 192, 0.2)',
            borderWidth: 2,
            tension: 0.1,
            fill: true
          }
        ]
      };
    });
    
    // 차트 렌더링 함수
    const renderChart = () => {
      if (chartInstance.value) {
        chartInstance.value.destroy();
      }
      
      if (!chartCanvas.value) return;
      
      const ctx = chartCanvas.value.getContext('2d');
      
      chartInstance.value = new Chart(ctx, {
        type: 'line',
        data: chartData.value,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `가격: $${context.parsed.y.toFixed(2)}`;
                }
              }
            },
            legend: {
              display: true,
              position: 'top'
            },
            title: {
              display: true,
              text: selectedMetal.value === 'gold' ? '금 가격 변동 추이' : '은 가격 변동 추이',
              font: {
                size: 16
              }
            }
          },
          scales: {
            x: {
              title: {
                display: true,
                text: '날짜'
              },
              ticks: {
                maxRotation: 45,
                minRotation: 45,
                autoSkip: true,
                maxTicksLimit: 15
              }
            },
            y: {
              title: {
                display: true,
                text: '가격 (USD)'
              },
              beginAtZero: false
            }
          }
        }
      });
    };
    
    // 데이터 로드 함수
    const fetchData = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const params = {
          metal_type: selectedMetal.value
        };
        
        if (startDate.value) {
          params.start_date = startDate.value;
        }
        
        if (endDate.value) {
          params.end_date = endDate.value;
        }
        
        const response = await api.get('/finance-info/metal-prices/', { params });
        
        if (response.data && response.data.data) {
          metalPrices.value = response.data.data;
          statistics.value = response.data.statistics || {
            min_price: 0,
            max_price: 0,
            avg_price: 0
          };
        } else {
          metalPrices.value = [];
          statistics.value = {
            min_price: 0,
            max_price: 0,
            avg_price: 0
          };
        }
        
        // 차트 다시 그리기
        renderChart();
      } catch (err) {
        console.error('Metal prices fetch error:', err);
        error.value = '가격 데이터를 불러오는 중 오류가 발생했습니다.';
      } finally {
        loading.value = false;
      }
    };
    
    // 메탈 선택 함수
    const selectMetal = (metal) => {
      selectedMetal.value = metal;
      fetchData();
    };
    
    // 날짜 초기화 함수
    const resetDates = () => {
      startDate.value = '';
      endDate.value = '';
      fetchData();
    };
    
    // 가격 형식화 함수
    const formatPrice = (price) => {
      if (!price) return '0.00';
      return parseFloat(price).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    };
    
    // 메탈 타입 변경 감시
    watch(selectedMetal, () => {
      fetchData();
    });
    
    // 컴포넌트 마운트 시 데이터 로드
    onMounted(() => {
      fetchData();
    });
    
    return {
      chartCanvas,
      selectedMetal,
      startDate,
      endDate,
      chartData,
      loading,
      error,
      statistics,
      selectMetal,
      resetDates,
      fetchData,
      formatPrice
    };
  }
};
</script>

<style scoped>
.metal-price-chart-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 30px;
}

.chart-controls {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 15px;
}

.metal-selector {
  display: flex;
  gap: 10px;
}

.metal-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  background-color: #f0f0f0;
}

.metal-btn.active {
  background-color: #4a90e2;
  color: white;
}

.metal-btn:hover:not(.active) {
  background-color: #e0e0e0;
}

.date-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
}

.date-filter {
  display: flex;
  align-items: center;
  gap: 5px;
}

.date-filter label {
  font-size: 14px;
  color: #555;
}

.date-filter input {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.reset-btn {
  padding: 6px 12px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.reset-btn:hover {
  background-color: #e0e0e0;
}

.chart-container {
  height: 400px;
  position: relative;
  margin-bottom: 20px;
}

.loading-indicator,
.error-message,
.no-data-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 16px;
  color: #666;
}

.error-message {
  color: #e53935;
}

.chart-canvas {
  width: 100%;
  height: 100%;
}

.price-stats {
  display: flex;
  justify-content: space-around;
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 15px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

@media (max-width: 768px) {
  .chart-controls {
    flex-direction: column;
  }
  
  .date-filters {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .price-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .stat-item {
    text-align: left;
  }
}
</style>