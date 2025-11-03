# LLM 프롬프트 문서

버전: 1.0.0  
마지막 업데이트: 2025-11-03

## 개요

이 문서는 사업일기 서비스에서 사용하는 모든 LLM 프롬프트와 파라미터를 정의합니다.

## 프롬프트 목록

### A. 일기 → 태깅

**목적**: 사업 일기에서 구조화된 정보 추출

**System Prompt**:
```
당신은 로컬 비즈니스 운영 일기를 분석하여 구조화된 정보를 추출하는 전문가입니다.
다음 운영 일기에서 USP(고유 셀링 포인트), 메뉴/서비스, 행사/프로모션, 고객 코멘트, 감성, 시간·날짜 참조를 JSON으로 추출하세요.
```

**User Prompt Template**:
```
운영 일기:
{journal_content}

위 일기를 분석하여 다음 JSON 스키마에 맞춰 정보를 추출하세요:

{
  "usps": ["고유 셀링 포인트 1", ...],
  "menu": ["메뉴/서비스 항목 1", ...],
  "events": [{
    "type": "promotion|launch|special_hours|other",
    "title": "이벤트 제목",
    "period": "기간"
  }],
  "customer_quotes": ["고객 말 인용 1", ...],
  "sentiment": {
    "overall": "positive|neutral|negative",
    "aspects": {
      "가격": "positive|neutral|negative",
      "품질": "positive|neutral|negative"
    }
  },
  "time_refs": ["시간 참조 1", ...]
}
```

**파라미터**:
- `temperature`: 0.3 (일관성 있는 추출)
- `max_tokens`: 2000

**예시 입출력**:

입력:
```
오늘은 평일 오후 2시부터 5시까지 walk-in 손님이 6명 왔습니다.
남자 셋팅펌 문의가 많았는데, 우리 매장의 로우포지션 컷 기술이 만족도가 높다는 평을 들었어요.
"남자 셋팅펌 유지력 정말 좋아요!" 라는 후기도 받았습니다.
11월 평일 20% 할인 프로모션이 효과가 있는 것 같습니다.
```

출력:
```json
{
  "usps": ["로우포지션 컷 전문", "평일 대기 짧음"],
  "menu": ["셋팅펌", "남자 컷"],
  "events": [{
    "type": "promotion",
    "title": "11월 평일 20% 할인",
    "period": "2025-11"
  }],
  "customer_quotes": ["남자 셋팅펌 유지력 정말 좋아요!"],
  "sentiment": {
    "overall": "positive",
    "aspects": {
      "품질": "positive"
    }
  },
  "time_refs": ["2025-11-03 14:00-17:00 walk-in 6명"]
}
```

---

### B. DB → 콘텐츠 브리프

**목적**: 정보자산과 키워드로 채널별 콘텐츠 전략 수립

**System Prompt**:
```
당신은 로컬 비즈니스의 마케팅 전략가입니다.
매장의 정보자산(USP, FAQ, 고객 리뷰)과 저경쟁 키워드를 활용하여 
인스타그램과 블로그용 콘텐츠 브리프를 작성합니다.
```

**User Prompt Template**:
```
매장 정보:
- 비즈니스 유형: {business_type}
- 최근 USP 상위 3개: {top_usps}
- 저경쟁 키워드 상위 5개: {low_comp_keywords}
- 이번 주 프로모션: {current_promotion}
- 최근 고객 피드백: {recent_feedback}

위 정보를 바탕으로 다음 채널별 콘텐츠 브리프를 작성하세요:

1. **인스타그램 브리프**:
   - 핵심 메시지 (1-2문장)
   - 타겟 감성/톤
   - 포함할 USP
   - 추천 해시태그 카테고리

2. **블로그 브리프**:
   - 제목 방향 (SEO 키워드 포함)
   - 주요 섹션 구성
   - 내부 링크 기회
   - 메타 설명 방향

JSON 형식으로 출력하세요.
```

**파라미터**:
- `temperature`: 0.8 (크리에이티브)
- `max_tokens`: 2000

---

### C-1. 브리프 → 초안 (인스타그램)

**목적**: 인스타그램 포스트 초안 생성

**System Prompt**:
```
당신은 인스타그램 콘텐츠 크리에이터입니다.
로컬 비즈니스를 위한 매력적이고 자연스러운 인스타그램 포스트를 작성합니다.
```

**User Prompt Template**:
```
브리프:
{brief}

위 브리프를 바탕으로 다음 형식의 인스타그램 포스트를 작성하세요:

{
  "hook": "첫 문장 (눈길을 끄는 후크)",
  "body": "본문 4-6문장 (자연스럽고 진정성 있게)",
  "hashtags": ["해시태그1", ... (12-18개)],
  "first_comment": "첫 댓글 추천"
}

- 이모지는 자연스럽게 2-3개만
- 해시태그는 관련성 높은 것부터
- 브랜드 톤: 친근하고 전문적
```

**파라미터**:
- `temperature`: 0.8
- `max_tokens`: 1500

---

### C-2. 브리프 → 초안 (블로그)

**목적**: SEO 최적화 블로그 포스트 초안 생성

**System Prompt**:
```
당신은 SEO에 능숙한 로컬 비즈니스 블로거입니다.
검색 의도를 충족하면서도 읽기 쉬운 블로그 포스트를 작성합니다.
```

**User Prompt Template**:
```
브리프:
{brief}

위 브리프를 바탕으로 다음 형식의 블로그 포스트를 작성하세요:

{
  "title_options": ["제목 1", "제목 2", "제목 3"],
  "h1": "메인 제목 (키워드 포함)",
  "h2_sections": [{
    "heading": "H2 제목",
    "content": "섹션 내용 (150-200자)"
  }],
  "meta_description": "150자 이내, 키워드 포함",
  "body": "전체 본문 (600-900자)",
  "internal_links": ["[[앵커|URL]]"]
}

- 목표 길이: 600-900자
- 자연스러운 키워드 배치
- 단락은 2-3문장
```

**파라미터**:
- `temperature`: 0.8
- `max_tokens`: 2500

---

### D. 리포트 원인 → 대응

**목적**: KPI 변화 분석 및 실행 가능한 인사이트 도출

**System Prompt**:
```
당신은 데이터 기반 비즈니스 분석가입니다.
KPI 변화를 분석하고 실행 가능한 인사이트를 도출합니다.
```

**User Prompt Template**:
```
기간: {period_start} ~ {period_end}

KPI 변화:
{kpi_changes}

로그 요약:
{log_summary}

콘텐츠 성과:
{content_performance}

위 데이터를 분석하여 다음을 작성하세요:

{
  "causes": [{
    "description": "원인 가설",
    "evidence_links": [{
      "type": "journal|content|log",
      "id": "ID",
      "snippet": "관련 내용"
    }],
    "confidence": 0.0-1.0
  }],
  "actions": [{
    "description": "구체적인 실행 항목",
    "priority": "high|medium|low",
    "related_cause_index": 0
  }]
}

- 원인 3개, 대응 3개 이상
- 구체적이고 실행 가능
- 근거 링크 필수
```

**파라미터**:
- `temperature`: 0.5 (분석)
- `max_tokens`: 2000

---

### E. 키워드 추천

**목적**: 저경쟁 고효율 키워드 추천

**System Prompt**:
```
당신은 로컬 SEO 전문가입니다.
매장의 강점과 시장 기회를 분석하여 저경쟁 키워드를 추천합니다.
```

**User Prompt Template**:
```
매장 정보:
- USP: {usps}
- 최근 일기 토픽: {recent_topics}
- 위치: {location}
- 카테고리: {category}

위 정보를 바탕으로 저경쟁·고효율 키워드 10개를 추천하고,
각 키워드에 대한 간단한 근거를 제시하세요.

{
  "keywords": [{
    "keyword": "키워드",
    "rationale": "추천 이유",
    "competition_score": 0.0-1.0,
    "relevance_score": 0.0-1.0
  }]
}
```

**파라미터**:
- `temperature`: 0.5
- `max_tokens`: 1500

---

### F. USP 추출

**목적**: 매장 고유 강점 발굴

**System Prompt**:
```
당신은 브랜드 전략가입니다.
운영 일기와 고객 피드백에서 매장의 고유한 강점(USP)을 발굴합니다.
```

**User Prompt Template**:
```
데이터:
{data}

위 데이터에서 이 매장만의 고유한 강점 5개를 추출하세요.

{
  "usps": [{
    "title": "USP 제목 (5-10자)",
    "description": "상세 설명 (30-50자)",
    "evidence_count": 언급_횟수,
    "customer_impact": "고객 가치"
  }]
}
```

**파라미터**:
- `temperature`: 0.5
- `max_tokens`: 1500

---

## 파라미터 가이드

### Temperature

- **0.0-0.3**: 일관성 중요 (태깅, 추출)
- **0.4-0.6**: 분석 작업 (리포트, 키워드)
- **0.7-0.9**: 크리에이티브 (브리프, 초안)

### Max Tokens

- **짧은 응답** (태깅): 1000-1500
- **중간 응답** (브리프, 키워드): 1500-2000
- **긴 응답** (블로그, 리포트): 2000-2500

---

## 프롬프트 버전 관리

프롬프트 수정 시:

1. `backend/app/prompts/templates.py` 업데이트
2. 버전 번호 증가
3. 변경 사항을 이 문서에 기록
4. 테스트 후 커밋

**변경 이력**:

- v1.0.0 (2025-11-03): 초기 버전

---

## 테스트

프롬프트 테스트는 `backend/tests/test_prompts.py` 참조

```bash
pytest tests/test_prompts.py -v
```

---

## 베스트 프랙티스

1. **명확한 지시**: "JSON만 출력", "3개 이상" 등 구체적으로
2. **예시 제공**: 입출력 예시로 품질 향상
3. **제약 조건**: 길이, 형식, 톤 등 명시
4. **컨텍스트**: 필요한 배경 정보 충분히 제공
5. **반복 테스트**: 여러 입력으로 일관성 확인

---

**문의**: 프롬프트 개선 제안은 이슈로 등록해 주세요.
