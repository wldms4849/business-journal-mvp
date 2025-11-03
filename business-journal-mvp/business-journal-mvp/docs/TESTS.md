# 테스트 가이드

## 테스트 시나리오

### 1. 일기 작성 및 태깅

**시나리오**: 사업 일기를 작성하고 자동 태깅이 동작하는지 확인

```bash
# 1. 일기 생성
curl -X POST http://localhost:8000/api/journals \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": 1,
    "author_id": 1,
    "date": "2025-11-03T14:00:00",
    "title": "평일 오후 손님 증가",
    "content_md": "오늘은 평일 오후에 재택근무 손님이 많이 왔습니다...",
    "media_urls": [],
    "checklist_json": []
  }'

# 기대 결과: 201 Created, journal_id 반환

# 2. 태그 추출
curl -X POST http://localhost:8000/api/journals/1/extract

# 기대 결과:
# {
#   "usps": ["조용한 작업 공간", ...],
#   "menu": ["아메리카노", ...],
#   "events": [],
#   "customer_quotes": ["..."],
#   "sentiment": {"overall": "positive"},
#   "time_refs": ["2025-11-03 14:00 ..."]
# }
```

**검증 포인트**:
- [ ] 일기가 DB에 저장되는가?
- [ ] 태그 추출이 1분 내에 완료되는가?
- [ ] USP가 Asset 테이블에도 저장되는가?
- [ ] 실행 로그가 기록되는가?

---

### 2. 콘텐츠 생성 플로우

**시나리오**: 브리프 생성 → 초안 작성 → 검수 → 예약

```bash
# 1. 브리프 자동 생성
curl -X POST http://localhost:8000/api/content/briefs/generate \
  -G \
  --data-urlencode "org_id=1" \
  --data-urlencode "channel_type=instagram" \
  --data-urlencode "business_type=cafe"

# 기대 결과: brief_id와 브리프 내용

# 2. 초안 생성
curl -X POST http://localhost:8000/api/content/drafts \
  -G \
  --data-urlencode "brief_id=1"

# 기대 결과: draft_id와 초안 내용 (hook, body, hashtags 등)

# 3. 초안 상태 업데이트 (검수 승인)
curl -X PUT http://localhost:8000/api/content/drafts/1/status \
  -G \
  --data-urlencode "new_status=approved" \
  --data-urlencode "user_id=1"

# 4. 예약 발행
curl -X POST http://localhost:8000/api/content/posts/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id": 1,
    "channel_id": 1,
    "scheduled_at": "2025-11-04T10:00:00",
    "created_by": 1
  }'
```

**검증 포인트**:
- [ ] 브리프가 USP와 키워드를 반영하는가?
- [ ] 초안이 브리프의 방향성을 따르는가?
- [ ] 모든 단계에서 로그가 기록되는가?
- [ ] 예약 시간이 올바르게 저장되는가?

---

### 3. 대시보드 조회

**시나리오**: 대시보드에서 진척 게이지, 추천, 로그 확인

```bash
# 1. 대시보드 요약
curl http://localhost:8000/api/dashboard/summary?org_id=1

# 기대 결과:
# {
#   "week_progress": {
#     "percentage": 70,
#     "completed": 7,
#     "total": 10
#   },
#   "todays_usps": ["조용한 작업 공간", ...],
#   "low_comp_keywords": ["동네 카페", ...],
#   "recent_logs": [...],
#   "credit_balance": 95
# }

# 2. 일일 추천 조회
curl http://localhost:8000/api/dashboard/recos?org_id=1&date=2025-11-03

# 3. 실행 로그 조회
curl http://localhost:8000/api/dashboard/logs/execution?org_id=1&limit=20
```

**검증 포인트**:
- [ ] 진척 게이지가 올바르게 계산되는가?
- [ ] 추천이 생성되지 않았을 때 자동 생성되는가?
- [ ] 로그가 시간순으로 정렬되는가?

---

### 4. 크레딧 시스템

**시나리오**: 크레딧 소모 및 되돌리기

```bash
# 1. 지갑 조회
curl http://localhost:8000/api/credits/wallet?org_id=1

# 기대 결과: balance=100

# 2. 크레딧 소모
curl -X POST http://localhost:8000/api/credits/consume \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": 1,
    "trigger": "content_generation",
    "amount": 5,
    "meta": {"draft_id": 1}
  }'

# 기대 결과:
# {
#   "success": true,
#   "transaction_id": 1,
#   "new_balance": 95,
#   "can_undo": true,
#   "undo_expires_at": "2025-11-04T14:00:00"
# }

# 3. 되돌리기
curl -X POST http://localhost:8000/api/credits/undo \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": 1,
    "transaction_id": 1
  }'

# 기대 결과: balance=100으로 복구

# 4. 거래 내역
curl http://localhost:8000/api/credits/transactions?org_id=1
```

**검증 포인트**:
- [ ] 소모 전 잔액 확인이 동작하는가?
- [ ] 되돌리기 슬롯이 24시간 후 만료되는가?
- [ ] 모든 거래가 로그에 기록되는가?
- [ ] 잔액 부족 시 에러 처리가 되는가?

---

### 5. 리포트 생성

**시나리오**: 주간/월간 리포트 생성

```bash
# 주간 리포트 생성 (수동 트리거)
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": 1,
    "period_type": "weekly"
  }'

# 기대 결과:
# {
#   "report_id": 1,
#   "causes": [
#     {
#       "description": "재택근무 증가로 인한...",
#       "evidence_links": [...],
#       "confidence": 0.8
#     }
#   ],
#   "actions": [
#     {
#       "description": "작업 공간 관련 콘텐츠 강화",
#       "priority": "high"
#     }
#   ]
# }
```

**검증 포인트**:
- [ ] 원인 3개 이상, 대응 3개 이상이 생성되는가?
- [ ] 각 원인에 근거 링크가 포함되는가?
- [ ] 리포트가 PDF로 내보내기 가능한가?

---

## 단위 테스트

```bash
# Backend 테스트 실행
cd backend
pytest tests/ -v

# 커버리지 포함
pytest --cov=app tests/ --cov-report=html

# 특정 테스트만
pytest tests/test_journals.py -v
```

### 테스트 파일 구조

```
tests/
├── __init__.py
├── conftest.py           # 공통 fixture
├── test_journals.py      # 일기 API 테스트
├── test_content.py       # 콘텐츠 API 테스트
├── test_credits.py       # 크레딧 테스트
├── test_dashboard.py     # 대시보드 테스트
└── test_prompts.py       # LLM 프롬프트 테스트
```

---

## 통합 테스트

### E2E 시나리오: 전체 플로우

```bash
# 스크립트 실행
./run_e2e_test.sh

# 또는 수동으로:
# 1. 일기 작성
# 2. 태그 추출
# 3. 브리프 생성
# 4. 초안 작성
# 5. 검수 승인
# 6. 예약 발행
# 7. 크레딧 소모
# 8. 대시보드 확인
# 9. 리포트 생성
# 10. 되돌리기 테스트
```

---

## 성능 테스트

### 목표 지표

- **일기 → 태깅**: < 1분
- **브리프 → 초안**: < 30초
- **대시보드 로딩**: < 2초
- **리포트 생성**: < 1분

### 부하 테스트

```bash
# Locust 사용
pip install locust

# locustfile.py 실행
locust -f tests/load/locustfile.py
```

---

## 수용 기준 (AC) 체크리스트

- [x] 일기 작성→자동 태깅→정보자산 생성 1분 내 완료
- [x] 월관리 칸반에서 브리프→초안→예약 전 흐름 동작
- [x] 대시보드에 주간 진척 게이지 노출
- [x] 주/월 리포트에 원인→대응 3개 이상 + 근거 링크
- [x] 로그(설정/집행/과금) 검색/필터 가능
- [x] 크레딧 소모 시 사전 고지 + 로그 + 되돌리기 동작

---

## 트러블슈팅

### OpenAI API 타임아웃

```python
# .env에서 타임아웃 증가
OPENAI_TIMEOUT=120
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 실행 확인
docker-compose ps postgres

# 마이그레이션 재실행
alembic upgrade head
```

### 크레딧 잔액 오류

```sql
-- 수동으로 잔액 조정
UPDATE credit_wallets SET balance = 100 WHERE org_id = 1;
```

---

**테스트 시 문의**: 이슈로 등록해 주세요.
