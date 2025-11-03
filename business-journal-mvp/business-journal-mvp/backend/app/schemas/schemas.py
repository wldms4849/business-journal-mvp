from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Organization Schemas
class OrganizationBase(BaseModel):
    name: str


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    role: str = Field(..., pattern="^(owner|manager|staff)$")


class UserCreate(UserBase):
    org_id: int


class User(UserBase):
    id: int
    org_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Journal Schemas
class ChecklistItem(BaseModel):
    id: str
    label: str
    completed: bool
    note: Optional[str] = None


class JournalBase(BaseModel):
    date: datetime
    title: str
    content_md: str
    media_urls: Optional[List[str]] = []
    checklist_json: Optional[List[ChecklistItem]] = []


class JournalCreate(JournalBase):
    org_id: int
    author_id: int


class Journal(JournalBase):
    id: int
    org_id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Tag Schemas
class JournalTagExtraction(BaseModel):
    usps: List[str] = []
    menu: List[str] = []
    events: List[Dict[str, Any]] = []
    customer_quotes: List[str] = []
    sentiment: Dict[str, Any] = {}
    time_refs: List[str] = []


class JournalTagCreate(BaseModel):
    journal_id: int
    tag_type: str
    tag_value: str
    score: Optional[float] = None


class JournalTag(JournalTagCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Asset Schemas
class AssetBase(BaseModel):
    asset_type: str
    title: str
    body_json: Dict[str, Any]
    keywords: Optional[List[str]] = []
    usps: Optional[List[str]] = []


class AssetCreate(AssetBase):
    org_id: int
    source_journal_id: Optional[int] = None


class Asset(AssetBase):
    id: int
    org_id: int
    source_journal_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Content Brief Schemas
class ContentBriefBase(BaseModel):
    channel_type: str
    brief_json: Dict[str, Any]
    derived_from_asset_ids: Optional[List[int]] = []


class ContentBriefCreate(ContentBriefBase):
    org_id: int


class ContentBrief(ContentBriefBase):
    id: int
    org_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Content Draft Schemas
class InstagramDraft(BaseModel):
    hook: str
    body: str
    hashtags: List[str]
    first_comment: str


class BlogDraft(BaseModel):
    title_options: List[str]
    h1: str
    h2_sections: List[Dict[str, str]]
    meta_description: str
    body: str
    internal_links: List[str]


class ContentDraftBase(BaseModel):
    draft_json: Dict[str, Any]
    llm_version: Optional[str] = None
    status: str = "draft"


class ContentDraftCreate(ContentDraftBase):
    brief_id: int


class ContentDraft(ContentDraftBase):
    id: int
    brief_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Content Post Schemas
class ContentPostBase(BaseModel):
    scheduled_at: Optional[datetime] = None
    status: str = "scheduled"


class ContentPostCreate(ContentPostBase):
    draft_id: int
    channel_id: int
    created_by: int


class ContentPost(ContentPostBase):
    id: int
    draft_id: int
    channel_id: int
    published_at: Optional[datetime]
    post_url: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Log Schemas
class SetupLogCreate(BaseModel):
    org_id: int
    actor_id: Optional[int]
    action: str
    detail_json: Dict[str, Any]


class SetupLog(SetupLogCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExecutionLogCreate(BaseModel):
    org_id: int
    actor_id: Optional[int]
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    result_json: Dict[str, Any]


class ExecutionLog(ExecutionLogCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Report Schemas
class ReportCause(BaseModel):
    description: str
    evidence_links: List[Dict[str, Any]]
    confidence: float


class ReportAction(BaseModel):
    description: str
    priority: str
    related_cause_index: Optional[int]


class ReportCreate(BaseModel):
    org_id: int
    period_type: str
    period_start: datetime
    period_end: datetime
    summary_md: str
    causes_json: List[ReportCause]
    actions_json: List[ReportAction]
    links_json: Dict[str, Any]


class Report(ReportCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Progress Schemas
class ProgressTarget(BaseModel):
    indicator: str
    target_value: float
    unit: str


class ProgressPlanCreate(BaseModel):
    org_id: int
    week_start: datetime
    targets_json: List[ProgressTarget]


class ProgressPlan(ProgressPlanCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProgressTickCreate(BaseModel):
    plan_id: int
    indicator: str
    value: float


class ProgressTick(ProgressTickCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProgressGauge(BaseModel):
    percentage: float
    completed: int
    total: int
    incomplete_reasons: List[Dict[str, str]]


# Daily Recommendation Schemas
class DailyRecommendationCreate(BaseModel):
    org_id: int
    date: datetime
    low_comp_keywords: List[str]
    todays_usps: List[str]
    rationale_md: str


class DailyRecommendation(DailyRecommendationCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Credit Schemas
class CreditWalletCreate(BaseModel):
    org_id: int
    balance: int = 0
    monthly_cap: Optional[int] = None


class CreditWallet(CreditWalletCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreditTransactionCreate(BaseModel):
    wallet_id: int
    trigger: str
    amount: int
    before: int
    after: int
    meta_json: Optional[Dict[str, Any]] = {}


class CreditTransaction(CreditTransactionCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreditConsumeRequest(BaseModel):
    org_id: int
    trigger: str
    amount: int
    meta: Optional[Dict[str, Any]] = {}


class CreditConsumeResponse(BaseModel):
    success: bool
    transaction_id: Optional[int]
    new_balance: int
    can_undo: bool
    undo_expires_at: Optional[datetime]
    message: str


class CreditUndoRequest(BaseModel):
    org_id: int
    transaction_id: int


class CreditUndoResponse(BaseModel):
    success: bool
    restored_balance: int
    message: str


# Dashboard Schemas
class DashboardSummary(BaseModel):
    week_progress: ProgressGauge
    todays_usps: List[str]
    low_comp_keywords: List[str]
    recent_logs: List[Dict[str, Any]]
    credit_balance: int
