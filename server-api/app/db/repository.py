"""Member / campaign / redemption DB operations."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Campaign, Coupon, Member, Redemption


def _today() -> date:
    return datetime.now(timezone.utc).date()


def member_to_dict(m: Member) -> dict[str, str]:
    return {
        "member_id": m.member_id,
        "line_user_id": m.line_user_id,
        "姓名": m.name,
        "電話": m.phone,
        "email": m.email or "",
        "性別": m.gender or "",
        "出生年月日": m.birth_date.isoformat() if m.birth_date else "",
        "首次參加館別": m.first_hotel or "",
        "註冊時間": m.registered_at.isoformat() if m.registered_at else "",
        "狀態": m.status,
    }


def campaign_to_dict(c: Campaign) -> dict[str, str]:
    return {
        "campaign_id": c.campaign_id,
        "活動名稱": c.name,
        "活動類型": c.campaign_type,
        "適用館別": c.hotels,
        "開始日期": c.start_date.isoformat() if c.start_date else "",
        "結束日期": c.end_date.isoformat() if c.end_date else "",
        "獎勵類型": c.reward_type,
        "獎勵描述": c.reward_description or "",
        "每人限領次數": str(c.max_per_member),
        "兌換條件說明": c.redeem_note or "",
        "狀態": c.status,
    }


def redemption_to_dict(r: Redemption) -> dict[str, str]:
    return {
        "redemption_id": r.redemption_id,
        "member_id": r.member_id,
        "campaign_id": r.campaign_id,
        "兌換館別": r.hotel,
        "兌換時間": r.redeemed_at.isoformat() if r.redeemed_at else "",
        "核銷人員": r.staff_id or "",
        "社群平台": r.social_platform or "",
        "審核備註": r.note or "",
        "獎勵類型": r.reward_type,
        "券碼": r.coupon_code or "",
        "狀態": r.status,
    }


def find_member_by_line(session: Session, line_user_id: str) -> Member | None:
    stmt = select(Member).where(Member.line_user_id == line_user_id, Member.status == "active")
    return session.scalars(stmt).first()


def find_member_by_id(session: Session, member_id: str) -> Member | None:
    return session.get(Member, member_id)


def phone_taken(session: Session, phone: str, exclude_line_user_id: str | None = None) -> bool:
    stmt = select(Member).where(Member.phone == phone)
    if exclude_line_user_id:
        stmt = stmt.where(Member.line_user_id != exclude_line_user_id)
    return session.scalars(stmt).first() is not None


def create_member(
    session: Session,
    *,
    line_user_id: str,
    name: str,
    phone: str,
    email: str,
    gender: str,
    birth_date: str,
    first_hotel: str,
) -> Member:
    bd: date | None = None
    if birth_date:
        bd = date.fromisoformat(birth_date)
    member = Member(
        member_id=str(uuid.uuid4()),
        line_user_id=line_user_id,
        name=name,
        phone=phone,
        email=email,
        gender=gender,
        birth_date=bd,
        first_hotel=first_hotel,
    )
    session.add(member)
    session.flush()
    return member


def list_active_campaigns(session: Session) -> list[Campaign]:
    today = _today()
    stmt = select(Campaign).where(Campaign.status == "active")
    rows = list(session.scalars(stmt).all())
    result = []
    for c in rows:
        if c.start_date and today < c.start_date:
            continue
        if c.end_date and today > c.end_date:
            continue
        result.append(c)
    return result


def find_campaign(session: Session, campaign_id: str) -> Campaign | None:
    return session.get(Campaign, campaign_id)


def list_redemptions_for_member(session: Session, member_id: str) -> list[Redemption]:
    stmt = select(Redemption).where(
        Redemption.member_id == member_id,
        Redemption.status == "completed",
    )
    return list(session.scalars(stmt).all())


def has_redeemed(session: Session, member_id: str, campaign_id: str) -> bool:
    stmt = select(Redemption.redemption_id).where(
        Redemption.member_id == member_id,
        Redemption.campaign_id == campaign_id,
        Redemption.status == "completed",
    )
    return session.scalars(stmt).first() is not None


def assign_coupon_atomic(session: Session, campaign_id: str, member_id: str) -> str | None:
    stmt = (
        select(Coupon)
        .where(Coupon.campaign_id == campaign_id, Coupon.status == "unused")
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    coupon = session.scalars(stmt).first()
    if not coupon:
        return None
    coupon.member_id = member_id
    coupon.assigned_at = datetime.now(timezone.utc)
    coupon.status = "used"
    session.flush()
    return coupon.coupon_code


def create_redemption(
    session: Session,
    *,
    member_id: str,
    campaign_id: str,
    hotel: str,
    staff_id: str,
    social_platform: str,
    note: str,
    reward_type: str,
    coupon_code: str | None,
) -> Redemption:
    redemption = Redemption(
        redemption_id=str(uuid.uuid4()),
        member_id=member_id,
        campaign_id=campaign_id,
        hotel=hotel,
        staff_id=staff_id,
        social_platform=social_platform,
        note=note,
        reward_type=reward_type,
        coupon_code=coupon_code or "",
        status="completed",
    )
    session.add(redemption)
    session.flush()
    return redemption
