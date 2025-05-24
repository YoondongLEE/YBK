# 5/23
- 협업 경험이 적은 2명이 만나 개발프로젝트를 진행하려니 어떻게 역할을 나눠야 할지 잘 몰랐다.
- 그래서 프론트와 백 둘 다 같이 하면서 학습하자는 의미로 프론트, 백 으로 역할을 나누지 않고 기능별로 역할을 분담했다.
- git branch로 기능을 나눠서 구현 후 master branch에서 병합하면 안전하게 작업할 수 있다고 생각했다.
- 하지만 branch로 기능을 나눴다고 생각했지만 완벽히 독립적으로 진행되지 않았던 것 같다.
- 각자의 기능을 구현한 후 병합하였는데 각자의 기능이 성공적으로 구현된 걸 합쳤지만 합쳤을 때는 두 기능 모두 작동하지 않았다.
- 이러한 경험을 함으로써 git branch에 대해 더 알아야 앞으로 프로젝트할 때 큰 문제가 없을 것 같고 협업을 조금 더 경험해봐야 할 것 같다.

# 5/24
# 프로젝트 기능 구현 설명 - README

## 1. 사용자 인증 시스템

### 회원가입 및 로그인
- Vue 3와 Vuex를 활용한 상태 관리
- JWT 토큰 기반 인증 시스템 구현
- 로컬 스토리지를 활용한 토큰 저장 및 자동 로그인 기능
- 로그인 상태에 따른 조건부 UI 렌더링

```javascript
// 토큰 기반 인증
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})
```

## 2. 금융 데이터 시각화

### 금/은 가격 변동 추이
- Chart.js를 활용한 선형 그래프 구현
- 날짜 기반 필터링 기능 (시작일/종료일 선택)
- 금/은 자산 선택 기능
- 통계 정보 표시 (최저가, 최고가, 평균가)
- 동적 차트 생성과 캔버스 관리

```javascript
// 차트 렌더링
const renderChart = async () => {
  // 동적으로 Chart.js 임포트
  if (!Chart) Chart = (await import('chart.js/auto')).default
  
  // 캔버스 생성 및 차트 데이터 설정
  const canvas = document.createElement('canvas')
  chartInstance.value = new Chart(ctx, {
    type: 'line',
    data: { 
      labels, 
      datasets: [{ 
        label: selectedMetal.value==='gold' ? '금 가격' : '은 가격', 
        data, 
        borderColor: color, 
        tension: 0.1, 
        fill: false 
      }] 
    }
  })
}
```

## 3. 외부 API 통합

### YouTube Data API
- 관련 금융 교육 영상 검색 및 표시
- `VITE_YOUTUBE_API_KEY`를 활용한 YouTube API 통합
- 영상 결과 페이징 처리

### Hugging Face API
- 자연어 처리 기능 구현
- `VITE_HUGGINGFACE_API_KEY`를 활용한 텍스트 분석 및 감정 분석

### OpenAI API
- 금융 관련 질의응답 기능
- `VITE_OPENAI_API_KEY`를 활용한 AI 어시스턴트 구현
- 사용자 입력에 기반한 금융 조언 제공

```javascript
// API 키 환경 변수 활용 예시
const youtubeApiKey = import.meta.env.VITE_YOUTUBE_API_KEY
const huggingfaceApiKey = import.meta.env.VITE_HUGGINGFACE_API_KEY
const openaiApiKey = import.meta.env.VITE_OPENAI_API_KEY
```

## 4. 반응형 디자인

- 다양한 화면 크기에 적응하는 반응형 레이아웃
- CSS Grid와 Flexbox를 활용한 모바일 친화적 UI
- 미디어 쿼리를 통한 뷰포트 크기 기반 스타일 조정

```css
@media (max-width: 768px) {
  .metal-info {
    grid-template-columns: 1fr;
  }
  
  .chart-controls {
    flex-direction: column;
    gap: 15px;
  }
}
```

## 5. 백엔드 연동

- RESTful API를 통한 데이터 통신
- Django 백엔드와의 효율적인 통합
- Axios를 활용한 HTTP 요청 처리
- URL 라우팅과 API 엔드포인트 설계

```javascript
// 금속 가격 데이터 가져오기 예시
const fetchData = async () => {
  try {
    const params = { metal_type: selectedMetal.value }
    if (startDate.value) params.start_date = startDate.value
    if (endDate.value) params.end_date = endDate.value
    
    const res = await api.get('/finance-info/metal-prices/', { params })
    metalPrices.value = res.data.data || []
    statistics.value = res.data.statistics || { min_price:0, max_price:0, avg_price:0 }
  } catch (err) {
    error.value = '데이터 로드 실패'
  }
}
```

## 6. 사용 기술 스택

- **프론트엔드**: Vue 3, Vuex, Chart.js, Axios
- **백엔드**: Django, Django REST Framework
- **데이터베이스**: SQLite/PostgreSQL
- **외부 API**: YouTube Data API, Hugging Face API, OpenAI API
- **배포**: 미정 (Vercel, Netlify, AWS 등)

## 7. 환경 변수 관리

- .env 파일을 통한 API 키 및 중요 정보 관리
- 보안을 위한 환경 변수 분리
- Vite 빌드 시스템을 활용한 환경 변수 주입

프로젝트는 사용자 인증부터 외부 API 통합, 데이터 시각화까지 다양한 기능을 제공하며, 반응형 디자인으로 모든 디바이스에서 일관된 사용자 경험을 제공합니다.