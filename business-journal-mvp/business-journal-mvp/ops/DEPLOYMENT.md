# 배포 가이드

## 배포 옵션

사업일기 MVP는 다양한 플랫폼에 배포할 수 있습니다:

1. **Railway** (권장) - 간단한 설정, PostgreSQL 포함
2. **Render** - 무료 티어 제공
3. **Cloud Run** - 구글 클라우드
4. **Docker** - 직접 호스팅

---

## 1. Railway 배포

### 사전 준비

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login
```

### Backend 배포

```bash
cd backend

# Railway 프로젝트 생성
railway init

# PostgreSQL 서비스 추가
railway add postgresql

# 환경 변수 설정
railway vars set OPENAI_API_KEY=your-api-key
railway vars set OPENAI_MODEL=gpt-4

# 배포
railway up

# 도메인 확인
railway domain
```

### Frontend 배포

```bash
cd frontend

# Railway 프로젝트 생성
railway init

# 환경 변수 설정
railway vars set NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# 배포
railway up
```

**예상 비용**: $5-20/월 (사용량에 따라)

---

## 2. Render 배포

### Backend

1. [Render 대시보드](https://dashboard.render.com) 접속
2. "New +" → "Web Service"
3. GitHub 저장소 연결
4. 설정:
   - **Name**: business-journal-api
   - **Environment**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (또는 Starter $7/월)

5. 환경 변수 추가:
   ```
   DATABASE_URL=(Render PostgreSQL 연결 문자열)
   REDIS_URL=(Render Redis 연결 문자열)
   OPENAI_API_KEY=your-api-key
   ```

6. PostgreSQL 서비스 생성:
   - "New +" → "PostgreSQL"
   - Free 티어 선택

### Frontend

1. "New +" → "Static Site"
2. 설정:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/out`

**예상 비용**: Free (제한적) 또는 $7-14/월

---

## 3. Google Cloud Run 배포

### 사전 준비

```bash
# gcloud CLI 설치 및 인증
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Backend 배포

```bash
cd backend

# 컨테이너 빌드 및 배포
gcloud run deploy business-journal-api \
  --source . \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DATABASE_URL,OPENAI_API_KEY=$OPENAI_API_KEY
```

### Cloud SQL (PostgreSQL) 설정

```bash
# Cloud SQL 인스턴스 생성
gcloud sql instances create business-journal-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-northeast3

# 데이터베이스 생성
gcloud sql databases create business_journal \
  --instance=business-journal-db
```

**예상 비용**: $10-30/월

---

## 4. Docker 직접 호스팅

### VPS 서버 (DigitalOcean, Linode 등)

```bash
# 서버에 접속
ssh user@your-server-ip

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 프로젝트 클론
git clone https://github.com/your-repo/business-journal-mvp.git
cd business-journal-mvp

# 환경 변수 설정
cd backend
cp .env.example .env
nano .env  # 값 입력

# 실행
cd ../ops
docker-compose up -d

# Nginx 리버스 프록시 설정
sudo nano /etc/nginx/sites-available/business-journal
```

**Nginx 설정 예시**:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**예상 비용**: $5-20/월 (VPS)

---

## 환경 변수 체크리스트

배포 전 필수 환경 변수:

### Backend

- [x] `DATABASE_URL` - PostgreSQL 연결 문자열
- [x] `REDIS_URL` - Redis 연결 문자열
- [x] `OPENAI_API_KEY` - OpenAI API 키
- [ ] `OPENAI_MODEL` - 사용할 모델 (선택)
- [ ] `S3_*` - S3 스토리지 (이미지/영상 업로드 시)
- [x] `SECRET_KEY` - JWT 시크릿 (프로덕션에서 변경)

### Frontend

- [x] `NEXT_PUBLIC_API_URL` - Backend API URL

---

## 데이터베이스 마이그레이션

배포 후 첫 실행 시:

```bash
# Railway/Render
railway run alembic upgrade head

# Cloud Run (로컬에서 실행)
gcloud run jobs execute db-migrate \
  --region asia-northeast3

# Docker
docker-compose exec backend alembic upgrade head
```

---

## 시드 데이터 생성

데모/테스트용:

```bash
# Railway
railway run python seed_data.py

# Render
render run python seed_data.py

# Docker
docker-compose exec backend python seed_data.py
```

---

## 모니터링 및 로깅

### Railway

```bash
# 로그 확인
railway logs

# 메트릭 확인
railway metrics
```

### Render

- 대시보드에서 로그 및 메트릭 확인

### Cloud Run

```bash
# 로그 확인
gcloud run services logs read business-journal-api --region=asia-northeast3

# Cloud Logging 대시보드
https://console.cloud.google.com/logs
```

---

## SSL/HTTPS 설정

### Railway/Render

- 자동으로 SSL 인증서 발급

### Docker + Nginx

```bash
# Certbot 설치
sudo apt-get install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com
```

---

## 백업 전략

### 데이터베이스 백업

```bash
# PostgreSQL 덤프
pg_dump -h hostname -U username database_name > backup.sql

# 복구
psql -h hostname -U username database_name < backup.sql
```

### 자동 백업 설정

- **Railway**: 자동 백업 지원
- **Render**: 유료 플랜에서 자동 백업
- **Cloud SQL**: 자동 백업 기본 활성화

---

## 성능 최적화

### Backend

1. **Gunicorn 사용** (프로덕션):
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Redis 캐싱**:
   - 대시보드 데이터 캐싱 (5분)
   - 일일 추천 캐싱 (24시간)

3. **데이터베이스 인덱스**:
   - `journals.org_id`
   - `journals.date`
   - `assets.org_id, asset_type`

### Frontend

1. **정적 빌드**:
   ```bash
   npm run build
   npm run export
   ```

2. **이미지 최적화**: Next.js Image 컴포넌트 사용

3. **CDN**: Cloudflare 또는 Vercel Edge 사용

---

## 보안 체크리스트

- [ ] 환경 변수에 시크릿 저장 (코드에 하드코딩 X)
- [ ] HTTPS 사용
- [ ] CORS 설정 확인
- [ ] Rate Limiting 설정
- [ ] SQL Injection 방지 (SQLAlchemy ORM 사용)
- [ ] XSS 방지 (입력 검증)
- [ ] 정기적인 의존성 업데이트

---

## 트러블슈팅

### "Module not found" 오류

```bash
# 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

### 데이터베이스 연결 타임아웃

```python
# .env에서 풀 크기 조정
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### OpenAI API 429 오류

- API 키 할당량 확인
- Rate Limiting 구현
- 재시도 로직 추가

---

## 롤백

문제 발생 시:

```bash
# Railway
railway rollback

# Docker
docker-compose down
git checkout previous-commit
docker-compose up -d
```

---

## 문의

배포 관련 문제는 이슈로 등록해 주세요.
