# 프로젝트 구조

```
business-journal-mvp/
├── README.md                 # 프로젝트 개요 및 전체 가이드
├── QUICKSTART.md            # 5분 빠른 시작 가이드
│
├── backend/                  # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py          # FastAPI 애플리케이션 엔트리포인트
│   │   ├── core/
│   │   │   └── config.py    # 설정 및 DB 연결
│   │   ├── models/
│   │   │   └── models.py    # SQLAlchemy 모델 (전체 스키마)
│   │   ├── schemas/
│   │   │   └── schemas.py   # Pydantic 스키마 (요청/응답)
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── journals.py    # 일기 API
│   │   │       ├── content.py     # 콘텐츠 API
│   │   │       ├── dashboard.py   # 대시보드 API
│   │   │       └── credits.py     # 크레딧 API
│   │   ├── services/
│   │   │   └── llm_service.py    # LLM 통합 서비스
│   │   └── prompts/
│   │       └── templates.py       # LLM 프롬프트 템플릿
│   ├── alembic/              # 데이터베이스 마이그레이션
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/                # 테스트
│   ├── requirements.txt      # Python 의존성
│   ├── .env.example         # 환경 변수 예시
│   ├── Dockerfile           # Docker 이미지
│   ├── alembic.ini          # Alembic 설정
│   └── seed_data.py         # 시드 데이터 스크립트
│
├── frontend/                 # Next.js 프론트엔드
│   ├── app/
│   │   ├── page.tsx         # 메인 페이지
│   │   └── layout.tsx       # 레이아웃
│   ├── components/          # React 컴포넌트
│   │   ├── dashboard-summary.tsx
│   │   ├── journal-form.tsx
│   │   └── content-kanban.tsx
│   ├── lib/                 # 유틸리티
│   ├── public/              # 정적 파일
│   ├── package.json         # Node 의존성
│   ├── next.config.js       # Next.js 설정
│   ├── tailwind.config.js   # Tailwind 설정
│   └── Dockerfile           # Docker 이미지
│
├── ops/                      # 운영 및 배포
│   ├── docker-compose.yml   # Docker Compose 설정
│   └── DEPLOYMENT.md        # 배포 가이드
│
└── docs/                     # 문서
    ├── PROMPTS.md           # LLM 프롬프트 상세
    └── TESTS.md             # 테스트 가이드
```

## 주요 파일 설명

### Backend

#### `app/main.py`
FastAPI 애플리케이션의 진입점. CORS 설정, 라우터 등록, 헬스 체크 엔드포인트 포함.

#### `app/core/config.py`
- 환경 변수 로딩
- 데이터베이스 연결 설정
- 설정 클래스 (Settings)

#### `app/models/models.py`
모든 데이터베이스 테이블 정의:
- Organization, User, Channel
- Journal, JournalTag, Asset
- ContentBrief, ContentDraft, ContentPost
- ExecutionLog, SetupLog
- Report, ProgressPlan, DailyRecommendation
- CreditWallet, CreditTransaction, UndoSlot

#### `app/schemas/schemas.py`
Pydantic 스키마 (API 요청/응답 검증):
- XxxCreate - 생성 요청
- XxxUpdate - 업데이트 요청
- Xxx - 응답 스키마

#### `app/api/routes/`
RESTful API 엔드포인트:
- `journals.py`: 일기 CRUD, 태그 추출
- `content.py`: 브리프/초안/발행
- `dashboard.py`: 대시보드, 추천, 로그
- `credits.py`: 크레딧 소모/되돌리기

#### `app/services/llm_service.py`
OpenAI API 통합:
- `extract_journal_tags()` - 일기 태깅
- `generate_content_brief()` - 브리프 생성
- `generate_instagram_draft()` - 인스타 초안
- `generate_blog_draft()` - 블로그 초안
- `analyze_report()` - 리포트 분석
- `recommend_keywords()` - 키워드 추천

#### `app/prompts/templates.py`
모든 LLM 프롬프트 템플릿과 파라미터 정의.

#### `seed_data.py`
데모용 시드 데이터 생성:
- 2개 조직 (카페, 미용실)
- 14일치 일기
- 콘텐츠, 리포트 샘플

### Frontend

#### `app/page.tsx`
메인 대시보드 페이지:
- 진척 게이지
- 오늘의 셀링 포인트
- 저경쟁 키워드
- 일기 작성 폼
- 콘텐츠 칸반

#### `components/`
재사용 가능한 React 컴포넌트:
- `dashboard-summary.tsx` - 대시보드 요약
- `journal-form.tsx` - 일기 작성 폼
- `content-kanban.tsx` - 콘텐츠 관리 칸반

### Ops

#### `docker-compose.yml`
전체 스택 오케스트레이션:
- PostgreSQL (데이터베이스)
- Redis (캐시/큐)
- Backend (FastAPI)
- Frontend (Next.js)

### Docs

#### `PROMPTS.md`
LLM 프롬프트 전체 문서:
- 각 프롬프트 용도
- 시스템/유저 프롬프트
- 파라미터 설정
- 예시 입출력

#### `TESTS.md`
테스트 시나리오 및 가이드:
- 수동 테스트 시나리오
- curl 명령어 예시
- 검증 포인트
- 단위/통합 테스트

---

## API 엔드포인트 요약

### Journals
- `POST /api/journals` - 일기 생성
- `GET /api/journals` - 일기 목록
- `GET /api/journals/{id}` - 일기 상세
- `POST /api/journals/{id}/extract` - 태그 추출
- `GET /api/journals/{id}/tags` - 태그 조회

### Content
- `POST /api/content/briefs` - 브리프 생성
- `POST /api/content/briefs/generate` - 자동 브리프 생성
- `POST /api/content/drafts` - 초안 생성
- `GET /api/content/drafts` - 초안 목록
- `PUT /api/content/drafts/{id}/status` - 상태 업데이트
- `POST /api/content/posts/schedule` - 예약 발행
- `GET /api/content/posts` - 발행 목록

### Dashboard
- `GET /api/dashboard/summary` - 대시보드 요약
- `GET /api/dashboard/recos` - 일일 추천
- `POST /api/dashboard/progress/plan` - 진척 계획 생성
- `POST /api/dashboard/progress/tick` - 진척 기록
- `GET /api/dashboard/logs/execution` - 집행 로그
- `GET /api/dashboard/logs/setup` - 설정 로그

### Credits
- `GET /api/credits/wallet` - 지갑 조회
- `POST /api/credits/consume` - 크레딧 소모
- `POST /api/credits/undo` - 되돌리기
- `GET /api/credits/transactions` - 거래 내역

---

## 데이터 흐름

### 1. 일기 작성 → 정보자산

```
사용자 입력 (일기)
  ↓
Journal 테이블 저장
  ↓
LLM 태그 추출
  ↓
JournalTag 테이블 저장
  ↓
Asset 테이블 저장 (USP, FAQ 등)
```

### 2. 콘텐츠 생성

```
Asset 조회 (USP, 키워드)
  ↓
LLM 브리프 생성
  ↓
ContentBrief 저장
  ↓
LLM 초안 생성
  ↓
ContentDraft 저장 (검수 대기)
  ↓
검수 승인
  ↓
ContentPost 예약/발행
```

### 3. 대시보드

```
ProgressPlan 조회
  ↓
ProgressTick 조회
  ↓
진척 게이지 계산
  ↓
DailyRecommendation 조회/생성
  ↓
최근 로그 조회
  ↓
대시보드 렌더링
```

---

## 확장 포인트

### Backend

1. **새 API 엔드포인트**
   - `app/api/routes/` 에 새 파일 추가
   - `app/main.py` 에 라우터 등록

2. **새 LLM 프롬프트**
   - `app/prompts/templates.py` 에 추가
   - `app/services/llm_service.py` 에 메서드 추가

3. **새 데이터 모델**
   - `app/models/models.py` 에 모델 추가
   - `alembic revision --autogenerate` 실행

### Frontend

1. **새 페이지**
   - `app/` 에 새 디렉토리 추가
   - `page.tsx` 작성

2. **새 컴포넌트**
   - `components/` 에 추가
   - 재사용 가능하게 설계

---

**참고**: 상세한 API 문서는 http://localhost:8000/docs 에서 확인
