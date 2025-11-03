"""
LLM 프롬프트 템플릿
버전: 1.0.0
"""

# A. 일기 → 태깅
JOURNAL_TAGGING_SYSTEM = """당신은 로컬 비즈니스 운영 일기를 분석하여 구조화된 정보를 추출하는 전문가입니다.
다음 운영 일기에서 USP(고유 셀링 포인트), 메뉴/서비스, 행사/프로모션, 고객 코멘트, 감성, 시간·날짜 참조를 JSON으로 추출하세요."""

JOURNAL_TAGGING_USER = """운영 일기:
{journal_content}

위 일기를 분석하여 다음 JSON 스키마에 맞춰 정보를 추출하세요:

{{
  "usps": ["고유 셀링 포인트 1", "고유 셀링 포인트 2", ...],
  "menu": ["메뉴/서비스 항목 1", "메뉴/서비스 항목 2", ...],
  "events": [
    {{
      "type": "promotion|launch|special_hours|other",
      "title": "이벤트 제목",
      "period": "기간 (예: 2025-11-05~2025-11-30)"
    }}
  ],
  "customer_quotes": ["고객 말 인용 1", "고객 말 인용 2", ...],
  "sentiment": {{
    "overall": "positive|neutral|negative",
    "aspects": {{
      "가격": "positive|neutral|negative",
      "품질": "positive|neutral|negative",
      "서비스": "positive|neutral|negative"
    }}
  }},
  "time_refs": ["시간 참조 1 (예: 2025-11-03 14:00 walk-in 6건)", ...]
}}

JSON만 출력하세요. 추가 설명은 불필요합니다."""

# B. DB → 콘텐츠 브리프
CONTENT_BRIEF_SYSTEM = """당신은 로컬 비즈니스의 마케팅 전략가입니다.
매장의 정보자산(USP, FAQ, 고객 리뷰)과 저경쟁 키워드를 활용하여 인스타그램과 블로그용 콘텐츠 브리프를 작성합니다."""

CONTENT_BRIEF_USER = """매장 정보:
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

JSON 형식으로 출력하세요."""

# C. 브리프 → 초안 (인스타그램)
INSTAGRAM_DRAFT_SYSTEM = """당신은 인스타그램 콘텐츠 크리에이터입니다.
로컬 비즈니스를 위한 매력적이고 자연스러운 인스타그램 포스트를 작성합니다."""

INSTAGRAM_DRAFT_USER = """브리프:
{brief}

위 브리프를 바탕으로 다음 형식의 인스타그램 포스트를 작성하세요:

{{
  "hook": "첫 문장 (눈길을 끄는 후크)",
  "body": "본문 4-6문장 (자연스럽고 진정성 있게)",
  "hashtags": ["해시태그1", "해시태그2", ... (12-18개)],
  "first_comment": "첫 댓글 추천 (추가 정보나 CTA)"
}}

- 이모지는 자연스럽게 2-3개만 사용
- 해시태그는 관련성 높은 것부터 배치
- 브랜드 톤: 친근하고 전문적
- JSON만 출력"""

# C-2. 브리프 → 초안 (블로그)
BLOG_DRAFT_SYSTEM = """당신은 SEO에 능숙한 로컬 비즈니스 블로거입니다.
검색 의도를 충족하면서도 읽기 쉬운 블로그 포스트를 작성합니다."""

BLOG_DRAFT_USER = """브리프:
{brief}

위 브리프를 바탕으로 다음 형식의 블로그 포스트를 작성하세요:

{{
  "title_options": ["제목 옵션 1", "제목 옵션 2", "제목 옵션 3"],
  "h1": "메인 제목 (키워드 포함)",
  "h2_sections": [
    {{
      "heading": "H2 제목 1",
      "content": "섹션 내용 (150-200자)"
    }}
  ],
  "meta_description": "메타 설명 (150자 이내, 키워드 포함)",
  "body": "전체 본문 (600-900자)",
  "internal_links": ["[[링크_앵커_텍스트|링크_URL]]"]
}}

- 목표 길이: 600-900자
- 자연스러운 키워드 배치
- 단락은 2-3문장으로 짧게
- JSON만 출력"""

# D. 리포트 원인 → 대응
REPORT_ANALYSIS_SYSTEM = """당신은 데이터 기반 비즈니스 분석가입니다.
KPI 변화를 분석하고 실행 가능한 인사이트를 도출합니다."""

REPORT_ANALYSIS_USER = """기간: {period_start} ~ {period_end}

KPI 변화:
{kpi_changes}

로그 요약:
{log_summary}

콘텐츠 성과:
{content_performance}

위 데이터를 분석하여 다음을 작성하세요:

{{
  "causes": [
    {{
      "description": "원인 가설 설명",
      "evidence_links": [
        {{
          "type": "journal|content|log",
          "id": "ID",
          "snippet": "관련 내용 일부"
        }}
      ],
      "confidence": 0.0-1.0
    }}
  ],
  "actions": [
    {{
      "description": "구체적인 실행 항목",
      "priority": "high|medium|low",
      "related_cause_index": 0
    }}
  ]
}}

- 원인 3개, 대응 3개 이상
- 각 항목은 구체적이고 실행 가능해야 함
- 근거 링크 필수
- JSON만 출력"""

# E. 키워드 추천
KEYWORD_RECOMMENDATION_SYSTEM = """당신은 로컬 SEO 전문가입니다.
매장의 강점과 시장 기회를 분석하여 저경쟁 키워드를 추천합니다."""

KEYWORD_RECOMMENDATION_USER = """매장 정보:
- USP: {usps}
- 최근 일기 토픽: {recent_topics}
- 위치: {location}
- 카테고리: {category}

위 정보를 바탕으로 저경쟁·고효율 키워드 10개를 추천하고,
각 키워드에 대한 간단한 근거를 제시하세요.

{{
  "keywords": [
    {{
      "keyword": "키워드",
      "rationale": "추천 이유 (1-2문장)",
      "competition_score": 0.0-1.0,
      "relevance_score": 0.0-1.0
    }}
  ]
}}

JSON만 출력"""

# F. USP 추출
USP_EXTRACTION_SYSTEM = """당신은 브랜드 전략가입니다.
운영 일기와 고객 피드백에서 매장의 고유한 강점(USP)을 발굴합니다."""

USP_EXTRACTION_USER = """데이터:
{data}

위 데이터에서 이 매장만의 고유한 강점 5개를 추출하세요.
각 USP는:
- 구체적이고 차별화된 내용
- 고객 관점에서 가치가 명확
- 반복 언급되거나 강조된 요소

{{
  "usps": [
    {{
      "title": "USP 제목 (5-10자)",
      "description": "상세 설명 (30-50자)",
      "evidence_count": 언급_횟수,
      "customer_impact": "고객에게 주는 가치"
    }}
  ]
}}

JSON만 출력"""


# 프롬프트 파라미터 기본값
DEFAULT_PARAMS = {
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}

# 특정 작업별 파라미터 오버라이드
TAGGING_PARAMS = {
    **DEFAULT_PARAMS,
    "temperature": 0.3,  # 더 일관된 추출을 위해 낮춤
}

CREATIVE_PARAMS = {
    **DEFAULT_PARAMS,
    "temperature": 0.8,  # 크리에이티브한 작업을 위해 높임
}

ANALYSIS_PARAMS = {
    **DEFAULT_PARAMS,
    "temperature": 0.5,  # 분석 작업을 위해 중간값
}
