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

# 초기 설정 및 서버 실행을 위한 entrypoint 스크립트 생성
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Railway 배포 - 초기 설정 시작..."\n\
python setup_project.py\n\
echo "✅ 초기 설정 완료"\n\
echo "🔥 서버 시작..."\n\
exec "$@"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 포트 설정
EXPOSE 8000

# 초기 설정 후 서버 실행
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]