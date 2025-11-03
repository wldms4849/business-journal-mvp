from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.config import get_db
from app.models.models import (
    ContentBrief, ContentDraft, ContentPost,
    Asset, ExecutionLog, Channel
)
from app.schemas.schemas import (
    ContentBrief as ContentBriefSchema,
    ContentBriefCreate,
    ContentDraft as ContentDraftSchema,
    ContentDraftCreate,
    ContentPost as ContentPostSchema,
    ContentPostCreate,
)
from app.services.llm_service import llm_service

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/briefs", response_model=ContentBriefSchema, status_code=status.HTTP_201_CREATED)
async def create_brief(
    brief_data: ContentBriefCreate,
    db: Session = Depends(get_db)
):
    """콘텐츠 브리프 생성"""
    try:
        db_brief = ContentBrief(**brief_data.dict())
        db.add(db_brief)
        db.commit()
        db.refresh(db_brief)
        
        return db_brief
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"브리프 생성 실패: {str(e)}"
        )


@router.post("/briefs/generate", response_model=ContentBriefSchema)
async def generate_brief(
    org_id: int,
    channel_type: str,
    business_type: str = "cafe",
    db: Session = Depends(get_db)
):
    """AI 기반 콘텐츠 브리프 자동 생성"""
    try:
        # USP 조회 (최근 3개)
        usps = db.query(Asset).filter(
            Asset.org_id == org_id,
            Asset.asset_type == "usp"
        ).order_by(Asset.created_at.desc()).limit(3).all()
        
        top_usps = [asset.title for asset in usps]
        
        # 저경쟁 키워드 (임시: 하드코딩, 추후 키워드 서비스 연동)
        low_comp_keywords = ["동네 카페", "조용한 카페", "브런치 맛집"]
        
        # LLM으로 브리프 생성
        brief_content = await llm_service.generate_content_brief(
            business_type=business_type,
            top_usps=top_usps,
            low_comp_keywords=low_comp_keywords,
            current_promotion=None,
            recent_feedback=None
        )
        
        # 브리프 저장
        db_brief = ContentBrief(
            org_id=org_id,
            channel_type=channel_type,
            brief_json=brief_content,
            derived_from_asset_ids=[asset.id for asset in usps]
        )
        db.add(db_brief)
        db.commit()
        db.refresh(db_brief)
        
        return db_brief
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"브리프 생성 실패: {str(e)}"
        )


@router.post("/drafts", response_model=ContentDraftSchema, status_code=status.HTTP_201_CREATED)
async def create_draft_from_brief(
    brief_id: int,
    db: Session = Depends(get_db)
):
    """브리프로부터 초안 생성"""
    # 브리프 조회
    brief = db.query(ContentBrief).filter(ContentBrief.id == brief_id).first()
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="브리프를 찾을 수 없습니다"
        )
    
    try:
        # 채널 타입에 따라 다른 초안 생성
        if brief.channel_type == "instagram":
            draft_content = await llm_service.generate_instagram_draft(brief.brief_json)
        elif brief.channel_type == "blog":
            draft_content = await llm_service.generate_blog_draft(brief.brief_json)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원하지 않는 채널 타입입니다"
            )
        
        # 초안 저장
        db_draft = ContentDraft(
            brief_id=brief_id,
            draft_json=draft_content,
            llm_version="gpt-4",
            status="draft"
        )
        db.add(db_draft)
        db.commit()
        db.refresh(db_draft)
        
        # 실행 로그
        log = ExecutionLog(
            org_id=brief.org_id,
            actor_id=None,  # 시스템 생성
            action="draft_generated",
            target_type="draft",
            target_id=db_draft.id,
            result_json={"brief_id": brief_id, "channel": brief.channel_type}
        )
        db.add(log)
        db.commit()
        
        return db_draft
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"초안 생성 실패: {str(e)}"
        )


@router.get("/drafts", response_model=List[ContentDraftSchema])
async def list_drafts(
    org_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """초안 목록 조회"""
    query = db.query(ContentDraft).join(ContentBrief).filter(
        ContentBrief.org_id == org_id
    )
    
    if status:
        query = query.filter(ContentDraft.status == status)
    
    drafts = query.order_by(ContentDraft.created_at.desc()).offset(skip).limit(limit).all()
    return drafts


@router.put("/drafts/{draft_id}/status")
async def update_draft_status(
    draft_id: int,
    new_status: str,
    user_id: int,
    db: Session = Depends(get_db)
):
    """초안 상태 업데이트 (검수 등)"""
    draft = db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="초안을 찾을 수 없습니다"
        )
    
    draft.status = new_status
    db.commit()
    
    # 실행 로그
    brief = db.query(ContentBrief).filter(ContentBrief.id == draft.brief_id).first()
    log = ExecutionLog(
        org_id=brief.org_id if brief else None,
        actor_id=user_id,
        action="draft_status_updated",
        target_type="draft",
        target_id=draft_id,
        result_json={"new_status": new_status}
    )
    db.add(log)
    db.commit()
    
    return {"message": "상태가 업데이트되었습니다", "status": new_status}


@router.post("/posts/schedule", response_model=ContentPostSchema)
async def schedule_post(
    post_data: ContentPostCreate,
    db: Session = Depends(get_db)
):
    """콘텐츠 예약 발행"""
    # 초안 확인
    draft = db.query(ContentDraft).filter(ContentDraft.id == post_data.draft_id).first()
    if not draft or draft.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="승인된 초안만 예약할 수 있습니다"
        )
    
    try:
        db_post = ContentPost(**post_data.dict())
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        # 실행 로그
        brief = db.query(ContentBrief).filter(ContentBrief.id == draft.brief_id).first()
        log = ExecutionLog(
            org_id=brief.org_id if brief else None,
            actor_id=post_data.created_by,
            action="post_scheduled",
            target_type="post",
            target_id=db_post.id,
            result_json={
                "scheduled_at": post_data.scheduled_at.isoformat() if post_data.scheduled_at else None
            }
        )
        db.add(log)
        db.commit()
        
        return db_post
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예약 실패: {str(e)}"
        )


@router.get("/posts", response_model=List[ContentPostSchema])
async def list_posts(
    org_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """발행 목록 조회"""
    query = db.query(ContentPost).join(ContentDraft).join(ContentBrief).filter(
        ContentBrief.org_id == org_id
    )
    
    if status:
        query = query.filter(ContentPost.status == status)
    
    posts = query.order_by(ContentPost.created_at.desc()).offset(skip).limit(limit).all()
    return posts
