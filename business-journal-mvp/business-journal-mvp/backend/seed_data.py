"""
시드 데이터 생성 스크립트
데모용 카페/미용실 2개 매장, 14일치 일기, 콘텐츠, 리포트 생성
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from app.core.config import SessionLocal
from app.models.models import *

def create_seed_data():
    db = SessionLocal()
    
    try:
        print("🌱 시드 데이터 생성 시작...")
        
        # 1. 조직 생성
        print("1️⃣  조직 생성 중...")
        cafe = Organization(name="동네 카페")
        salon = Organization(name="헤어 살롱")
        db.add_all([cafe, salon])
        db.commit()
        
        # 2. 사용자 생성
        print("2️⃣  사용자 생성 중...")
        cafe_owner = User(org_id=cafe.id, email="cafe@example.com", role="owner")
        salon_owner = User(org_id=salon.id, email="salon@example.com", role="owner")
        db.add_all([cafe_owner, salon_owner])
        db.commit()
        
        # 3. 채널 생성
        print("3️⃣  채널 생성 중...")
        cafe_instagram = Channel(
            org_id=cafe.id,
            type="instagram",
            handle="@dongne_cafe",
            status="active",
            meta_json={"followers": 1234}
        )
        cafe_blog = Channel(
            org_id=cafe.id,
            type="blog",
            handle="blog.dongne-cafe.com",
            status="active",
            meta_json={}
        )
        db.add_all([cafe_instagram, cafe_blog])
        db.commit()
        
        # 4. 크레딧 지갑 생성
        print("4️⃣  크레딧 지갑 생성 중...")
        cafe_wallet = CreditWallet(org_id=cafe.id, balance=100, monthly_cap=50)
        salon_wallet = CreditWallet(org_id=salon.id, balance=100, monthly_cap=50)
        db.add_all([cafe_wallet, salon_wallet])
        db.commit()
        
        # 5. 14일치 일기 생성 (카페)
        print("5️⃣  사업 일기 생성 중...")
        journal_templates = [
            {
                "title": "평일 오후 손님 증가",
                "content": """오늘은 평일 오후 2시부터 5시까지 손님이 많았습니다.
특히 재택근무하시는 분들이 조용한 분위기를 찾아 오시는 것 같아요.
우리 카페의 넓은 테이블과 콘센트가 많다는 점이 강점인 것 같습니다.
"여기 조용해서 집중 잘 돼요!" 라는 말씀을 들었습니다.
아메리카노와 카페라떼 판매량이 높았습니다."""
            },
            {
                "title": "브런치 메뉴 인기",
                "content": """주말 브런치 메뉴가 인기가 많습니다.
에그 베네딕트와 팬케이크가 특히 잘 나갑니다.
인스타그램에 올린 사진을 보고 오시는 분들이 많아졌어요.
"브런치 메뉴 비주얼 좋아요!" 라는 후기를 받았습니다.
주말에는 웨이팅이 생길 정도입니다."""
            },
            {
                "title": "단골 손님 방문",
                "content": """단골 손님 김선생님이 오셨습니다.
항상 아메리카노 두 잔을 테이크아웃하시는데, 오늘은 케이크도 구매하셨어요.
"여기 케이크가 다른 곳보다 덜 달아서 좋아요" 라고 하셨습니다.
단골 손님들과의 관계가 우리 카페의 큰 자산인 것 같습니다."""
            },
        ]
        
        today = datetime.now()
        for i in range(14):
            date = today - timedelta(days=i)
            template = journal_templates[i % len(journal_templates)]
            
            journal = Journal(
                org_id=cafe.id,
                author_id=cafe_owner.id,
                date=date,
                title=f"Day {14-i}: {template['title']}",
                content_md=template['content'],
                media_urls=[],
                checklist_json=[
                    {"id": "post", "label": "포스트 1편", "completed": i % 2 == 0},
                    {"id": "story", "label": "스토리 1회", "completed": i % 3 == 0},
                ]
            )
            db.add(journal)
        
        db.commit()
        
        # 6. 정보자산 생성
        print("6️⃣  정보자산 생성 중...")
        assets = [
            Asset(
                org_id=cafe.id,
                asset_type="usp",
                title="조용한 작업 공간",
                body_json={"description": "재택근무자들이 선호하는 조용한 환경"},
                keywords=["조용한 카페", "작업하기 좋은 카페"],
                usps=["조용한 작업 공간"]
            ),
            Asset(
                org_id=cafe.id,
                asset_type="usp",
                title="넓은 테이블과 콘센트",
                body_json={"description": "노트북 작업에 최적화된 공간"},
                keywords=["노트북 카페", "콘센트 많은 카페"],
                usps=["넓은 테이블과 콘센트"]
            ),
            Asset(
                org_id=cafe.id,
                asset_type="usp",
                title="비주얼 좋은 브런치",
                body_json={"description": "인스타그램 감성의 브런치 메뉴"},
                keywords=["브런치 맛집", "예쁜 카페"],
                usps=["비주얼 좋은 브런치"]
            ),
        ]
        db.add_all(assets)
        db.commit()
        
        # 7. 콘텐츠 브리프 및 초안 생성
        print("7️⃣  콘텐츠 생성 중...")
        brief = ContentBrief(
            org_id=cafe.id,
            channel_type="instagram",
            brief_json={
                "core_message": "조용한 작업 공간으로서의 카페 가치 전달",
                "tone": "친근하고 전문적",
                "usps": ["조용한 작업 공간", "넓은 테이블"],
                "hashtag_categories": ["동네카페", "작업카페", "재택근무"]
            },
            derived_from_asset_ids=[assets[0].id, assets[1].id]
        )
        db.add(brief)
        db.commit()
        
        draft = ContentDraft(
            brief_id=brief.id,
            draft_json={
                "hook": "재택근무 할 때 집중이 안 되시나요? ☕",
                "body": "우리 동네 카페는 조용한 분위기와 넓은 테이블로 작업하기 딱 좋은 공간이에요. 콘센트도 넉넉해서 하루 종일 걱정 없어요! 오늘도 많은 분들이 노트북 들고 오셨는데, 다들 집중 잘 하시더라고요 😊",
                "hashtags": ["#동네카페", "#작업하기좋은카페", "#재택근무카페", "#조용한카페", "#노트북카페"],
                "first_comment": "평일 오후 2-5시가 가장 조용해요!"
            },
            llm_version="gpt-4",
            status="approved"
        )
        db.add(draft)
        db.commit()
        
        # 8. 일일 추천 생성
        print("8️⃣  일일 추천 생성 중...")
        daily_reco = DailyRecommendation(
            org_id=cafe.id,
            date=today,
            low_comp_keywords=["동네 작업 카페", "조용한 브런치 카페", "콘센트 많은 카페"],
            todays_usps=["조용한 작업 공간", "넓은 테이블과 콘센트"],
            rationale_md="최근 일기 분석 결과, 작업 공간으로서의 강점이 두드러짐"
        )
        db.add(daily_reco)
        db.commit()
        
        # 9. 진척 계획 생성
        print("9️⃣  진척 계획 생성 중...")
        week_start = today - timedelta(days=today.weekday())
        progress_plan = ProgressPlan(
            org_id=cafe.id,
            week_start=week_start,
            targets_json=[
                {"indicator": "포스트", "target_value": 3, "unit": "편"},
                {"indicator": "스토리", "target_value": 5, "unit": "회"},
                {"indicator": "고객 DM", "target_value": 10, "unit": "응답"}
            ]
        )
        db.add(progress_plan)
        db.commit()
        
        # 진척 기록
        ticks = [
            ProgressTick(plan_id=progress_plan.id, indicator="포스트", value=2),
            ProgressTick(plan_id=progress_plan.id, indicator="스토리", value=3),
            ProgressTick(plan_id=progress_plan.id, indicator="고객 DM", value=8),
        ]
        db.add_all(ticks)
        db.commit()
        
        # 10. 리포트 생성
        print("🔟 리포트 생성 중...")
        report = Report(
            org_id=cafe.id,
            period_type="weekly",
            period_start=week_start,
            period_end=today,
            summary_md="이번 주는 평일 오후 트래픽이 증가했으며, 브런치 메뉴의 인기가 높았습니다.",
            causes_json=[
                {
                    "description": "재택근무 증가로 인한 작업 공간 수요 증가",
                    "evidence_links": [{"type": "journal", "id": 1, "snippet": "조용한 분위기를 찾아..."}],
                    "confidence": 0.8
                }
            ],
            actions_json=[
                {
                    "description": "작업 공간 관련 콘텐츠 강화",
                    "priority": "high",
                    "related_cause_index": 0
                }
            ],
            links_json={}
        )
        db.add(report)
        db.commit()
        
        # 11. 실행 로그 생성
        print("1️⃣1️⃣ 로그 생성 중...")
        logs = [
            ExecutionLog(
                org_id=cafe.id,
                actor_id=cafe_owner.id,
                action="journal_created",
                target_type="journal",
                target_id=1,
                result_json={"title": "일기 작성 완료"}
            ),
            ExecutionLog(
                org_id=cafe.id,
                actor_id=cafe_owner.id,
                action="draft_generated",
                target_type="draft",
                target_id=1,
                result_json={"channel": "instagram"}
            ),
        ]
        db.add_all(logs)
        db.commit()
        
        print("✅ 시드 데이터 생성 완료!")
        print(f"   - 조직: {cafe.name}")
        print(f"   - 사용자: {cafe_owner.email}")
        print(f"   - 일기: 14개")
        print(f"   - 자산: 3개")
        print(f"   - 콘텐츠: 1개")
        print(f"   - 리포트: 1개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
