from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.config import get_db
from app.models.models import Journal, JournalTag, Asset, ExecutionLog
from app.schemas.schemas import (
    Journal as JournalSchema,
    JournalCreate,
    JournalTag as JournalTagSchema,
    JournalTagExtraction,
)
from app.services.llm_service import llm_service

router = APIRouter(prefix="/journals", tags=["journals"])


@router.post("/", response_model=JournalSchema, status_code=status.HTTP_201_CREATED)
async def create_journal(
    journal: JournalCreate,
    db: Session = Depends(get_db)
):
    """사업 일기 생성"""
    try:
        # 일기 생성
        db_journal = Journal(**journal.dict())
        db.add(db_journal)
        db.commit()
        db.refresh(db_journal)
        
        # 실행 로그 기록
        log = ExecutionLog(
            org_id=journal.org_id,
            actor_id=journal.author_id,
            action="journal_created",
            target_type="journal",
            target_id=db_journal.id,
            result_json={"title": journal.title}
        )
        db.add(log)
        db.commit()
        
        return db_journal
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일기 생성 실패: {str(e)}"
        )


@router.get("/", response_model=List[JournalSchema])
async def list_journals(
    org_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """일기 목록 조회"""
    journals = db.query(Journal).filter(
        Journal.org_id == org_id
    ).order_by(
        Journal.date.desc()
    ).offset(skip).limit(limit).all()
    
    return journals


@router.get("/{journal_id}", response_model=JournalSchema)
async def get_journal(journal_id: int, db: Session = Depends(get_db)):
    """일기 상세 조회"""
    journal = db.query(Journal).filter(Journal.id == journal_id).first()
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일기를 찾을 수 없습니다"
        )
    return journal


@router.post("/{journal_id}/extract", response_model=JournalTagExtraction)
async def extract_tags(
    journal_id: int,
    db: Session = Depends(get_db)
):
    """일기에서 태그 자동 추출"""
    # 일기 조회
    journal = db.query(Journal).filter(Journal.id == journal_id).first()
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일기를 찾을 수 없습니다"
        )
    
    try:
        # LLM으로 태그 추출
        extraction = await llm_service.extract_journal_tags(journal.content_md)
        
        # 태그 저장
        for usp in extraction.get("usps", []):
            tag = JournalTag(
                journal_id=journal_id,
                tag_type="usp",
                tag_value=usp,
                score=1.0
            )
            db.add(tag)
        
        for menu_item in extraction.get("menu", []):
            tag = JournalTag(
                journal_id=journal_id,
                tag_type="menu",
                tag_value=menu_item,
                score=1.0
            )
            db.add(tag)
        
        for event in extraction.get("events", []):
            tag = JournalTag(
                journal_id=journal_id,
                tag_type="event",
                tag_value=event.get("title", ""),
                score=1.0
            )
            db.add(tag)
        
        for quote in extraction.get("customer_quotes", []):
            tag = JournalTag(
                journal_id=journal_id,
                tag_type="quote",
                tag_value=quote,
                score=1.0
            )
            db.add(tag)
        
        # USP를 Asset으로 저장
        for usp in extraction.get("usps", []):
            asset = Asset(
                org_id=journal.org_id,
                source_journal_id=journal_id,
                asset_type="usp",
                title=usp,
                body_json={"description": usp, "extracted_from": "journal"},
                keywords=[],
                usps=[usp]
            )
            db.add(asset)
        
        db.commit()
        
        # 실행 로그 기록
        log = ExecutionLog(
            org_id=journal.org_id,
            actor_id=journal.author_id,
            action="tags_extracted",
            target_type="journal",
            target_id=journal_id,
            result_json={
                "usp_count": len(extraction.get("usps", [])),
                "menu_count": len(extraction.get("menu", [])),
                "event_count": len(extraction.get("events", []))
            }
        )
        db.add(log)
        db.commit()
        
        return extraction
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"태그 추출 실패: {str(e)}"
        )


@router.get("/{journal_id}/tags", response_model=List[JournalTagSchema])
async def get_journal_tags(journal_id: int, db: Session = Depends(get_db)):
    """일기의 태그 조회"""
    tags = db.query(JournalTag).filter(
        JournalTag.journal_id == journal_id
    ).all()
    return tags
