"""
Affiliate Router for AICA-SyS
Phase 9-4: Affiliate system
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.affiliate_service import AffiliateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/affiliate", tags=["affiliate"])


# Request Models
class AffiliateRegisterRequest(BaseModel):
    """アフィリエイト登録リクエスト"""

    user_id: str


class ReferralLinkCreateRequest(BaseModel):
    """紹介リンク作成リクエスト"""

    affiliate_id: int
    destination_url: str
    campaign_name: Optional[str] = None
    valid_until: Optional[datetime] = None


class ClickTrackRequest(BaseModel):
    """クリック追跡リクエスト"""

    link_code: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    session_id: Optional[str] = None


class ConversionRecordRequest(BaseModel):
    """コンバージョン記録リクエスト"""

    link_code: str
    referred_user_id: str
    conversion_value: float
    subscription_id: Optional[int] = None


class CommissionRuleCreateRequest(BaseModel):
    """報酬ルール作成リクエスト"""

    tier: str
    reward_type: str
    fixed_amount: Optional[float] = None
    percentage: Optional[float] = None
    min_threshold: Optional[float] = None


class PayoutRequest(BaseModel):
    """支払いリクエスト"""

    affiliate_id: int
    amount: Optional[float] = None
    payment_method: str = "bank_transfer"


class AffiliateCouponCreateRequest(BaseModel):
    """アフィリエイトクーポン作成リクエスト"""

    affiliate_id: int
    discount_type: str
    discount_value: float
    max_uses: Optional[int] = None
    valid_until: Optional[datetime] = None


# Affiliate Endpoints
@router.post("/register")
async def register_affiliate(
    request: AffiliateRegisterRequest, db: Session = Depends(get_db)
):
    """アフィリエイトを登録"""
    try:
        service = AffiliateService(db)
        affiliate = await service.register_affiliate(request.user_id)
        return {"success": True, "affiliate": affiliate}
    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Affiliate registration error")
        raise HTTPException(status_code=500, detail="登録に失敗しました") from e


@router.get("/profile/{user_id}")
async def get_affiliate_profile(user_id: str, db: Session = Depends(get_db)):
    """アフィリエイトプロフィールを取得"""
    try:
        service = AffiliateService(db)
        affiliate = await service.get_affiliate(user_id)
        if not affiliate:
            raise HTTPException(
                status_code=404, detail="アフィリエイトが見つかりません"
            )

        stats = await service.get_affiliate_stats(affiliate.id)
        return {"success": True, "affiliate": affiliate, "stats": stats}
    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Get affiliate profile error")
        raise HTTPException(status_code=500, detail="取得に失敗しました") from e


@router.put("/{affiliate_id}/tier")
async def update_affiliate_tier(
    affiliate_id: int, new_tier: str, db: Session = Depends(get_db)
):
    """アフィリエイトティアを更新"""
    try:
        service = AffiliateService(db)
        affiliate = await service.update_affiliate_tier(affiliate_id, new_tier)
        return {"success": True, "affiliate": affiliate}
    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Update tier error")
        raise HTTPException(status_code=500, detail="更新に失敗しました") from e


# Referral Link Endpoints
@router.post("/referral-links")
async def create_referral_link(
    request: ReferralLinkCreateRequest, db: Session = Depends(get_db)
):
    """紹介リンクを作成"""
    try:
        service = AffiliateService(db)
        link = await service.create_referral_link(
            affiliate_id=request.affiliate_id,
            destination_url=request.destination_url,
            campaign_name=request.campaign_name,
            valid_until=request.valid_until,
        )
        return {"success": True, "link": link}
    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Create referral link error")
        raise HTTPException(status_code=500, detail="作成に失敗しました") from e


@router.get("/referral-links/{affiliate_id}")
async def get_referral_links(
    affiliate_id: int, active_only: bool = True, db: Session = Depends(get_db)
):
    """紹介リンク一覧を取得"""
    try:
        service = AffiliateService(db)
        links = await service.get_referral_links(affiliate_id, active_only)
        return {"success": True, "links": links, "count": len(links)}
    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Get referral links error")
        raise HTTPException(status_code=500, detail="取得に失敗しました") from e


# Click Tracking Endpoints
@router.post("/track-click")
async def track_click(request: ClickTrackRequest, db: Session = Depends(get_db)):
    """クリックを追跡"""
    try:
        service = AffiliateService(db)
        click = await service.track_click(
            link_code=request.link_code,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            referrer=request.referrer,
            session_id=request.session_id,
        )
        return {"success": True, "click": click}
    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Track click error")
        raise HTTPException(status_code=500, detail="追跡に失敗しました") from e


# Conversion Endpoints
@router.post("/conversions")
async def record_conversion(
    request: ConversionRecordRequest, db: Session = Depends(get_db)
):
    """コンバージョンを記録"""
    try:
        service = AffiliateService(db)
        conversion = await service.record_conversion(
            link_code=request.link_code,
            referred_user_id=request.referred_user_id,
            conversion_value=request.conversion_value,
            subscription_id=request.subscription_id,
        )
        return {"success": True, "conversion": conversion}
    except HTTPException:

        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Record conversion error")
        raise HTTPException(status_code=500, detail="記録に失敗しました") from e


@router.put("/conversions/{conversion_id}/approve")
async def approve_conversion(conversion_id: int, db: Session = Depends(get_db)):
    """コンバージョンを承認"""
    try:
        service = AffiliateService(db)
        conversion = await service.approve_conversion(conversion_id)
        return {"success": True, "conversion": conversion}
    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Approve conversion error")
        raise HTTPException(status_code=500, detail="承認に失敗しました") from e


# Commission Rule Endpoints
@router.post("/commission-rules")
async def create_commission_rule(
    request: CommissionRuleCreateRequest, db: Session = Depends(get_db)
):
    """報酬ルールを作成"""
    try:
        service = AffiliateService(db)
        rule = await service.create_commission_rule(
            tier=request.tier,
            reward_type=request.reward_type,
            fixed_amount=request.fixed_amount,
            percentage=request.percentage,
            min_threshold=request.min_threshold,
        )
        return {"success": True, "rule": rule}
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Create commission rule error")
        raise HTTPException(status_code=500, detail="作成に失敗しました") from e


@router.get("/commission-rules")
async def get_commission_rules(
    tier: Optional[str] = None, active_only: bool = True, db: Session = Depends(get_db)
):
    """報酬ルール一覧を取得"""
    try:
        service = AffiliateService(db)
        rules = await service.get_commission_rules(tier, active_only)
        return {"success": True, "rules": rules, "count": len(rules)}
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Get commission rules error")
        raise HTTPException(status_code=500, detail="取得に失敗しました") from e


# Payout Endpoints
@router.post("/payouts")
async def request_payout(request: PayoutRequest, db: Session = Depends(get_db)):
    """支払いをリクエスト"""
    try:
        service = AffiliateService(db)
        payout = await service.request_payout(
            affiliate_id=request.affiliate_id,
            amount=request.amount,
            payment_method=request.payment_method,
        )
        return {"success": True, "payout": payout}
    except HTTPException:

        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Request payout error")
        raise HTTPException(status_code=500, detail="リクエストに失敗しました") from e


@router.put("/payouts/{payout_id}/complete")
async def complete_payout(
    payout_id: int, transaction_id: Optional[str] = None, db: Session = Depends(get_db)
):
    """支払いを完了"""
    try:
        service = AffiliateService(db)
        payout = await service.complete_payout(payout_id, transaction_id)
        return {"success": True, "payout": payout}
    except HTTPException:

        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Complete payout error")
        raise HTTPException(status_code=500, detail="完了に失敗しました") from e


@router.get("/payouts/{affiliate_id}")
async def get_payouts(
    affiliate_id: int, limit: int = 50, db: Session = Depends(get_db)
):
    """支払い履歴を取得"""
    try:
        service = AffiliateService(db)
        payouts = await service.get_payouts(affiliate_id, limit)
        return {"success": True, "payouts": payouts, "count": len(payouts)}
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Get payouts error")
        raise HTTPException(status_code=500, detail="取得に失敗しました") from e


# Affiliate Coupon Endpoints
@router.post("/coupons")
async def create_affiliate_coupon(
    request: AffiliateCouponCreateRequest, db: Session = Depends(get_db)
):
    """アフィリエイト専用クーポンを作成"""
    try:
        service = AffiliateService(db)
        coupon = await service.create_affiliate_coupon(
            affiliate_id=request.affiliate_id,
            discount_type=request.discount_type,
            discount_value=request.discount_value,
            max_uses=request.max_uses,
            valid_until=request.valid_until,
        )
        return {"success": True, "coupon": coupon}
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Create affiliate coupon error")
        raise HTTPException(status_code=500, detail="作成に失敗しました") from e


# Analytics Endpoints
@router.get("/stats/{affiliate_id}")
async def get_affiliate_stats(affiliate_id: int, db: Session = Depends(get_db)):
    """アフィリエイト統計を取得"""
    try:
        service = AffiliateService(db)
        stats = await service.get_affiliate_stats(affiliate_id)
        return {"success": True, "stats": stats}
    except HTTPException:

        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Get affiliate stats error")
        raise HTTPException(status_code=500, detail="取得に失敗しました") from e


@router.get("/top-affiliates")
async def get_top_affiliates(
    limit: int = 10, order_by: str = "total_revenue", db: Session = Depends(get_db)
):
    """トップアフィリエイトを取得"""
    try:
        service = AffiliateService(db)
        affiliates = await service.get_top_affiliates(limit, order_by)
        return {"success": True, "affiliates": affiliates, "count": len(affiliates)}
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Get top affiliates error")
        raise HTTPException(status_code=500, detail="取得に失敗しました") from e


# Admin Endpoints
class ReferralLinkUpdateRequest(BaseModel):
    """紹介リンク更新リクエスト"""

    is_active: Optional[bool] = None
    valid_until: Optional[datetime] = None


@router.put("/referral-links/{link_id}")
async def update_referral_link(
    link_id: int,
    request: ReferralLinkUpdateRequest,
    db: Session = Depends(get_db),
):
    """紹介リンクを更新（管理者用）"""
    try:
        service = AffiliateService(db)
        link = await service.update_referral_link(
            link_id=link_id,
            is_active=request.is_active,
            valid_until=request.valid_until,
        )
        return {"success": True, "link": link}
    except HTTPException:

        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Update referral link error")
        raise HTTPException(status_code=500, detail="更新に失敗しました") from e


@router.get("/admin/referral-links")
async def get_all_referral_links(
    active_only: bool = True,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """全紹介リンクを取得（管理者用）"""
    try:
        service = AffiliateService(db)
        links = await service.get_all_referral_links(active_only, limit)
        return {"success": True, "links": links, "count": len(links)}
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Get all referral links error")
        raise HTTPException(status_code=500, detail="取得に失敗しました") from e


@router.get("/admin/click-statistics")
async def get_click_statistics(
    affiliate_id: Optional[int] = None,
    link_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """クリック統計を取得（管理者用）"""
    try:
        service = AffiliateService(db)
        stats = await service.get_click_statistics(affiliate_id, link_id)
        return {"success": True, "statistics": stats}
    except HTTPException:

        raise

    except Exception as e:
        logger.exception("Get click statistics error")
        raise HTTPException(status_code=500, detail="取得に失敗しました") from e
