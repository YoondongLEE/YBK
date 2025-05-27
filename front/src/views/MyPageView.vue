<!-- filepath: /Users/iyundong/Desktop/SSAFY/1학기_관통/final-pjt-v3/final-pjt/front/src/views/MyPageView.vue -->
<template>
  <div class="mypage-container">
    <h1>마이페이지</h1>
    
    <!-- 사용자 정보 섹션 -->
    <div class="user-info-section">
      <h2>회원 정보</h2>
      <div class="user-info">
        <!-- 좌측: 기본 정보 + 현재 포트폴리오 -->
        <div class="basic-info">
          <div class="info-card">
            <h3>계정 정보</h3>
            <p><strong>아이디:</strong> {{ userProfile.username }}</p>
            <p><strong>이메일:</strong> {{ userProfile.email || '이메일 정보 없음' }}</p>
          </div>

          <div class="info-card">
            <h3>개인 정보</h3>
            <p v-if="userProfile.age">
              <strong>나이:</strong> {{ userProfile.age }}세
            </p>
            <p v-if="userProfile.assets">
              <strong>자산:</strong> {{ formatCurrency(userProfile.assets) }}
            </p>
            <p v-if="userProfile.annual_income">
              <strong>연봉:</strong> {{ formatCurrency(userProfile.annual_income) }}
            </p>
            <p v-if="!userProfile.age && !userProfile.assets && !userProfile.annual_income" class="no-info">
              개인 정보를 입력해주세요.
            </p>
          </div>
          
          <!-- 포트폴리오 정보 -->
          <div class="info-card">
            <h3>금융 포트폴리오</h3>
            <div v-if="userProfile.savings_tendency || userProfile.investment_tendency || userProfile.preferred_bank">
              <p v-if="userProfile.savings_tendency">
                <strong>저축성향:</strong> {{ getSavingsTendencyLabel(userProfile.savings_tendency) }}
              </p>
              <p v-if="userProfile.investment_tendency">
                <strong>투자성향:</strong> {{ getInvestmentTendencyLabel(userProfile.investment_tendency) }}
              </p>
              <p v-if="userProfile.preferred_bank">
                <strong>선호 은행:</strong> {{ getPreferredBankName(userProfile.preferred_bank) }}
              </p>
            </div>
            <p v-else class="no-info">포트폴리오 정보를 입력해주세요.</p>
          </div>
        </div>
        
        <!-- 우측: 정보 수정 폼 -->
        <div class="profile-form">
          <h3>정보 수정</h3>
          <form @submit.prevent="updateProfile">
            <!-- 개인 정보 입력 -->
            <div class="form-section">
              <h4>개인 정보</h4>
              
              <div class="form-group">
                <label for="age">나이:</label>
                <input 
                  type="number" 
                  id="age" 
                  v-model="profileForm.age" 
                  placeholder="나이를 입력하세요"
                  min="0"
                  max="150"
                />
              </div>
              
              <div class="form-group">
                <label for="assets">자산:</label>
                <div class="input-with-controls">
                  <input 
                    type="text" 
                    id="assets" 
                    v-model="formattedAssets" 
                    @input="handleAssetsInput"
                    @blur="formatAssetsOnBlur"
                    placeholder="자산을 입력하세요 (원)"
                  />
                  <div class="input-controls">
                    <button type="button" @click="increaseAssets" class="control-btn">▲</button>
                    <button type="button" @click="decreaseAssets" class="control-btn">▼</button>
                  </div>
                </div>
                <span class="input-guide">※ 100원 단위로 입력해주세요</span>
              </div>
              
              <div class="form-group">
                <label for="annual_income">연봉:</label>
                <div class="input-with-controls">
                  <input 
                    type="text" 
                    id="annual_income" 
                    v-model="formattedAnnualIncome" 
                    @input="handleAnnualIncomeInput"
                    @blur="formatAnnualIncomeOnBlur"
                    placeholder="연봉을 입력하세요 (원)"
                  />
                  <div class="input-controls">
                    <button type="button" @click="increaseAnnualIncome" class="control-btn">▲</button>
                    <button type="button" @click="decreaseAnnualIncome" class="control-btn">▼</button>
                  </div>
                </div>
                <span class="input-guide">※ 100원 단위로 입력해주세요</span>
              </div>
            </div>

            <!-- 포트폴리오 정보 입력 -->
            <div class="form-section">
              <h4>금융 포트폴리오</h4>
              
              <div class="form-group">
                <label for="savings_tendency">저축성향:</label>
                <select 
                  id="savings_tendency" 
                  v-model="profileForm.savings_tendency"
                  class="form-select"
                >
                  <option value="">선택하세요</option>
                  <option value="conservative">안정형 - 원금보장 우선</option>
                  <option value="moderate">균형형 - 안정성과 수익성 균형</option>
                  <option value="aggressive">적극형 - 높은 수익률 추구</option>
                </select>
              </div>

              <div class="form-group">
                <label for="investment_tendency">투자성향:</label>
                <select 
                  id="investment_tendency" 
                  v-model="profileForm.investment_tendency"
                  class="form-select"
                >
                  <option value="">선택하세요</option>
                  <option value="very_conservative">매우 보수적</option>
                  <option value="conservative">보수적</option>
                  <option value="moderate">중립적</option>
                  <option value="aggressive">적극적</option>
                  <option value="very_aggressive">매우 적극적</option>
                </select>
              </div>

              <div class="form-group">
                <label for="preferred_bank">선호 은행:</label>
                <select 
                  id="preferred_bank" 
                  v-model="profileForm.preferred_bank"
                  class="form-select"
                >
                  <option value="">선택하세요</option>
                  <option 
                    v-for="bank in banks" 
                    :key="bank.fin_co_no" 
                    :value="bank.fin_co_no"
                  >
                    {{ bank.kor_co_nm }}
                  </option>
                </select>
              </div>
            </div>
            
            <button type="submit" class="update-btn" :disabled="updateLoading">
              {{ updateLoading ? '업데이트 중...' : '정보 업데이트' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- 상품 추천 섹션 -->
    <div v-if="isAuthenticated" class="recommendation-section">
      <h2>맞춤형 상품 추천</h2>
      <p class="recommendation-description">
        회원님과 비슷한 나이, 자산, 소득을 가진 사용자들이 선택한 인기 상품을 추천드립니다.
      </p>
      
      <div class="recommendation-controls">
        <button 
          @click="fetchRecommendations" 
          class="recommendation-btn"
          :disabled="recommendationLoading"
        >
          {{ recommendationLoading ? '분석 중...' : '추천 받기' }}
        </button>
      </div>

      <!-- 추천 결과 -->
      <div v-if="recommendations.length > 0" class="recommendations-container">
        <div class="recommendation-info">
          <p>{{ recommendationMessage }}</p>
        </div>
        
        <div class="recommendation-grid">
          <div 
            v-for="(rec, index) in recommendations" 
            :key="rec.product.fin_prdt_cd"
            class="recommendation-card"
            @click="goToProductDetail(rec.type, rec.product.fin_prdt_cd)"
          >
            <div class="recommendation-header">
              <span class="product-type" :class="rec.type">
                {{ rec.type === 'deposit' ? '예금' : '적금' }}
              </span>
              <span class="recommendation-rank">#{{ index + 1 }}</span>
            </div>
            
            <h4 class="product-name">{{ rec.product.fin_prdt_nm }}</h4>
            <p class="bank-name">{{ rec.product.bank.kor_co_nm }}</p>
            
            <div class="product-info">
              <div class="max-rate">
                최고금리 <span class="rate-value">{{ getMaxRecommendationRate(rec.product) }}%</span>
              </div>
              <div class="popularity">
                <i class="fas fa-users"></i>
                {{ rec.recommendation_count }}명이 선택
              </div>
            </div>
            
            <div class="card-footer">
              <button class="detail-btn">
                자세히 보기 <i class="fas fa-arrow-right"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 추천 실패 또는 오류 메시지 -->
      <div v-else-if="recommendationError" class="recommendation-error">
        <div class="error-content">
          <i class="fas fa-exclamation-triangle"></i>
          <h3>추천을 받을 수 없습니다</h3>
          <p>{{ recommendationError }}</p>
          <p v-if="!userProfile.age || !userProfile.assets || !userProfile.annual_income" class="error-hint">
            정확한 추천을 위해 위에서 나이, 자산, 연봉 정보를 입력해주세요.
          </p>
        </div>
      </div>

      <!-- 추천 로딩 상태 -->
      <div v-else-if="recommendationLoading" class="recommendation-loading">
        <div class="loading-content">
          <div class="loading-spinner"></div>
          <p>비슷한 사용자들의 데이터를 분석하고 있습니다...</p>
        </div>
      </div>
    </div>
    
    <!-- 정기예금 목록 섹션 -->
    <div class="subscription-section">
      <h2>가입한 정기예금 상품</h2>
      <div v-if="depositLoading" class="loading">
        정기예금 상품 정보를 불러오는 중...
      </div>
      <div v-else-if="!depositProducts.length" class="empty-state">
        가입한 정기예금 상품이 없습니다.
      </div>
      <div v-else class="product-list">
        <!-- 정기예금 상품 목록 -->
        <div v-for="product in depositProducts" :key="product.fin_prdt_cd" class="product-card"
          @click="goToDetail('deposit', product.fin_prdt_cd)">
          <div class="bank-name">{{ product.bank_name || getBankName(product) || '정보 없음' }}</div>
          <div class="product-name">{{ product.fin_prdt_nm }}</div>
          <div class="rate">최고금리: {{ getMaxRate(product) }}%</div>
        </div>
      </div>
    </div>

    <!-- 정기적금 목록 섹션 -->
    <div class="subscription-section">
      <h2>가입한 정기적금 상품</h2>
      <div v-if="savingLoading" class="loading">
        정기적금 상품 정보를 불러오는 중...
      </div>
      <div v-else-if="!savingProducts.length" class="empty-state">
        가입한 정기적금 상품이 없습니다.
      </div>
      <div v-else class="product-list">
        <!-- 정기적금 상품 목록 -->
        <div v-for="product in savingProducts" :key="product.fin_prdt_cd" class="product-card"
          @click="goToDetail('saving', product.fin_prdt_cd)">
          <div class="bank-name">{{ product.bank_name || getBankName(product) || '정보 없음' }}</div>
          <div class="product-name">{{ product.fin_prdt_nm }}</div>
          <div class="rate">최고금리: {{ getMaxRate(product) }}%</div>
        </div>
      </div>
    </div>

    <!-- 기존 차트 섹션 -->
    <div v-if="showCharts" class="charts-section">
      <h2>가입 상품 금리 분석</h2>
      
      <!-- 금리 비교 차트 -->
      <div class="chart-container">
        <h3>상품별 최고 금리 비교</h3>
        <canvas ref="interestRateChart" width="400" height="200"></canvas>
      </div>

      <!-- 상품 분포 차트 -->
      <div class="chart-container">
        <h3>가입 상품 분포</h3>
        <canvas ref="distributionChart" width="400" height="200"></canvas>
      </div>

      <!-- 예금/적금 평균 금리 비교 -->
      <div class="chart-container">
        <h3>예금 vs 적금 평균 금리 비교</h3>
        <canvas ref="comparisonChart" width="400" height="200"></canvas>
      </div>
    </div>
    
    <!-- 평가 이력 섹션 (새로 추가) -->
    <div v-if="isAuthenticated" class="assessment-history-section">
      <h2>평가 이력</h2>
      
      <div v-if="assessmentHistory.length === 0 && !assessmentLoading" class="empty-state">
        <p>아직 응시한 평가가 없습니다.</p>
        <router-link to="/finance-academy" class="start-assessment-btn">
          평가 응시하러 가기
        </router-link>
      </div>
      
      <div v-else-if="assessmentHistory.length > 0" class="assessment-list">
        <div 
          v-for="assessment in assessmentHistory" 
          :key="assessment.id"
          class="assessment-item"
          :class="{ 'passed': assessment.passed }"
          @click="viewAssessmentDetail(assessment.id)"
        >
          <div class="assessment-info">
            <div class="difficulty-badge" :class="assessment.difficulty">
              {{ getDifficultyName(assessment.difficulty) }}
            </div>
            <div class="assessment-details">
              <h3>{{ getDifficultyName(assessment.difficulty) }} 평가</h3>
              <p class="date">{{ formatDate(assessment.taken_at) }}</p>
            </div>
          </div>
          
          <div class="assessment-result">
            <div class="score">
              <span class="score-text">{{ assessment.score }}/10</span>
              <span class="percentage">({{ assessment.score_percentage }}%)</span>
            </div>
            <div class="grade" :class="{ 'passed': assessment.passed }">
              {{ assessment.grade || (assessment.passed ? '합격' : '불합격') }}
            </div>
          </div>
          
          <div class="view-detail">
            <i class="bi bi-chevron-right"></i>
          </div>
        </div>
      </div>
      
      <!-- 로딩 상태 -->
      <div v-if="assessmentLoading" class="loading">
        <p>평가 이력을 불러오는 중...</p>
      </div>
    </div>
    
    <!-- 저장된 영상 섹션 -->
    <div v-if="isAuthenticated" class="saved-items-section">
      <h2>저장된 금융 콘텐츠</h2>
      <SavedItems />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useYoutubeStore } from '../stores/youtube';
import api from '../api';
import SavedItems from '../components/youtube/SavedItems.vue';
import { Chart, registerables } from 'chart.js';

// Chart.js 등록
Chart.register(...registerables);

const router = useRouter();
const authStore = useAuthStore();
const youtubeStore = useYoutubeStore();
const user = ref(authStore.user || {});
const isAuthenticated = computed(() => authStore.isAuthenticated);

// 사용자 프로필 정보
const userProfile = ref({});
const profileForm = ref({
  age: null,
  assets: null,
  annual_income: null,
  savings_tendency: '',
  investment_tendency: '',
  preferred_bank: ''
});
const updateLoading = ref(false);

// 포맷된 입력값들
const formattedAssets = ref('');
const formattedAnnualIncome = ref('');

// 정기예금 상품 관련 상태
const depositLoading = ref(true);
const depositProducts = ref([]);

// 정기적금 상품 관련 상태
const savingLoading = ref(true);
const savingProducts = ref([]);

// 은행 정보
const banks = ref([]);

// 추천 관련 상태 변수들
const recommendations = ref([]);
const recommendationLoading = ref(false);
const recommendationError = ref('');
const recommendationMessage = ref('');

// 평가 이력 관련 상태
const assessmentHistory = ref([]);
const assessmentLoading = ref(false);

// 차트 인스턴스들
const interestRateChartInstance = ref(null);
const distributionChartInstance = ref(null);
const comparisonChartInstance = ref(null);

// 차트 캔버스 참조 (template의 ref와 일치)
const interestRateChart = ref(null);
const distributionChart = ref(null);
const comparisonChart = ref(null);

// 차트 생성 상태 관리
const chartsCreated = ref(false);

// 차트 표시 조건
const showCharts = computed(() => {
  const hasData = (depositProducts.value.length > 0 || savingProducts.value.length > 0);
  const loadingComplete = !depositLoading.value && !savingLoading.value;
  
  console.log('차트 표시 조건 체크:', {
    hasData,
    loadingComplete,
    depositCount: depositProducts.value.length,
    savingCount: savingProducts.value.length,
    depositLoading: depositLoading.value,
    savingLoading: savingLoading.value
  });
  
  return hasData && loadingComplete;
});

// 유틸리티 함수들
const formatCurrency = (value) => {
  if (!value) return '정보 없음';
  return new Intl.NumberFormat('ko-KR').format(value) + '원';
};

const addCommas = (value) => {
  if (!value && value !== 0) return '';
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

const removeCommas = (value) => {
  if (!value) return '';
  return value.toString().replace(/,/g, '');
};

const roundToHundred = (value) => {
  return Math.round(value / 100) * 100;
};

const getSavingsTendencyLabel = (value) => {
  const tendencies = {
    'conservative': '안정형',
    'moderate': '균형형',
    'aggressive': '적극형'
  };
  return tendencies[value] || value;
};

const getInvestmentTendencyLabel = (value) => {
  const tendencies = {
    'very_conservative': '매우 보수적',
    'conservative': '보수적',
    'moderate': '중립적',
    'aggressive': '적극적',
    'very_aggressive': '매우 적극적'
  };
  return tendencies[value] || value;
};

const getPreferredBankName = (bankCode) => {
  const bank = banks.value.find(b => b.fin_co_no === bankCode);
  return bank ? bank.kor_co_nm : bankCode;
};

// 평가 관련 함수들
const getDifficultyName = (difficulty) => {
  const names = {
    'youth': '청소년',
    'adult_basic': '성인 기본', 
    'adult_advanced': '성인 심화'
  }
  return names[difficulty] || difficulty
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const viewAssessmentDetail = (assessmentId) => {
  console.log('평가 상세 보기:', assessmentId)
  router.push({ 
    name: 'assessment-detail', 
    params: { id: assessmentId } 
  })
}

const fetchAssessmentHistory = async () => {
  try {
    assessmentLoading.value = true
    console.log('평가 이력 조회 시작...')
    
    // 올바른 API 경로로 수정 (/api/assessments/history/ → /api/finance-academy/assessment/history/)
    const response = await api.get('/finance-academy/assessment/history/')
    console.log('API 응답:', response.data)
    
    assessmentHistory.value = response.data
    console.log('평가 이력 설정 완료:', assessmentHistory.value)
    
  } catch (error) {
    console.error('평가 이력을 불러오는데 실패했습니다:', error)
    
    // 상세 에러 정보 출력
    if (error.response) {
      console.error('Error status:', error.response.status)
      console.error('Error data:', error.response.data)
      console.error('Error headers:', error.response.headers)
    } else if (error.request) {
      console.error('Request made but no response:', error.request)
    } else {
      console.error('Error message:', error.message)
    }
  } finally {
    assessmentLoading.value = false
  }
}

// 추천 관련 함수들
const fetchRecommendations = async () => {
  try {
    recommendationLoading.value = true;
    recommendationError.value = '';
    
    const response = await api.get('/accounts/recommendations/');
    recommendations.value = response.data.recommendations || [];
    recommendationMessage.value = response.data.message || '';
    
    if (recommendations.value.length === 0) {
      recommendationError.value = response.data.error || '추천할 상품이 없습니다.';
    }
    
  } catch (error) {
    console.error('상품 추천 조회 실패:', error);
    if (error.response && error.response.data) {
      recommendationError.value = error.response.data.error || '추천 조회에 실패했습니다.';
    } else {
      recommendationError.value = '추천 조회에 실패했습니다.';
    }
  } finally {
    recommendationLoading.value = false;
  }
};

const goToProductDetail = (type, productId) => {
  if (type === 'deposit') {
    router.push({ name: 'deposit-detail', params: { id: productId } });
  } else {
    router.push({ name: 'saving-detail', params: { id: productId } });
  }
};

const getMaxRecommendationRate = (product) => {
  if (!product.options || product.options.length === 0) return '0.00';
  const maxRate = Math.max(...product.options.map(option => 
    parseFloat(option.intr_rate2 || option.intr_rate || 0)
  ));
  return maxRate.toFixed(2);
};

// 최대 금리 계산 함수
const getMaxRate = (product) => {
  console.log('getMaxRate 호출:', product);
  
  if (!product) {
    console.log('상품이 없습니다');
    return '0.00';
  }
  
  // options가 배열인지 확인
  let options = [];
  if (Array.isArray(product.options)) {
    options = product.options;
  } else if (product.options && typeof product.options === 'string') {
    try {
      options = JSON.parse(product.options);
    } catch (e) {
      console.log('JSON 파싱 실패:', e);
      options = [];
    }
  }
  
  console.log('옵션 데이터:', options);
  
  if (!options || !Array.isArray(options) || options.length === 0) {
    console.log('옵션이 없거나 배열이 아님');
    return '0.00';
  }
  
  let maxRate = 0;
  options.forEach(option => {
    // 우대금리(intr_rate2)가 있으면 우선, 없으면 기본금리(intr_rate)
    const rate = parseFloat(option.intr_rate2) || parseFloat(option.intr_rate) || 0;
    console.log('옵션별 금리:', option, '계산된 금리:', rate);
    if (rate > maxRate) maxRate = rate;
  });
  
  console.log('최대 금리:', maxRate);
  return maxRate.toFixed(2);
};

// 은행명 가져오기
const getBankName = (product) => {
  if (product.bank && typeof product.bank === 'object' && product.bank.kor_co_nm) {
    return product.bank.kor_co_nm;
  }
  
  if (product.bank && typeof product.bank === 'string') {
    const bankObj = banks.value.find(b => b.fin_co_no === product.bank);
    return bankObj ? bankObj.kor_co_nm : '정보 없음';
  }
  
  // fin_co_no로 은행 찾기
  if (product.fin_co_no) {
    const bankObj = banks.value.find(b => b.fin_co_no === product.fin_co_no);
    return bankObj ? bankObj.kor_co_nm : '정보 없음';
  }
  
  return '정보 없음';
};

// 상세 페이지로 이동하는 함수
const goToDetail = (type, id) => {
  router.push({ name: `${type}-detail`, params: { id } });
};

// 데이터 fetch 함수들
const fetchDepositProducts = async () => {
  try {
    depositLoading.value = true;
    console.log('정기예금 상품 조회 API 호출 시작');
    
    const response = await api.get('/deposits/user-subscriptions/');
    console.log('정기예금 상품 조회 응답:', response.data);
    depositProducts.value = response.data;
    
    // 첫 번째 상품의 구조 확인
    if (response.data.length > 0) {
      console.log('첫 번째 예금 상품 구조:', response.data[0]);
      console.log('첫 번째 예금 상품 옵션:', response.data[0].options);
    }
    
  } catch (error) {
    console.error('정기예금 상품 정보 조회 실패:', error);
  } finally {
    depositLoading.value = false;
  }
};

const fetchSavingProducts = async () => {
  try {
    savingLoading.value = true;
    console.log('정기적금 상품 조회 API 호출 시작');
    
    const response = await api.get('/savings/user-subscriptions/');
    console.log('정기적금 상품 조회 응답:', response.data);
    savingProducts.value = response.data;
    
    // 첫 번째 상품의 구조 확인
    if (response.data.length > 0) {
      console.log('첫 번째 적금 상품 구조:', response.data[0]);
      console.log('첫 번째 적금 상품 옵션:', response.data[0].options);
    }
    
  } catch (error) {
    console.error('정기적금 상품 정보 조회 실패:', error);
  } finally {
    savingLoading.value = false;
  }
};

// 차트 생성 함수들
const createInterestRateChart = () => {
  console.log('금리 비교 차트 생성 시작');
  const ctx = interestRateChart.value?.getContext('2d');
  if (!ctx) {
    console.error('interestRateChart 캔버스를 찾을 수 없습니다');
    return;
  }

  // 기존 차트가 있다면 제거
  if (interestRateChartInstance.value) {
    interestRateChartInstance.value.destroy();
    interestRateChartInstance.value = null;
  }

  const allProducts = [
    ...depositProducts.value.map(d => ({...d, type: '예금'})),
    ...savingProducts.value.map(s => ({...s, type: '적금'}))
  ];

  console.log('전체 상품 데이터:', allProducts);

  if (allProducts.length === 0) {
    console.log('표시할 상품이 없습니다');
    return;
  }

  const labels = allProducts.map(p => {
    const name = p.fin_prdt_nm || '상품명 없음';
    return name.length > 15 ? name.substring(0, 15) + '...' : name;
  });
  
  const rates = allProducts.map(p => {
    const rate = parseFloat(getMaxRate(p));
    console.log(`${p.fin_prdt_nm} 금리:`, rate);
    return isNaN(rate) ? 0 : rate;
  });
  
  const colors = allProducts.map(p => 
    p.type === '예금' ? 'rgba(54, 162, 235, 0.6)' : 'rgba(255, 99, 132, 0.6)'
  );

  console.log('차트 데이터:', { labels, rates, colors });

  // 모든 금리가 0인지 확인
  const hasValidData = rates.some(rate => rate > 0);
  if (!hasValidData) {
    console.warn('모든 상품의 금리가 0입니다. 데이터를 확인해주세요.');
  }

  try {
    interestRateChartInstance.value = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: '최고 금리 (%)',
          data: rates,
          backgroundColor: colors,
          borderColor: colors.map(color => color.replace('0.6', '1')),
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const product = allProducts[context.dataIndex];
                return `${product.type}: ${context.parsed.y}%`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: '금리 (%)'
            }
          },
          x: {
            title: {
              display: true,
              text: '상품명'
            }
          }
        }
      }
    });
    console.log('금리 비교 차트 생성 완료');
  } catch (error) {
    console.error('금리 비교 차트 생성 실패:', error);
  }
};

const createComparisonChart = () => {
  console.log('비교 차트 생성 시작');
  const ctx = comparisonChart.value?.getContext('2d');
  if (!ctx) {
    console.error('comparisonChart 캔버스를 찾을 수 없습니다');
    return;
  }

  if (comparisonChartInstance.value) {
    comparisonChartInstance.value.destroy();
    comparisonChartInstance.value = null;
  }

  // 예금과 적금의 평균 금리 계산
  console.log('예금 상품들:', depositProducts.value);
  console.log('적금 상품들:', savingProducts.value);
  
  const depositAvg = depositProducts.value.length > 0 ? 
    depositProducts.value.reduce((sum, d) => {
      const rate = parseFloat(getMaxRate(d));
      console.log(`예금 ${d.fin_prdt_nm} 금리:`, rate);
      return sum + (isNaN(rate) ? 0 : rate);
    }, 0) / depositProducts.value.length : 0;
    
  const savingAvg = savingProducts.value.length > 0 ? 
    savingProducts.value.reduce((sum, s) => {
      const rate = parseFloat(getMaxRate(s));
      console.log(`적금 ${s.fin_prdt_nm} 금리:`, rate);
      return sum + (isNaN(rate) ? 0 : rate);
    }, 0) / savingProducts.value.length : 0;

  console.log('평균 금리:', { depositAvg, savingAvg });

  try {
    comparisonChartInstance.value = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['정기예금', '정기적금'],
        datasets: [{
          label: '평균 최고 금리 (%)',
          data: [parseFloat(depositAvg.toFixed(2)), parseFloat(savingAvg.toFixed(2))],
          backgroundColor: [
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 99, 132, 0.6)'
          ],
          borderColor: [
            'rgba(54, 162, 235, 1)',
            'rgba(255, 99, 132, 1)'
          ],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: '평균 금리 (%)'
            }
          }
        }
      }
    });
    console.log('비교 차트 생성 완료');
  } catch (error) {
    console.error('비교 차트 생성 실패:', error);
  }
};

const createDistributionChart = () => {
  console.log('분포 차트 생성 시작');
  const ctx = distributionChart.value?.getContext('2d');
  if (!ctx) {
    console.error('distributionChart 캔버스를 찾을 수 없습니다');
    return;
  }

  if (distributionChartInstance.value) {
    distributionChartInstance.value.destroy();
    distributionChartInstance.value = null;
  }

  const depositCount = depositProducts.value.length;
  const savingCount = savingProducts.value.length;
  
  console.log('상품 개수:', { depositCount, savingCount });

  if (depositCount === 0 && savingCount === 0) {
    console.log('표시할 데이터가 없습니다');
    return;
  }

  try {
    distributionChartInstance.value = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['정기예금', '정기적금'],
        datasets: [{
          data: [depositCount, savingCount],
          backgroundColor: [
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 99, 132, 0.6)'
          ],
          borderColor: [
            'rgba(54, 162, 235, 1)',
            'rgba(255, 99, 132, 1)'
          ],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.label + ': ' + context.parsed + '개';
              }
            }
          }
        }
      }
    });
    console.log('분포 차트 생성 완료');
  } catch (error) {
    console.error('분포 차트 생성 실패:', error);
  }
};

// 모든 차트 생성
const createCharts = async () => {
  console.log('차트 생성 시작, 데이터 확인:', {
    depositProducts: depositProducts.value.length,
    savingProducts: savingProducts.value.length,
    depositLoading: depositLoading.value,
    savingLoading: savingLoading.value,
    showCharts: showCharts.value,
    chartsCreated: chartsCreated.value
  });

  // 조건 확인
  if (!showCharts.value) {
    console.log('차트 표시 조건이 맞지 않습니다');
    return;
  }

  if (chartsCreated.value) {
    console.log('차트가 이미 생성되었습니다');
    return;
  }

  chartsCreated.value = true;

  // DOM이 준비될 때까지 대기
  await nextTick();
  
  // 조금 더 기다린 후 차트 생성
  setTimeout(() => {
    console.log('금리 비교 차트 생성 시도');
    createInterestRateChart();
  }, 100);
  
  setTimeout(() => {
    console.log('분포 차트 생성 시도');
    createDistributionChart();
  }, 200);
  
  setTimeout(() => {
    console.log('비교 차트 생성 시도');
    createComparisonChart();
  }, 300);
};

// 차트 인스턴스 정리
const destroyCharts = () => {
  console.log('차트 인스턴스 정리');
  if (interestRateChartInstance.value) {
    interestRateChartInstance.value.destroy();
    interestRateChartInstance.value = null;
  }
  if (distributionChartInstance.value) {
    distributionChartInstance.value.destroy();
    distributionChartInstance.value = null;
  }
  if (comparisonChartInstance.value) {
    comparisonChartInstance.value.destroy();
    comparisonChartInstance.value = null;
  }
  chartsCreated.value = false;
};

// showCharts computed 속성 감시
watch(showCharts, (newValue, oldValue) => {
  console.log('showCharts 변경:', { newValue, oldValue, chartsCreated: chartsCreated.value });
  
  if (newValue && !chartsCreated.value) {
    console.log('차트 표시 조건 충족, 차트 생성 시작');
    createCharts();
  }
}, { immediate: true });

// 입력 처리 함수들
const handleAssetsInput = (event) => {
  const inputValue = event.target.value;
  const numericOnly = inputValue.replace(/[^\d]/g, '');
  
  if (numericOnly) {
    const numericValue = parseInt(numericOnly);
    const roundedValue = roundToHundred(numericValue);
    profileForm.value.assets = roundedValue;
    formattedAssets.value = numericOnly;
  } else {
    profileForm.value.assets = null;
    formattedAssets.value = '';
  }
};

const formatAssetsOnBlur = () => {
  if (profileForm.value.assets) {
    formattedAssets.value = addCommas(profileForm.value.assets);
  }
};

const handleAnnualIncomeInput = (event) => {
  const inputValue = event.target.value;
  const numericOnly = inputValue.replace(/[^\d]/g, '');
  
  if (numericOnly) {
    const numericValue = parseInt(numericOnly);
    const roundedValue = roundToHundred(numericValue);
    profileForm.value.annual_income = roundedValue;
    formattedAnnualIncome.value = numericOnly;
  } else {
    profileForm.value.annual_income = null;
    formattedAnnualIncome.value = '';
  }
};

const formatAnnualIncomeOnBlur = () => {
  if (profileForm.value.annual_income) {
    formattedAnnualIncome.value = addCommas(profileForm.value.annual_income);
  }
};

const increaseAssets = () => {
  const currentValue = profileForm.value.assets || 0;
  const newValue = currentValue + 100000;
  profileForm.value.assets = newValue;
  formattedAssets.value = addCommas(newValue);
};

const decreaseAssets = () => {
  const currentValue = profileForm.value.assets || 0;
  const newValue = Math.max(0, currentValue - 100000);
  profileForm.value.assets = newValue === 0 ? null : newValue;
  formattedAssets.value = newValue === 0 ? '' : addCommas(newValue);
};

const increaseAnnualIncome = () => {
  const currentValue = profileForm.value.annual_income || 0;
  const newValue = currentValue + 1000000;
  profileForm.value.annual_income = newValue;
  formattedAnnualIncome.value = addCommas(newValue);
};

const decreaseAnnualIncome = () => {
  const currentValue = profileForm.value.annual_income || 0;
  const newValue = Math.max(0, currentValue - 1000000);
  profileForm.value.annual_income = newValue === 0 ? null : newValue;
  formattedAnnualIncome.value = newValue === 0 ? '' : addCommas(newValue);
};

// 프로필 관련 함수들
const fetchUserProfile = async () => {
  try {
    const response = await api.get('/accounts/profile/');
    userProfile.value = response.data;
    
    profileForm.value = {
      age: response.data.age || null,
      assets: response.data.assets || null,
      annual_income: response.data.annual_income || null,
      savings_tendency: response.data.savings_tendency || '',
      investment_tendency: response.data.investment_tendency || '',
      preferred_bank: response.data.preferred_bank || ''
    };
    
    formattedAssets.value = response.data.assets ? addCommas(response.data.assets) : '';
    formattedAnnualIncome.value = response.data.annual_income ? addCommas(response.data.annual_income) : '';
  } catch (error) {
    console.error('사용자 프로필 정보 조회 실패:', error);
  }
};

const updateProfile = async () => {
  try {
    updateLoading.value = true;
    
    const updateData = {};
    if (profileForm.value.age !== null && profileForm.value.age !== '') {
      updateData.age = parseInt(profileForm.value.age);
    }
    if (profileForm.value.assets !== null && profileForm.value.assets !== '') {
      updateData.assets = parseInt(profileForm.value.assets);
    }
    if (profileForm.value.annual_income !== null && profileForm.value.annual_income !== '') {
      updateData.annual_income = parseInt(profileForm.value.annual_income);
    }
    if (profileForm.value.savings_tendency) {
      updateData.savings_tendency = profileForm.value.savings_tendency;
    }
    if (profileForm.value.investment_tendency) {
      updateData.investment_tendency = profileForm.value.investment_tendency;
    }
    if (profileForm.value.preferred_bank) {
      updateData.preferred_bank = profileForm.value.preferred_bank;
    }
    
    const response = await api.put('/accounts/profile/update/', updateData);
    
    // 업데이트 후 즉시 사용자 프로필을 다시 가져오기
    await fetchUserProfile();
    
    alert('프로필 정보가 성공적으로 업데이트되었습니다.');
  } catch (error) {
    console.error('프로필 업데이트 실패:', error);
    
    if (error.response && error.response.data) {
      const errors = error.response.data;
      let errorMessage = '프로필 업데이트에 실패했습니다.\n\n';
      
      Object.keys(errors).forEach(key => {
        if (Array.isArray(errors[key])) {
          errorMessage += `${key}: ${errors[key].join(', ')}\n`;
        } else {
          errorMessage += `${key}: ${errors[key]}\n`;
        }
      });
      
      alert(errorMessage);
    } else {
      alert('프로필 업데이트에 실패했습니다.');
    }
  } finally {
    updateLoading.value = false;
  }
};

const fetchBanks = async () => {
  try {
    const response = await api.get('/banks/');
    banks.value = response.data;
    console.log('은행 정보 로드:', banks.value.length);
  } catch (error) {
    console.error('은행 정보 로드 실패:', error);
  }
};

// 라이프사이클 훅
onMounted(async () => {
  console.log('컴포넌트 마운트됨');
  if (isAuthenticated.value) {
    await fetchBanks();
    await fetchUserProfile();
    await fetchDepositProducts();
    await fetchSavingProducts();
    await fetchAssessmentHistory();
    
    youtubeStore.initialize();
  } else {
    router.push({ name: 'login' });
  }
});

onUnmounted(() => {
  destroyCharts();
});
</script>

<style scoped>
.mypage-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.mypage-container h1 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 30px;
  font-size: 32px;
  font-weight: 700;
}

h1 {
  margin-bottom: 30px;
  color: #333;
  text-align: center;
}

.user-info-section,
.subscribed-products-section,
.youtube-section,
.recommendation-section,
.subscription-section,
.charts-section,
.assessment-history-section,
.saved-items-section {
  background-color: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.user-info-section h2,
.subscribed-products-section h2,
.youtube-section h2,
.recommendation-section h2,
.subscription-section h2,
.charts-section h2,
.assessment-history-section h2,
.saved-items-section h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 700;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e9ecef;
}

.info-item label {
  font-weight: 600;
  color: #495057;
}

.info-item span {
  color: #6c757d;
  font-weight: 500;
}

.profile-update-form {
  border-top: 2px solid #e9ecef;
  padding-top: 30px;
}

.profile-update-form h3 {
  color: #495057;
  margin-bottom: 20px;
  font-size: 20px;
}

h2 {
  margin-bottom: 25px;
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
  font-size: 24px;
}

h3 {
  margin-bottom: 15px;
  color: #34495e;
  font-size: 18px;
  font-weight: 600;
}

h4 {
  margin-bottom: 15px;
  color: #555;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.user-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: start;
}

.basic-info {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.info-card {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #3498db;
}

.info-card h3 {
  margin-bottom: 15px;
  margin-top: 0;
  color: #2c3e50;
  font-size: 16px;
}

.info-card p {
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.5;
}

.no-info {
  color: #7f8c8d;
  font-style: italic;
  font-size: 13px;
}

.profile-form {
  background-color: #fff;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  padding: 25px;
}

.form-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #495057;
}

.input-with-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-with-controls input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.form-select:focus,
.form-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-controls {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.control-btn {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 32px;
  height: 22px;
  cursor: pointer;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.control-btn:hover {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

.input-guide {
  display: block;
  margin-top: 5px;
  font-size: 11px;
  color: #7f8c8d;
}

.update-btn {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  padding: 12px 30px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
  width: 100%;
  margin-top: 10px;
}

.update-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9, #3498db);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.update-btn:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.product-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.product-card {
  border: 1px solid #e9ecef;
  border-radius: 10px;
  padding: 20px;
  background-color: #fff;
  transition: all 0.3s;
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #3498db;
}

.bank-name {
  font-size: 13px;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.product-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #2c3e50;
  line-height: 1.3;
}

.rate {
  font-size: 15px;
  color: #e74c3c;
  font-weight: 700;
}

.loading, .empty-state {
  padding: 40px;
  text-align: center;
  background-color: #f8f9fa;
  border-radius: 10px;
  color: #7f8c8d;
}

/* 차트 관련 스타일 */
.charts-section {
  background-color: white;
}

.chart-container {
  margin-bottom: 40px;
  padding: 25px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  height: 450px;
}

.chart-container:last-child {
  margin-bottom: 0;
}

.chart-container h3 {
  margin-bottom: 20px;
  text-align: center;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.chart-container canvas {
  max-height: 400px;
  width: 100% !important;
  height: 400px !important;
}

/* 추천 섹션 스타일 */
.recommendation-section {
  background-color: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.recommendation-section h2 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 24px;
  font-weight: 700;
}

.recommendation-description {
  color: #7f8c8d;
  margin-bottom: 20px;
  line-height: 1.6;
}

.recommendation-controls {
  margin-bottom: 25px;
}

.recommendation-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recommendation-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.recommendation-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.recommendation-info {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #667eea;
}

.recommendation-info p {
  margin: 0;
  color: #495057;
  font-weight: 500;
}

.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.recommendation-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.recommendation-card:hover {
  border-color: #667eea;
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.product-type {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.product-type.deposit {
  background-color: #e3f2fd;
  color: #1976d2;
}

.product-type.saving {
  background-color: #fff3e0;
  color: #f57c00;
}

.recommendation-rank {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
}

.recommendation-card .product-name {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.3;
}

.recommendation-card .bank-name {
  color: #7f8c8d;
  margin-bottom: 15px;
  font-size: 14px;
}

.product-info {
  margin-bottom: 20px;
}

.max-rate {
  margin-bottom: 10px;
  color: #2c3e50;
  font-weight: 500;
}

.rate-value {
  color: #e74c3c;
  font-weight: 700;
  font-size: 18px;
}

.popularity {
  color: #7f8c8d;
  font-size: 14px;
}

.popularity i {
  margin-right: 5px;
  color: #667eea;
}

.card-footer {
  border-top: 1px solid #e9ecef;
  padding-top: 15px;
}

.detail-btn {
  background: transparent;
  border: 2px solid #667eea;
  color: #667eea;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.detail-btn:hover {
  background-color: #667eea;
  color: white;
}

.recommendation-error {
  text-align: center;
  padding: 40px 20px;
  background-color: #fff5f5;
  border-radius: 12px;
  border: 2px solid #fed7d7;
}

.error-content h3 {
  color: #e53e3e;
  margin-bottom: 10px;
}

.error-content p {
  color: #744210;
  line-height: 1.6;
}

.error-hint {
  background-color: #fef3cd;
  padding: 10px;
  border-radius: 6px;
  margin-top: 15px;
  border-left: 4px solid #ffc107;
}

.recommendation-loading {
  text-align: center;
  padding: 40px 20px;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 평가 이력 섹션 스타일 */
.assessment-history-section {
  background-color: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.assessment-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.assessment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 12px;
  border: 2px solid #e9ecef;
  cursor: pointer;
  transition: all 0.3s ease;
}

.assessment-item:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
}

.assessment-item.passed {
  border-color: #28a745;
  background-color: #f8fff9;
}

.assessment-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.difficulty-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.difficulty-badge.youth {
  background-color: #e3f2fd;
  color: #1976d2;
}

.difficulty-badge.adult_basic {
  background-color: #fff3e0;
  color: #f57c00;
}

.difficulty-badge.adult_advanced {
  background-color: #ffebee;
  color: #d32f2f;
}

.assessment-details h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #2c3e50;
}

.assessment-details .date {
  margin: 0;
  font-size: 14px;
  color: #7f8c8d;
}

.assessment-result {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score {
  text-align: center;
}

.score-text {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

.percentage {
  font-size: 14px;
  color: #7f8c8d;
}

.grade {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  background-color: #ffebee;
  color: #d32f2f;
}

.grade.passed {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.view-detail {
  color: #667eea;
  font-size: 18px;
}

.start-assessment-btn {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  margin-top: 15px;
  transition: all 0.3s ease;
}

.start-assessment-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  text-decoration: none;
  color: white;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .user-info {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .info-card {
    padding: 15px;
  }
  
  .profile-form {
    padding: 20px;
  }
  
  .product-list {
    grid-template-columns: 1fr;
  }
  
  .input-with-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .input-controls {
    flex-direction: row;
    justify-content: center;
    margin-top: 8px;
  }
  
  .control-btn {
    width: 50px;
    height: 30px;
    font-size: 12px;
  }

  .recommendation-grid {
    grid-template-columns: 1fr;
  }
  
  .recommendation-section {
    padding: 20px;
  }

  .assessment-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .assessment-result {
    align-self: stretch;
    justify-content: space-between;
  }

  .chart-container {
    height: 350px;
    padding: 15px;
  }

  .chart-container canvas {
    max-height: 300px !important;
    height: 300px !important;
  }
}
</style>