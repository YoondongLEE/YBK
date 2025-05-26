# 금융 정보 서비스 프로젝트

이 프로젝트는 사용자에게 다양한 금융 정보와 서비스를 제공하는 웹 애플리케이션입니다.

## 기능 소개

- **금융 상품 정보**: 예금 및 적금 상품 정보 조회 및 비교
- **개인화 추천 시스템**: 사용자 프로필 기반 맞춤형 금융상품 추천
- **금/은 가격 추이**: 금과 은의 가격 변동 추이 시각화
- **금융 아카데미**: 금융 교육 콘텐츠 제공
- **회원 기능**: 회원가입, 로그인, 마이페이지
- **금융 상품 가입**: 관심 있는 금융 상품 가입 및 관리
- **가까운 은행 찾기**: 지도에서 주변 은행 검색 및 경로 안내
- **마이페이지 차트**: 가입 상품 금리 분석 및 통계 시각화

## 프로젝트 설치 및 실행 가이드

### 사전 요구사항

- Python 3.9 이상
- Node.js 16 이상
- Django 4.2 이상
- Vue 3

### 🚀 빠른 시작 (권장)

#### 1. 프로젝트 클론
```bash
git clone [repository-url]
cd final-pjt
```

#### 2. 백엔드 자동 설정
```bash
cd back

# 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 환경변수 파일 생성 (.env)
# FINLIFE_API_KEY=your_api_key_here

# 🎯 원클릭 초기 설정 (모든 데이터 로드 자동화)
python setup_project.py
```

#### 3. 프론트엔드 설정
```bash
cd ../front

# 패키지 설치
npm install

# 환경변수 파일 생성 (.env)
# VITE_YOUTUBE_API_KEY="your_key"
# VITE_HUGGINGFACE_API_KEY="your_key"
# VITE_OPENAI_API_KEY="your_key"
# VITE_KAKAO_JAVASCRIPT_KEY="your_key"
# VITE_KAKAO_REST_API_KEY="your_key"
```

#### 4. 서버 실행
```bash
# 백엔드 서버 (새 터미널)
cd back
python manage.py runserver

# 프론트엔드 서버 (새 터미널)
cd front
npm run dev
```

브라우저에서 `http://localhost:5173` 접속

### 📋 상세 설정 가이드

#### 백엔드 설정 (Django)

1. **프로젝트 디렉토리로 이동**
```bash
cd final-pjt/back
```

2. **가상환경 생성 및 활성화**
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

3. **필요한 패키지 설치**
```bash
pip install -r requirements.txt
```

4. **환경 변수 설정**
```bash
# 파일 경로: final-pjt/back/.env
FINLIFE_API_KEY=your_finlife_api_key
```

5. **데이터베이스 및 초기 데이터 설정**

**자동 설정 (권장):**
```bash
python setup_project.py
```

**수동 설정:**
```bash
# 데이터베이스 마이그레이션
python manage.py migrate

# 금/은 가격 데이터 로드
python manage.py loaddata finance_info/fixtures/gold_prices.json finance_info/fixtures/silver_prices.json

# 더미 사용자 데이터 로드 (있는 경우)
python manage.py loaddata accounts/fixtures/dummy_accounts.json
python manage.py loaddata accounts/fixtures/dummy_deposits.json

# 서버 실행
python manage.py runserver

# 금융상품 데이터 로드 (브라우저에서 접속)
# http://localhost:8000/api/save-deposit-products/
# http://localhost:8000/api/save-saving-products/
```

#### 프론트엔드 설정 (Vue)

1. **프로젝트 디렉토리로 이동**
```bash
cd final-pjt/front
```

2. **필요한 패키지 설치**
```bash
npm install
```

3. **환경 변수 설정**
```bash
# 파일 경로: final-pjt/front/.env
VITE_YOUTUBE_API_KEY=your_youtube_api_key
VITE_HUGGINGFACE_API_KEY=your_huggingface_api_key
VITE_OPENAI_API_KEY=your_openai_api_key
VITE_KAKAO_JAVASCRIPT_KEY=your_kakao_js_key
VITE_KAKAO_REST_API_KEY=your_kakao_rest_api_key
```

4. **개발 서버 실행**
```bash
npm run dev
```

### 🔍 실행 확인

- **백엔드**: http://localhost:8000/admin/
- **프론트엔드**: http://localhost:5173
- **API 테스트**: 금융상품 목록이 정상 표시되는지 확인

### ⚠️ 문제 해결

```bash
# 더미 데이터가 없는 경우
python manage.py create_and_save_dummy_data

# 금융상품 데이터가 로드되지 않은 경우
# 브라우저에서 다음 URL 접속:
# http://localhost:8000/api/save-deposit-products/
# http://localhost:8000/api/save-saving-products/

# 패키지 설치 오류 시
pip install --upgrade pip
npm cache clean --force
```

## 📊 데이터 정보

### 초기 로드 데이터
- **금융상품 데이터**: 금융감독원 API에서 실시간 로드 (최신 금리 정보)
- **금/은 가격 데이터**: 2023.01.09 ~ 2024.12.01 기간 데이터
- **더미 사용자 데이터**: 1,000명의 가상 사용자 프로필 (분석용)
- **가입 이력 데이터**: 3,500건의 가입 기록 (추천 시스템용)

### 데이터 재로드 필요성
- ✅ **금융상품**: 최신 금리 반영을 위해 재로드 권장
- ✅ **금/은 가격**: 시세 업데이트를 위해 재로드 권장
- ⚪ **사용자/가입 데이터**: 기존 db.sqlite3에 포함되어 재로드 불필요

## 프로젝트 구조

```
final-pjt/
├── back/                    # 백엔드 (Django)
│   ├── accounts/           # 사용자 계정 관리 & 추천 시스템
│   ├── config/             # 프로젝트 설정
│   ├── deposits/           # 예금 상품 API
│   ├── savings/            # 적금 상품 API
│   ├── finance_academy/    # 금융 교육 컨텐츠
│   ├── finance_info/       # 금융 정보 (금/은 가격)
│   ├── youtube/            # 유튜브 콘텐츠 관리
│   ├── setup_project.py    # 🚀 원클릭 초기 설정 스크립트
│   └── requirements.txt    # Python 의존성
│
└── front/                  # 프론트엔드 (Vue 3)
    ├── public/             # 정적 파일
    └── src/                # 소스 코드
        ├── api/            # API 클라이언트
        ├── assets/         # 이미지 등 자산 파일
        ├── components/     # Vue 컴포넌트
        │   ├── charts/     # 차트 컴포넌트
        │   └── youtube/    # 유튜브 컴포넌트
        ├── router/         # Vue Router 설정
        ├── stores/         # Pinia 상태 관리
        └── views/          # 페이지 컴포넌트
```

## 주요 기능 사용법

### 개인화 추천 시스템
1. 회원가입 후 로그인
2. 마이페이지에서 개인정보 입력 (나이, 자산, 연봉, 금융성향)
3. 금융상품에 가입하여 선호도 데이터 축적
4. 홈페이지 하단 "추천 상품" 섹션에서 맞춤형 추천 확인

### 마이페이지 데이터 분석
1. 금융상품 가입 후 마이페이지 접속
2. "가입 상품 금리 분석" 섹션에서 차트 확인:
   - 상품별 최고 금리 비교 (막대그래프)
   - 가입 상품 분포 (도넛차트)
   - 예금 vs 적금 평균 금리 비교

### 금/은 가격 변동 추이 확인
1. 네비게이션 바에서 "금융정보" 메뉴 클릭
2. "금/은 가격 변동 추이" 카드 클릭
3. 금 또는 은 버튼을 선택하여 해당 금속의 가격 추이 확인
4. 시작일과 종료일을 설정하여 특정 기간의 데이터 확인 (2023.01.09 ~ 2024.12.01)

### 금리 비교 기능
1. 네비게이션 바에서 "금융정보" 메뉴 클릭
2. "금리 비교" 카드 클릭
3. 예금과 적금 탭을 전환하며 상품 비교
4. 기간, 은행 등 필터를 적용하여 원하는 조건의 상품 검색

### 금융 교육 콘텐츠
1. "금융 아카데미" 메뉴 접속
2. 유튜브 기반 금융 교육 영상 시청
3. 관심 있는 콘텐츠 저장 및 관리

## 기술 스택

### 프론트엔드
- **프레임워크**: Vue 3 (Composition API)
- **상태관리**: Pinia
- **라우팅**: Vue Router
- **HTTP 클라이언트**: Axios
- **차트**: Chart.js
- **지도**: Kakao Map API
- **UI**: Bootstrap, Custom CSS

### 백엔드
- **프레임워크**: Django 4.2, Django REST Framework
- **인증**: JWT (JSON Web Token)
- **데이터베이스**: SQLite
- **API**: RESTful API 설계
- **외부 API**: 금융감독원 금융상품 API, YouTube Data API

### 데이터 과학
- **추천 시스템**: 협업 필터링 (코사인 유사도)
- **데이터 분석**: Pandas, NumPy
- **시각화**: Chart.js를 통한 프론트엔드 차트
- **통계 분석**: 사용자 유사도 분석, 상품 선호도 패턴 분석

## 🎯 프로젝트 특징

### 데이터 기반 개인화
- 사용자 프로필과 행동 데이터를 활용한 맞춤형 추천
- 실시간 차트를 통한 개인 금융 데이터 시각화
- 통계적 분석 기반의 상품 추천 알고리즘

### 사용자 중심 UX/UI
- 직관적인 네비게이션과 반응형 디자인
- 실시간 데이터 업데이트 및 인터랙티브 차트
- 개인정보 수정 시 즉시 반영되는 반응형 인터페이스

### 확장 가능한 아키텍처
- 모듈화된 컴포넌트 구조
- RESTful API 설계로 확장성 확보
- 외부 API 연동을 통한 실시간 데이터 활용

---

이 README.md는 프로젝트를 처음 클론받은 사람이 빠르게 시작할 수 있도록 **원클릭 설정 스크립트**와 **상세 가이드**를 모두 제공합니다. 또한 핵심 기능인 **개인화 추천 시스템**과 **데이터 시각화** 기능의 사용법을 포함하여 프로젝트의 전체적인 가치를 이해할 수 있도록 작성되었습니다.