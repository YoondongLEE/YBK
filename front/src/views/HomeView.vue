<template>
  <div class="page-background">
    <div class="home-container">
      <!-- 헤더 섹션 -->
      <div class="header-section">
        <h1>YBK 금융 아카데미</h1>
        <p class="subtitle">금융 지식을 함께 학습하는 공간</p>
      </div>

      <!-- 메인 배너 섹션 -->
      <div class="main-banner">
        <div class="banner-content">
          <h2>금융의 세계로 오신것을 환영합니다</h2>
          <p>실용적인 금융 지식을 쉽게 배우고 미래를 준비하세요</p>
          <button class="cta-button" @click="scrollToServices">시작하기</button>
        </div>
      </div>

      <!-- 서비스 소개 섹션 -->
      <div id="services-section" class="services-section">
        <div class="service-item academy" @click="navigateTo('financeAcademy')">
          <div class="icon">
            <i class="fas fa-graduation-cap"></i>
          </div>
          <h2>금융 아카데미</h2>
          <p>기초부터 심화까지 체계적인 금융 교육 콘텐츠를 제공합니다</p>
          <div class="btn-more">자세히 알아보기 →</div>
        </div>
        
        <div class="service-item info" @click="navigateTo('financeInfo')">
          <div class="icon">
            <i class="fas fa-info-circle"></i>
          </div>
          <h2>금융 정보 길잡이</h2>
          <p>실생활에 필요한 유용한 금융 정보와 최신 트렌드를 확인하세요</p>
          <div class="btn-more">자세히 알아보기 →</div>
        </div>
      </div>
      
      <!-- 특징 섹션 -->
      <div class="features-section">
        <h2>왜 윤봉길 금융 아카데미인가요?</h2>
        <div class="features-container">
          <div class="feature">
            <h3>전문적인 콘텐츠</h3>
            <p>금융 전문가들이 제작한 양질의 교육 자료</p>
          </div>
          <div class="feature">
            <h3>실용적 접근</h3>
            <p>실생활에 바로 적용할 수 있는 실용적인 금융 지식</p>
          </div>
          <div class="feature">
            <h3>맞춤형 학습</h3>
            <p>초보자부터 전문가까지 수준별 콘텐츠 제공</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import bannerImage from '@/assets/images/main_banner.png'; // 이미지 import는 css에서 사용하지 않아도 유지

const router = useRouter();

const navigateTo = (routeName) => {
  router.push({ name: routeName });
};

const scrollToServices = () => {
  const servicesSection = document.getElementById('services-section');
  if (servicesSection) {
    servicesSection.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
  }
};
</script>

<style scoped>
.page-background {
  background-image: url('@/assets/images/main_banner.png');
  background-size: cover;
  background-repeat: no-repeat;
  background-position: 65% 90%; /* 오른쪽으로 5%, 위로 10% 이동 */
  background-attachment: fixed;
  min-height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
}

.home-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
  font-family: 'Noto Sans KR', sans-serif;
}

/* 헤더 섹션 스타일 */
.header-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px 0;
}

.header-section h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.2rem;
  color: #7f8c8d;
}

/* 메인 배너 스타일 */
.main-banner {
  position: relative;
  min-height: 500px;
  display: flex;
  align-items: center;
  margin-bottom: 50px;
  border-radius: 12px;
  overflow: hidden;
}

.banner-content {
  background-color: rgba(0, 0, 0, 0.6);
  padding: 40px;
  border-radius: 12px;
  color: white;
  max-width: 600px;
  backdrop-filter: blur(5px);
}

.banner-content h2 {
  font-size: 2rem;
  margin-bottom: 15px;
}

.banner-content p {
  font-size: 1.1rem;
  margin-bottom: 25px;
  opacity: 0.9;
}

.cta-button {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 30px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  width: fit-content;
}

.cta-button:hover {
  background-color: #3a7bc8;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

/* 서비스 섹션 스타일 */
.services-section {
  display: flex;
  gap: 30px;
  margin-bottom: 50px;
}

.service-item {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  backdrop-filter: blur(10px);
}

.service-item:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
  background-color: rgba(255, 255, 255, 0.95);
}

.service-item .icon {
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #4a90e2;
}

.service-item h2 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.5rem;
}

.service-item p {
  color: #2c3e50;
  margin-bottom: 20px;
  line-height: 1.6;
}

.btn-more {
  color: #4a90e2;
  font-weight: 600;
  margin-top: auto;
  padding-top: 10px;
}

.academy {
  border-top: 4px solid #4a90e2;
}

.info {
  border-top: 4px solid #2ecc71;
}

/* 특징 섹션 스타일 */
.features-section {
  text-align: center;
  padding: 40px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  margin-top: 50px;
}

.features-section h2 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 1.8rem;
}

.features-container {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.feature {
  flex: 1;
  background-color: rgba(248, 249, 250, 0.8);
  padding: 25px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.feature:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.feature h3 {
  color: #4a90e2;
  margin-bottom: 10px;
}

.feature p {
  color: #2c3e50;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .page-background {
    background-size: cover;
    background-position: center;
  }
  
  .banner-content {
    max-width: 100%;
  }
  
  .services-section {
    flex-direction: column;
  }
  
  .features-container {
    flex-direction: column;
  }
}
</style>