# 금융 정보 서비스 프로젝트

이 프로젝트는 사용자에게 다양한 금융 정보와 서비스를 제공하는 웹 애플리케이션입니다.

## 기능 소개

- **금융 상품 정보**: 예금 및 적금 상품 정보 조회 및 비교
- **금/은 가격 추이**: 금과 은의 가격 변동 추이 시각화
- **금융 아카데미**: 금융 교육 콘텐츠 제공
- **회원 기능**: 회원가입, 로그인, 마이페이지
- **금융 상품 가입**: 관심 있는 금융 상품 가입 및 관리
- **가까운 은행 찾기**: 지도에서 주변 은행 검색 및 경로 안내

## 프로젝트 설치 및 실행 가이드

### 사전 요구사항

- Python 3.9 이상
- Node.js 16 이상
- Django 4.2 이상
- Vue 3

### 백엔드 설정 (Django)

1. 프로젝트 디렉토리로 이동

```bash
cd final-pjt/back
```

2. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

3. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

4. 환경 변수 설정 (.env 파일 생성)
```bash
경로 : 'final-pjt/back/.env'
# 금융감독원 금융상품APIKEY
FINLIFE_API_KEY=key
```

```bash
경로 : 'final-pjt/front/.env'
VITE_YOUTUBE_API_KEY="key"

VITE_HUGGINGFACE_API_KEY="key"

VITE_OPENAI_API_KEY="key"

VITE_KAKAO_JAVASCRIPT_KEY="key"

VITE_KAKAO_REST_API_KEY="key"
```

5. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

6. 초기 데이터 로드 (금/은 가격 데이터 및 금융상품 데이터)

```bash
# 금/은 가격 데이터 로드
python manage.py loaddata finance_info/fixtures/gold_prices.json finance_info/fixtures/silver_prices.json

# 금융상품 데이터 로드 (서버 실행 후)
python manage.py runserver
```

서버가 실행된 상태에서 브라우저에서 다음 URL에 접속하여 API를 통해 데이터를 로드합니다:
- 정기예금: http://localhost:8000/api/save-deposit-products/
- 정기적금: http://localhost:8000/api/save-saving-products/

7. 서버 실행

```bash
python manage.py runserver
```

### 프론트엔드 설정 (Vue)

1. 프로젝트 디렉토리로 이동

```bash
cd final-pjt/front
```

2. 필요한 패키지 설치

```bash
npm install
```

3. 개발 서버 실행

```bash
npm run dev
```

4. 브라우저에서 접속

```
http://localhost:5173
```

## 프로젝트 구조

```
final-pjt/
├── back/              # 백엔드 (Django)
│   ├── accounts/      # 사용자 계정 관리
│   ├── config/        # 프로젝트 설정
│   ├── deposits/      # 예금 상품 API
│   ├── finance_academy/ # 금융 교육 컨텐츠
│   └── finance_info/  # 금융 정보 (금/은 가격 등)
│
└── front/             # 프론트엔드 (Vue 3)
    ├── public/        # 정적 파일
    └── src/           # 소스 코드
        ├── api/       # API 클라이언트
        ├── assets/    # 이미지 등 자산 파일
        ├── components/# Vue 컴포넌트
        ├── router/    # Vue Router 설정
        ├── stores/    # Pinia 상태 관리
        └── views/     # 페이지 컴포넌트
```

## 주요 기능 사용법

### 금/은 가격 변동 추이 확인

1. 네비게이션 바에서 "금융정보" 메뉴 클릭
2. "금/은 가격 변동 추이" 카드 클릭
3. 금 또는 은 버튼을 선택하여 해당 금속의 가격 추이 확인
4. 시작일과 종료일을 설정하여 특정 기간의 데이터 확인 (2023.01.09 ~ 2024.12.01 기간 내 선택)

### 금리 비교 기능

1. 네비게이션 바에서 "금융정보" 메뉴 클릭
2. "금리 비교" 카드 클릭
3. 예금과 적금 탭을 전환하며 상품 비교
4. 기간, 은행 등 필터를 적용하여 원하는 조건의 상품 검색

## 기술 스택

- **프론트엔드**: Vue 3, Vuex, Chart.js, Axios
- **백엔드**: Django, Django REST Framework
- **데이터베이스**: SQLite
- **기타**: JWT 인증, RESTful API


이 README.md는 프로젝트를 처음 클론받은 사람이 필요한 설치 과정과 초기 데이터 로드, 실행 방법에 대한 상세한 가이드를 제공합니다. 또한 주요 기능의 사용법도 포함하여 사용자가 빠르게 시작할 수 있도록 작성했습니다.이 README.md는 프로젝트를 처음 클론받은 사람이 필요한 설치 과정과 초기 데이터 로드, 실행 방법에 대한 상세한 가이드를 제공합니다. 또한 주요 기능의 사용법도 포함하여 사용자가 빠르게 시작할 수 있도록 작성했습니다.