import json
import openai
from typing import Dict, Any, List, Optional
from app.core.config import get_settings
from app.prompts.templates import (
    JOURNAL_TAGGING_SYSTEM, JOURNAL_TAGGING_USER,
    CONTENT_BRIEF_SYSTEM, CONTENT_BRIEF_USER,
    INSTAGRAM_DRAFT_SYSTEM, INSTAGRAM_DRAFT_USER,
    BLOG_DRAFT_SYSTEM, BLOG_DRAFT_USER,
    REPORT_ANALYSIS_SYSTEM, REPORT_ANALYSIS_USER,
    KEYWORD_RECOMMENDATION_SYSTEM, KEYWORD_RECOMMENDATION_USER,
    USP_EXTRACTION_SYSTEM, USP_EXTRACTION_USER,
    TAGGING_PARAMS, CREATIVE_PARAMS, ANALYSIS_PARAMS
)

settings = get_settings()


class LLMService:
    """LLM 서비스 추상화 레이어"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.timeout = settings.OPENAI_TIMEOUT
    
    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        params: Dict[str, Any]
    ) -> str:
        """LLM API 호출 wrapper"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **params,
                timeout=self.timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM API 호출 실패: {str(e)}")
    
    async def extract_journal_tags(self, journal_content: str) -> Dict[str, Any]:
        """일기에서 태그 추출"""
        user_prompt = JOURNAL_TAGGING_USER.format(journal_content=journal_content)
        response = await self._call_llm(
            JOURNAL_TAGGING_SYSTEM,
            user_prompt,
            TAGGING_PARAMS
        )
        
        try:
            # JSON 파싱
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 재시도 또는 빈 결과 반환
            return {
                "usps": [],
                "menu": [],
                "events": [],
                "customer_quotes": [],
                "sentiment": {},
                "time_refs": []
            }
    
    async def generate_content_brief(
        self,
        business_type: str,
        top_usps: List[str],
        low_comp_keywords: List[str],
        current_promotion: Optional[str] = None,
        recent_feedback: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """콘텐츠 브리프 생성"""
        user_prompt = CONTENT_BRIEF_USER.format(
            business_type=business_type,
            top_usps=", ".join(top_usps),
            low_comp_keywords=", ".join(low_comp_keywords),
            current_promotion=current_promotion or "없음",
            recent_feedback=", ".join(recent_feedback) if recent_feedback else "없음"
        )
        
        response = await self._call_llm(
            CONTENT_BRIEF_SYSTEM,
            user_prompt,
            CREATIVE_PARAMS
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "브리프 생성 실패"}
    
    async def generate_instagram_draft(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """인스타그램 초안 생성"""
        user_prompt = INSTAGRAM_DRAFT_USER.format(brief=json.dumps(brief, ensure_ascii=False))
        
        response = await self._call_llm(
            INSTAGRAM_DRAFT_SYSTEM,
            user_prompt,
            CREATIVE_PARAMS
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "초안 생성 실패"}
    
    async def generate_blog_draft(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """블로그 초안 생성"""
        user_prompt = BLOG_DRAFT_USER.format(brief=json.dumps(brief, ensure_ascii=False))
        
        response = await self._call_llm(
            BLOG_DRAFT_SYSTEM,
            user_prompt,
            CREATIVE_PARAMS
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "초안 생성 실패"}
    
    async def analyze_report(
        self,
        period_start: str,
        period_end: str,
        kpi_changes: Dict[str, Any],
        log_summary: str,
        content_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """리포트 원인 분석 및 대응 제안"""
        user_prompt = REPORT_ANALYSIS_USER.format(
            period_start=period_start,
            period_end=period_end,
            kpi_changes=json.dumps(kpi_changes, ensure_ascii=False),
            log_summary=log_summary,
            content_performance=json.dumps(content_performance, ensure_ascii=False)
        )
        
        response = await self._call_llm(
            REPORT_ANALYSIS_SYSTEM,
            user_prompt,
            ANALYSIS_PARAMS
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"causes": [], "actions": []}
    
    async def recommend_keywords(
        self,
        usps: List[str],
        recent_topics: List[str],
        location: str,
        category: str
    ) -> List[Dict[str, Any]]:
        """저경쟁 키워드 추천"""
        user_prompt = KEYWORD_RECOMMENDATION_USER.format(
            usps=", ".join(usps),
            recent_topics=", ".join(recent_topics),
            location=location,
            category=category
        )
        
        response = await self._call_llm(
            KEYWORD_RECOMMENDATION_SYSTEM,
            user_prompt,
            ANALYSIS_PARAMS
        )
        
        try:
            result = json.loads(response)
            return result.get("keywords", [])
        except json.JSONDecodeError:
            return []
    
    async def extract_usps(self, data: str) -> List[Dict[str, Any]]:
        """USP 추출"""
        user_prompt = USP_EXTRACTION_USER.format(data=data)
        
        response = await self._call_llm(
            USP_EXTRACTION_SYSTEM,
            user_prompt,
            ANALYSIS_PARAMS
        )
        
        try:
            result = json.loads(response)
            return result.get("usps", [])
        except json.JSONDecodeError:
            return []


# 싱글톤 인스턴스
llm_service = LLMService()
