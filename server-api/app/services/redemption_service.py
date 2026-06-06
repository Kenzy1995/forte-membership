"""Redemption logic with per-member+campaign lock + PostgreSQL UNIQUE."""

from __future__ import annotations

from typing import Any

from sqlalchemy.exc import IntegrityError

from app.db import repository as repo
from app.db.session import session_scope
from app.locks import get_redemption_lock


def get_redemptions_for_member(member_id: str) -> list[dict[str, str]]:
    with session_scope() as session:
        return [repo.redemption_to_dict(r) for r in repo.list_redemptions_for_member(session, member_id)]


def redeem(
    *,
    member_id: str,
    campaign_id: str,
    hotel: str,
    staff_id: str,
    social_platform: str = "",
    note: str = "",
) -> dict[str, Any]:
    lock_key = f"{member_id}:{campaign_id}"
    lock = get_redemption_lock(lock_key)
    with lock:
        with session_scope() as session:
            member = repo.find_member_by_id(session, member_id)
            if not member:
                raise ValueError("member_not_found")

            campaign = repo.find_campaign(session, campaign_id)
            if not campaign or campaign.status != "active":
                raise ValueError("campaign_not_active")

            hotels = [h.strip() for h in (campaign.hotels or "").split(",") if h.strip()]
            if hotels and hotel not in hotels:
                raise ValueError("hotel_not_allowed")

            if repo.has_redeemed(session, member_id, campaign_id):
                raise ValueError("already_redeemed")

            reward_type = campaign.reward_type or "physical"
            coupon_code = None
            if reward_type in ("digital_coupon", "both"):
                coupon_code = repo.assign_coupon_atomic(session, campaign_id, member_id)

            try:
                redemption = repo.create_redemption(
                    session,
                    member_id=member_id,
                    campaign_id=campaign_id,
                    hotel=hotel,
                    staff_id=staff_id,
                    social_platform=social_platform,
                    note=note,
                    reward_type=reward_type,
                    coupon_code=coupon_code,
                )
            except IntegrityError as exc:
                raise ValueError("already_redeemed") from exc

            return {
                "redemption_id": redemption.redemption_id,
                "member": repo.member_to_dict(member),
                "campaign": repo.campaign_to_dict(campaign),
                "coupon_code": coupon_code,
                "reward_type": reward_type,
            }
