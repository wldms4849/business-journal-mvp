from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Boolean, ARRAY, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.config import Base


class Organization(Base):
    """조직 테이블"""
    __tablename__ = "orgs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="organization")
    channels = relationship("Channel", back_populates="organization")
    journals = relationship("Journal", back_populates="organization")
    assets = relationship("Asset", back_populates="organization")
    credit_wallet = relationship("CreditWallet", back_populates="organization", uselist=False)


class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)  # owner, manager, staff
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    journals = relationship("Journal", back_populates="author")


class Channel(Base):
    """채널 테이블 (인스타그램, 블로그 등)"""
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    type = Column(String, nullable=False)  # instagram, blog
    handle = Column(String)
    status = Column(String, default="active")  # active, inactive
    meta_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="channels")
    posts = relationship("ContentPost", back_populates="channel")


class Journal(Base):
    """사업 일기 테이블"""
    __tablename__ = "journals"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    title = Column(String, nullable=False)
    content_md = Column(Text)
    media_urls = Column(ARRAY(String))
    checklist_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="journals")
    author = relationship("User", back_populates="journals")
    tags = relationship("JournalTag", back_populates="journal")
    assets = relationship("Asset", back_populates="source_journal")


class JournalTag(Base):
    """일기 자동 태깅 테이블"""
    __tablename__ = "journal_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("journals.id"), nullable=False)
    tag_type = Column(String, nullable=False)  # usp, menu, event, quote, sentiment
    tag_value = Column(String, nullable=False)
    score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    journal = relationship("Journal", back_populates="tags")


class Asset(Base):
    """정보자산 테이블"""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    source_journal_id = Column(Integer, ForeignKey("journals.id"))
    asset_type = Column(String, nullable=False)  # usp, faq, before_after, review
    title = Column(String, nullable=False)
    body_json = Column(JSON)
    keywords = Column(ARRAY(String))
    usps = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="assets")
    source_journal = relationship("Journal", back_populates="assets")


class ContentBrief(Base):
    """콘텐츠 브리프 테이블"""
    __tablename__ = "content_briefs"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    derived_from_asset_ids = Column(ARRAY(Integer))
    channel_type = Column(String, nullable=False)  # instagram, blog
    brief_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    drafts = relationship("ContentDraft", back_populates="brief")


class ContentDraft(Base):
    """콘텐츠 초안 테이블"""
    __tablename__ = "content_drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    brief_id = Column(Integer, ForeignKey("content_briefs.id"), nullable=False)
    draft_json = Column(JSON)
    llm_version = Column(String)
    status = Column(String, default="draft")  # draft, reviewed, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brief = relationship("ContentBrief", back_populates="drafts")
    posts = relationship("ContentPost", back_populates="draft")


class ContentPost(Base):
    """콘텐츠 발행 테이블"""
    __tablename__ = "content_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("content_drafts.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    scheduled_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    post_url = Column(String)
    status = Column(String, default="scheduled")  # scheduled, published, failed
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    draft = relationship("ContentDraft", back_populates="posts")
    channel = relationship("Channel", back_populates="posts")


class SetupLog(Base):
    """설정 로그 테이블"""
    __tablename__ = "setup_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    detail_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ExecutionLog(Base):
    """집행 로그 테이블"""
    __tablename__ = "execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    target_type = Column(String)
    target_id = Column(Integer)
    result_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KPISnapshot(Base):
    """KPI 스냅샷 테이블"""
    __tablename__ = "kpi_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    metrics_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    """리포트 테이블"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    period_type = Column(String, nullable=False)  # weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    summary_md = Column(Text)
    causes_json = Column(JSON)
    actions_json = Column(JSON)
    links_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProgressPlan(Base):
    """진척 계획 테이블"""
    __tablename__ = "progress_plan"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    week_start = Column(DateTime(timezone=True), nullable=False)
    targets_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticks = relationship("ProgressTick", back_populates="plan")


class ProgressTick(Base):
    """진척 체크 테이블"""
    __tablename__ = "progress_ticks"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("progress_plan.id"), nullable=False)
    indicator = Column(String, nullable=False)
    value = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    plan = relationship("ProgressPlan", back_populates="ticks")


class DailyRecommendation(Base):
    """일일 추천 테이블 (저경쟁 키워드, 셀링 포인트)"""
    __tablename__ = "daily_recos"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    low_comp_keywords = Column(ARRAY(String))
    todays_usps = Column(ARRAY(String))
    rationale_md = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CreditWallet(Base):
    """크레딧 지갑 테이블"""
    __tablename__ = "credit_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False, unique=True)
    balance = Column(Integer, default=0)
    monthly_cap = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="credit_wallet")
    transactions = relationship("CreditTransaction", back_populates="wallet")


class CreditTransaction(Base):
    """크레딧 거래 테이블"""
    __tablename__ = "credit_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("credit_wallets.id"), nullable=False)
    trigger = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    before = Column(Integer, nullable=False)
    after = Column(Integer, nullable=False)
    meta_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    wallet = relationship("CreditWallet", back_populates="transactions")
    undo_slot = relationship("UndoSlot", back_populates="transaction", uselist=False)


class UndoSlot(Base):
    """되돌리기 슬롯 테이블"""
    __tablename__ = "undo_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    txn_id = Column(Integer, ForeignKey("credit_transactions.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    
    # Relationships
    transaction = relationship("CreditTransaction", back_populates="undo_slot")
