FROM python:3.11-slim

# 작업 디렉터리 설정
WORKDIR /app

# 시스템 의존성 설치 (필요한 경우 대비 및 pg_isready 사용을 위한 postgresql-client 설치)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 및 필요한 폴더 복사
COPY src/ ./src/
COPY db/ ./db/

# 실행 시 버퍼링 방지 (컨테이너 내 실시간 로깅 보장)
ENV PYTHONUNBUFFERED=1

# 기본 실행 명령
CMD ["python", "src/generator.py"]
