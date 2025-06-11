FROM python:3.9-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# DATABASE_URL 사용하는 개선된 스크립트
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Railway 배포 시작..."\n\
echo "🔍 DATABASE_URL 확인: ${DATABASE_URL:0:30}..."\n\
if [ -z "$DATABASE_URL" ]; then\n\
  echo "❌ DATABASE_URL이 설정되지 않았습니다!"\n\
  exit 1\n\
fi\n\
echo "⏳ 데이터베이스 연결 테스트..."\n\
python -c "import dj_database_url, psycopg2; db_config = dj_database_url.parse(\"$DATABASE_URL\"); psycopg2.connect(**db_config); print(\"✅ 데이터베이스 연결 성공\")" || {\n\
  echo "❌ 데이터베이스 연결 실패. 재시도 중..."\n\
  sleep 5\n\
  python -c "import dj_database_url, psycopg2; db_config = dj_database_url.parse(\"$DATABASE_URL\"); psycopg2.connect(**db_config); print(\"✅ 데이터베이스 연결 성공 (재시도)\")" || {\n\
    echo "❌ 데이터베이스 연결 최종 실패"\n\
    exit 1\n\
  }\n\
}\n\
echo "🔧 마이그레이션 실행..."\n\
python manage.py migrate\n\
echo "✅ 마이그레이션 완료"\n\
echo "📁 정적 파일 수집..."\n\
python manage.py collectstatic --noinput\n\
echo "✅ 정적 파일 수집 완료"\n\
echo "🔥 서버 시작..."\n\
exec "$@"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 포트 설정
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]