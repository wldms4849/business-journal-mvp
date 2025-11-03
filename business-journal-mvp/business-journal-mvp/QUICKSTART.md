# 🚀 빠른 시작 가이드

## 5분 안에 시작하기

### 1단계: 프로젝트 다운로드

```bash
# 프로젝트 압축 해제
cd business-journal-mvp
```

### 2단계: 환경 설정

```bash
# Backend 환경 변수 설정
cd backend
cp .env.example .env

# 필수 항목만 편집
nano .env
```

**최소 필수 설정**:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/business_journal
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3단계: Docker로 실행

```bash
cd ../ops
docker-compose up -d
```

### 4단계: 접속 확인

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

### 5단계: 시드 데이터 생성

```bash
docker-compose exec backend python seed_data.py
```

---

## ✅ 동작 확인

### 1. 일기 작성 테스트

```bash
curl -X POST http://localhost:8000/api/journals \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": 1,
    "author_id": 1,
    "date": "2025-11-03T14:00:00",
    "title": "테스트 일기",
    "content_md": "오늘은 손님이 많았습니다.",
    "media_urls": [],
    "checklist_json": []
  }'
```

### 2. 태그 추출 테스트

```bash
curl -X POST http://localhost:8000/api/journals/1/extract
```

### 3. 대시보드 확인

브라우저에서 http://localhost:3000 접속

---

## 📦 포함된 내용

### Backend (FastAPI)
- ✅ 사업 일기 CRUD
- ✅ 자동 태깅 (LLM)
- ✅ 콘텐츠 생성 (브리프→초안)
- ✅ 대시보드 & 추천
- ✅ 크레딧 시스템
- ✅ 로그 & 리포트

### Frontend (Next.js)
- ✅ 대시보드 뷰
- ✅ 일기 작성 폼
- ✅ 콘텐츠 칸반
- ✅ Tailwind + shadcn/ui

### 인프라
- ✅ Docker Compose
- ✅ PostgreSQL 15
- ✅ Redis 7
- ✅ Alembic 마이그레이션

### 문서
- ✅ README.md - 전체 개요
- ✅ PROMPTS.md - LLM 프롬프트
- ✅ TESTS.md - 테스트 가이드
- ✅ DEPLOYMENT.md - 배포 가이드

---

## 🎯 다음 단계

### 개발 환경

```bash
# Backend 로컬 개발
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend 로컬 개발
cd frontend
npm install
npm run dev
```

### 커스터마이징

1. **프롬프트 수정**: `backend/app/prompts/templates.py`
2. **API 추가**: `backend/app/api/routes/`
3. **UI 수정**: `frontend/app/` 및 `frontend/components/`

### 배포

```bash
# Railway (권장)
railway login
railway init
railway up

# 상세: ops/DEPLOYMENT.md 참조
```

---

## 🆘 문제 해결

### OpenAI API 키 오류

```bash
# .env 파일 확인
cat backend/.env | grep OPENAI_API_KEY

# 키가 비어있으면 실제 키로 교체
```

### Docker 오류

```bash
# 로그 확인
docker-compose logs backend
docker-compose logs postgres

# 재시작
docker-compose down
docker-compose up -d
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 실행 확인
docker-compose ps postgres

# 마이그레이션 재실행
docker-compose exec backend alembic upgrade head
```

---

## 📚 더 알아보기

- **전체 문서**: README.md
- **API 문서**: http://localhost:8000/docs
- **프롬프트**: docs/PROMPTS.md
- **테스트**: docs/TESTS.md
- **배포**: ops/DEPLOYMENT.md

---

## 💡 팁

### 개발 모드 vs 프로덕션

```bash
# 개발 (자동 리로드)
docker-compose up

# 프로덕션 (백그라운드)
docker-compose up -d
```

### 로그 모니터링

```bash
# 실시간 로그
docker-compose logs -f

# 특정 서비스만
docker-compose logs -f backend
```

### 데이터 초기화

```bash
# 컨테이너 정지 및 볼륨 삭제
docker-compose down -v

# 재시작 및 시드 데이터
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed_data.py
```

---

**준비 완료!** 🎉

이제 사업일기를 사용할 준비가 되었습니다.
문의사항은 이슈로 등록해 주세요.
