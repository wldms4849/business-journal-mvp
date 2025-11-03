from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.config import get_db, get_settings
from app.models.models import CreditWallet, CreditTransaction, UndoSlot, ExecutionLog
from app.schemas.schemas import (
    CreditWallet as CreditWalletSchema,
    CreditConsumeRequest, CreditConsumeResponse,
    CreditUndoRequest, CreditUndoResponse
)

router = APIRouter(prefix="/credits", tags=["credits"])
settings = get_settings()


@router.get("/wallet", response_model=CreditWalletSchema)
async def get_wallet(org_id: int, db: Session = Depends(get_db)):
    """크레딧 지갑 조회"""
    wallet = db.query(CreditWallet).filter(CreditWallet.org_id == org_id).first()
    
    if not wallet:
        # 지갑이 없으면 생성
        wallet = CreditWallet(
            org_id=org_id,
            balance=settings.DEFAULT_FREE_CREDITS,
            monthly_cap=settings.MONTHLY_FREE_CREDITS
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    return wallet


@router.post("/consume", response_model=CreditConsumeResponse)
async def consume_credits(
    request: CreditConsumeRequest,
    db: Session = Depends(get_db)
):
    """크레딧 소모"""
    # 지갑 조회
    wallet = db.query(CreditWallet).filter(CreditWallet.org_id == request.org_id).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="크레딧 지갑을 찾을 수 없습니다"
        )
    
    # 잔액 확인
    if wallet.balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"크레딧이 부족합니다 (현재: {wallet.balance}, 필요: {request.amount})"
        )
    
    try:
        # 거래 생성
        before = wallet.balance
        after = before - request.amount
        
        transaction = CreditTransaction(
            wallet_id=wallet.id,
            trigger=request.trigger,
            amount=-request.amount,
            before=before,
            after=after,
            meta_json=request.meta
        )
        db.add(transaction)
        
        # 지갑 업데이트
        wallet.balance = after
        
        db.commit()
        db.refresh(transaction)
        
        # 되돌리기 슬롯 생성 (24시간 유효)
        undo_slot = UndoSlot(
            org_id=request.org_id,
            txn_id=transaction.id,
            expires_at=datetime.now() + timedelta(hours=24),
            used=False
        )
        db.add(undo_slot)
        db.commit()
        
        # 실행 로그
        log = ExecutionLog(
            org_id=request.org_id,
            actor_id=None,
            action="credit_consumed",
            target_type="credit_transaction",
            target_id=transaction.id,
            result_json={
                "trigger": request.trigger,
                "amount": request.amount,
                "new_balance": after
            }
        )
        db.add(log)
        db.commit()
        
        return CreditConsumeResponse(
            success=True,
            transaction_id=transaction.id,
            new_balance=after,
            can_undo=True,
            undo_expires_at=undo_slot.expires_at,
            message=f"{request.amount} 크레딧이 소모되었습니다"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"크레딧 소모 실패: {str(e)}"
        )


@router.post("/undo", response_model=CreditUndoResponse)
async def undo_credit_consumption(
    request: CreditUndoRequest,
    db: Session = Depends(get_db)
):
    """크레딧 소모 되돌리기"""
    # 되돌리기 슬롯 확인
    undo_slot = db.query(UndoSlot).filter(
        UndoSlot.org_id == request.org_id,
        UndoSlot.txn_id == request.transaction_id,
        UndoSlot.used == False,
        UndoSlot.expires_at > datetime.now()
    ).first()
    
    if not undo_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="되돌리기 슬롯이 만료되었거나 이미 사용되었습니다"
        )
    
    # 원래 거래 조회
    transaction = db.query(CreditTransaction).filter(
        CreditTransaction.id == request.transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="거래를 찾을 수 없습니다"
        )
    
    try:
        # 지갑 조회
        wallet = db.query(CreditWallet).filter(
            CreditWallet.id == transaction.wallet_id
        ).first()
        
        # 크레딧 복구
        restore_amount = abs(transaction.amount)
        wallet.balance += restore_amount
        
        # 역거래 생성
        reverse_transaction = CreditTransaction(
            wallet_id=wallet.id,
            trigger=f"undo_{transaction.trigger}",
            amount=restore_amount,
            before=transaction.after,
            after=wallet.balance,
            meta_json={"original_txn_id": transaction.id}
        )
        db.add(reverse_transaction)
        
        # 슬롯 사용 처리
        undo_slot.used = True
        
        db.commit()
        
        # 실행 로그
        log = ExecutionLog(
            org_id=request.org_id,
            actor_id=None,
            action="credit_undone",
            target_type="credit_transaction",
            target_id=reverse_transaction.id,
            result_json={
                "original_txn_id": transaction.id,
                "restored_amount": restore_amount,
                "new_balance": wallet.balance
            }
        )
        db.add(log)
        db.commit()
        
        return CreditUndoResponse(
            success=True,
            restored_balance=wallet.balance,
            message=f"{restore_amount} 크레딧이 복구되었습니다"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"되돌리기 실패: {str(e)}"
        )


@router.get("/transactions")
async def get_transactions(
    org_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """크레딧 거래 내역 조회"""
    wallet = db.query(CreditWallet).filter(CreditWallet.org_id == org_id).first()
    
    if not wallet:
        return []
    
    transactions = db.query(CreditTransaction).filter(
        CreditTransaction.wallet_id == wallet.id
    ).order_by(CreditTransaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": txn.id,
            "trigger": txn.trigger,
            "amount": txn.amount,
            "before": txn.before,
            "after": txn.after,
            "meta": txn.meta_json,
            "created_at": txn.created_at.isoformat()
        }
        for txn in transactions
    ]
