from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from app.core.config import get_db
from app.models.models import (
    DailyRecommendation, ProgressPlan, ProgressTick,
    ExecutionLog, SetupLog, CreditWallet, Asset, Journal
)
from app.schemas.schemas import (
    DashboardSummary, ProgressGauge,
    DailyRecommendation as DailyRecoSchema,
)
from app.services.llm_service import llm_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    org_id: int,
    db: Session = Depends(get_db)
):
    """대시보드 요약 정보"""
    try:
        # 이번 주 진척 게이지 계산
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        progress_plan = db.query(ProgressPlan).filter(
            ProgressPlan.org_id == org_id,
            ProgressPlan.week_start == week_start.date()
        ).first()
        
        if progress_plan:
            ticks = db.query(ProgressTick).filter(
                ProgressTick.plan_id == progress_plan.id
            ).all()
            
            targets = progress_plan.targets_json or []
            completed = len([t for t in ticks if t.value >= 1.0])
            total = len(targets)
            percentage = (completed / total * 100) if total > 0 else 0
            
            week_progress = ProgressGauge(
                percentage=round(percentage, 1),
                completed=completed,
                total=total,
                incomplete_reasons=[]
            )
        else:
            week_progress = ProgressGauge(
                percentage=0,
                completed=0,
                total=0,
                incomplete_reasons=[]
            )
        
        # 오늘의 추천 조회
        today = datetime.now().date()
        daily_reco = db.query(DailyRecommendation).filter(
            DailyRecommendation.org_id == org_id,
            func.date(DailyRecommendation.date) == today
        ).first()
        
        todays_usps = daily_reco.todays_usps if daily_reco else []
        low_comp_keywords = daily_reco.low_comp_keywords if daily_reco else []
        
        # 최근 로그 (최근 10개)
        recent_logs = db.query(ExecutionLog).filter(
            ExecutionLog.org_id == org_id
        ).order_by(ExecutionLog.created_at.desc()).limit(10).all()
        
        log_items = [
            {
                "id": log.id,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "created_at": log.created_at.isoformat()
            }
            for log in recent_logs
        ]
        
        # 크레딧 잔액
        wallet = db.query(CreditWallet).filter(
            CreditWallet.org_id == org_id
        ).first()
        credit_balance = wallet.balance if wallet else 0
        
        return DashboardSummary(
            week_progress=week_progress,
            todays_usps=todays_usps,
            low_comp_keywords=low_comp_keywords,
            recent_logs=log_items,
            credit_balance=credit_balance
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대시보드 조회 실패: {str(e)}"
        )


@router.get("/recos", response_model=DailyRecoSchema)
async def get_daily_recommendations(
    org_id: int,
    date: str = None,
    db: Session = Depends(get_db)
):
    """일일 추천 조회 (저경쟁 키워드, 셀링 포인트)"""
    if not date:
        date = datetime.now().date()
    else:
        date = datetime.fromisoformat(date).date()
    
    # 기존 추천 확인
    reco = db.query(DailyRecommendation).filter(
        DailyRecommendation.org_id == org_id,
        func.date(DailyRecommendation.date) == date
    ).first()
    
    if reco:
        return reco
    
    # 추천 생성
    try:
        # USP 조회
        usps = db.query(Asset).filter(
            Asset.org_id == org_id,
            Asset.asset_type == "usp"
        ).order_by(Asset.created_at.desc()).limit(10).all()
        
        usp_list = [asset.title for asset in usps]
        
        # 최근 일기 토픽
        journals = db.query(Journal).filter(
            Journal.org_id == org_id
        ).order_by(Journal.date.desc()).limit(5).all()
        
        recent_topics = [journal.title for journal in journals]
        
        # LLM으로 키워드 추천
        keywords = await llm_service.recommend_keywords(
            usps=usp_list,
            recent_topics=recent_topics,
            location="서울",  # 추후 org 정보에서 가져오기
            category="카페"  # 추후 org 정보에서 가져오기
        )
        
        low_comp_keywords = [k["keyword"] for k in keywords[:5]]
        todays_usps = usp_list[:3]
        
        # 추천 저장
        new_reco = DailyRecommendation(
            org_id=org_id,
            date=datetime.combine(date, datetime.min.time()),
            low_comp_keywords=low_comp_keywords,
            todays_usps=todays_usps,
            rationale_md="LLM 기반 자동 생성"
        )
        db.add(new_reco)
        db.commit()
        db.refresh(new_reco)
        
        return new_reco
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"추천 생성 실패: {str(e)}"
        )


@router.post("/progress/plan")
async def create_progress_plan(
    org_id: int,
    week_start: str,
    targets: List[dict],
    db: Session = Depends(get_db)
):
    """주간 진척 계획 생성"""
    try:
        week_start_date = datetime.fromisoformat(week_start)
        
        plan = ProgressPlan(
            org_id=org_id,
            week_start=week_start_date,
            targets_json=targets
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        return {"message": "계획이 생성되었습니다", "plan_id": plan.id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계획 생성 실패: {str(e)}"
        )


@router.post("/progress/tick")
async def record_progress_tick(
    plan_id: int,
    indicator: str,
    value: float,
    db: Session = Depends(get_db)
):
    """진척 체크 기록"""
    try:
        tick = ProgressTick(
            plan_id=plan_id,
            indicator=indicator,
            value=value
        )
        db.add(tick)
        db.commit()
        
        return {"message": "진척이 기록되었습니다"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"진척 기록 실패: {str(e)}"
        )


@router.get("/logs/execution")
async def get_execution_logs(
    org_id: int,
    action: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """집행 로그 조회"""
    query = db.query(ExecutionLog).filter(ExecutionLog.org_id == org_id)
    
    if action:
        query = query.filter(ExecutionLog.action == action)
    
    logs = query.order_by(ExecutionLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "actor_id": log.actor_id,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "result": log.result_json,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]


@router.get("/logs/setup")
async def get_setup_logs(
    org_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """설정 로그 조회"""
    logs = db.query(SetupLog).filter(
        SetupLog.org_id == org_id
    ).order_by(SetupLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "actor_id": log.actor_id,
            "action": log.action,
            "detail": log.detail_json,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]
