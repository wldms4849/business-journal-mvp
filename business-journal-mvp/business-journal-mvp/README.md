# 사업일기 (Business Journal MVP)

로컬 사업자를 위한 **투명한 실행-로그-학습 SaaS**

## 🎯 서비스 개요

사장님의 **사업 일기 → 정보자산(DB) → 블로그/인스타 월관리 → 로그·진척 게이지·리포트**까지 연결하는 로컬 운영형 SaaS입니다.

### 핵심 기능

1. **사업 일기 가이드** - 일일/주간 템플릿, 자동 태깅
2. **정보자산 DB** - USP, FAQ, 전후 비교, 고객 리뷰 구조화
3. **월관리 실행** - 블로그/인스타 콘텐츠 생성·예약·발행
4. **투명 대시보드** - 진척 게이지, 로그, 리포트, 키워드 추천

## 📘 Product Spec

- [사업일기 Product Spec](docs/PRODUCT_SPEC.md)

## 🏗️ 기술 스택

### Backend
- **FastAPI** (Python 3.11)
- **PostgreSQL** (데이터베이스)
- **SQLAlchemy** + **Alembic** (ORM + 마이그레이션)
- **Redis** (캐시 + Celery)
- **OpenAI API** (LLM 통합)

### Frontend
- **Next.js 14** (React)
- **Tailwind CSS** + **shadcn/ui**
- **TypeScript**

### Infra
- **Docker** + **Docker Compose**
- **Railway / Render / Cloud Run** 배포 가능

## 🚀 빠른 시작

### 1. 사전 요구사항

- Docker & Docker Compose
- Node.js 18+ (Frontend 로컬 개발 시)
- Python 3.11+ (Backend 로컬 개발 시)

### 2. 환경 설정

```bash
# 프로젝트 클론
cd business-journal-mvp

# Backend 환경 변수 설정
cd backend
cp .env.example .env
# .env 파일을 열어 필수 값 입력 (DATABASE_URL, OPENAI_API_KEY 등)

cd ..
```

### 3. Docker로 실행

```bash
# ops 디렉토리에서 실행
cd ops
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 종료
docker-compose down
```

서비스 접속:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

### 4. 로컬 개발 (Docker 없이)

#### Backend

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# PostgreSQL 실행 (별도 설치 필요)
# .env 파일에서 DATABASE_URL 확인

# 마이그레이션
alembic upgrade head

# 개발 서버 실행
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

## 📊 데이터베이스 스키마

주요 테이블:
- `orgs` - 조직
- `users` - 사용자
- `journals` - 사업 일기
- `journal_tags` - 자동 태깅
- `assets` - 정보자산 (USP, FAQ 등)
- `content_briefs` - 콘텐츠 브리프
- `content_drafts` - 콘텐츠 초안
- `content_posts` - 발행된 콘텐츠
- `execution_logs` / `setup_logs` - 로그
- `reports` - 주/월 리포트
- `daily_recos` - 일일 추천
- `credit_wallets` / `credit_transactions` - 크레딧

상세 스키마: [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)

## 🧪 테스트

```bash
cd backend

# 단위 테스트
pytest tests/

# 커버리지 포함
pytest --cov=app tests/
```

## 📖 API 문서

서버 실행 후:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

주요 엔드포인트:
- `POST /api/journals` - 일기 생성
- `POST /api/journals/{id}/extract` - 태그 추출
- `POST /api/content/briefs/generate` - 브리프 생성
- `POST /api/content/drafts` - 초안 생성
- `GET /api/dashboard/summary` - 대시보드
- `POST /api/credits/consume` - 크레딧 소모

## 🎨 화면 구성

1. **홈 대시보드** - 진척 게이지, 오늘의 셀링 포인트, 키워드 추천
2. **사업 일기** - 작성, 업로드, 자동 태깅
3. **정보자산** - USP/FAQ 카드 뷰
4. **콘텐츠 월관리** - 칸반 보드 (브리프→초안→검수→발행)
5. **로그·리포트** - 설정/집행 로그, 주/월 리포트
6. **크레딧** - 잔액, 거래 내역, 되돌리기

## 💳 크레딧 시스템

- **무료**: 일기 기록, 기본 태깅, 기초 대시보드
- **크레딧 소모**: 콘텐츠 생성, 멀티채널 발행, 고급 리포트
- **되돌리기**: 24시간 내 1회 가능

## 📝 LLM 프롬프트

모든 프롬프트는 버전 관리됩니다: `backend/app/prompts/templates.py`

주요 프롬프트:
- A. 일기 → 태깅
- B. DB → 콘텐츠 브리프
- C. 브리프 → 초안 (인스타/블로그)
- D. 리포트 원인 → 대응
- E. 키워드 추천
- F. USP 추출

상세 문서: [docs/PROMPTS.md](docs/PROMPTS.md)

## 🔧 설정

### 환경 변수

주요 환경 변수 (`.env`):
- `DATABASE_URL` - PostgreSQL 연결 문자열
- `REDIS_URL` - Redis 연결 문자열
- `OPENAI_API_KEY` - OpenAI API 키
- `OPENAI_MODEL` - 사용할 모델 (기본: gpt-4)
- `S3_*` - S3 스토리지 설정 (이미지/영상)
- `DEFAULT_FREE_CREDITS` - 기본 무료 크레딧

전체 목록: `backend/.env.example`

## 📦 배포

### Railway

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 생성 및 배포
railway init
railway up
```

### Render

1. Render 대시보드에서 "New +" 클릭
2. "Web Service" 선택
3. GitHub 저장소 연결
4. Build Command: `cd backend && pip install -r requirements.txt`
5. Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Cloud Run

```bash
# gcloud CLI 설치 및 인증
gcloud auth login

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# 배포
gcloud run deploy business-journal \
  --source ./backend \
  --platform managed \
  --region asia-northeast3
```

## 🧰 개발 가이드

### 새 마이그레이션 생성

```bash
cd backend
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
```

### 새 API 엔드포인트 추가

1. `app/schemas/schemas.py`에 스키마 정의
2. `app/api/routes/`에 라우터 파일 생성
3. `app/main.py`에 라우터 등록

### LLM 프롬프트 수정

1. `app/prompts/templates.py` 수정
2. 버전 주석 업데이트
3. 테스트 후 커밋

## 🐛 트러블슈팅

### 데이터베이스 연결 오류

```bash
# PostgreSQL 실행 확인
docker-compose ps

# 로그 확인
docker-compose logs postgres
```

### OpenAI API 오류

- API 키 확인: `.env` 파일의 `OPENAI_API_KEY`
- 할당량 확인: https://platform.openai.com/usage
- 타임아웃 증가: `.env`의 `OPENAI_TIMEOUT`

## 📄 라이센스

MIT License

## 👥 팀

- **Product**: MVP 기획 및 요구사항 정의
- **Backend**: FastAPI + PostgreSQL + LLM 통합
- **Frontend**: Next.js + shadcn/ui

## 🗺️ 로드맵

- [x] MVP 1.0 - 핵심 기능 구현
- [ ] v1.1 - 실제 인스타/블로그 API 연동
- [ ] v1.2 - 키워드 API 연동
- [ ] v1.3 - Make/Zapier 웹훅 연동
- [ ] v2.0 - 멀티 테넌트, 역할 관리 강화
- [ ] v2.1 - 모바일 앱

## 📤 GitHub에 올리기

이 프로젝트를 GitHub에 업로드하는 방법:

### 🚀 제일 쉬운 방법 (자동 스크립트)
```bash
# Windows: upload-to-github.bat 더블클릭
# Mac: ./upload-to-github.sh 실행
```

### 📚 상세 가이드
- **초보자용**: `GITHUB_GUIDE.md` - 단계별 그림 설명
- **빠른 요약**: `QUICK_GITHUB.md` - 30초 요약
- **시각 자료**: `UPLOAD_VISUAL_GUIDE.md` - 3가지 방법 비교

## 📞 문의

이슈 또는 PR을 통해 문의해 주세요.

---

**Built with ❤️ for local business owners**
