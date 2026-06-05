"""Redemption logic with per-member+campaign lock."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import Settings, get_settings
from app import sheets
from app.locks import get_redemption_lock
from app.services import member_service


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_redemptions_for_member(member_id: str, settings: Settings | None = None) -> List[Dict[str, str]]:
    settings = settings or get_settings()
    return [
        r
        for r in sheets.get_all_records(settings.sheet_redemptions, settings)
        if r.get("member_id") == member_id and r.get("狀態") == "completed"
    ]


def has_redeemed(member_id: str, campaign_id: str, settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    for row in sheets.get_all_records(settings.sheet_redemptions, settings):
        if (
            row.get("member_id") == member_id
            and row.get("campaign_id") == campaign_id
            and row.get("狀態") == "completed"
        ):
            return True
    return False


def find_campaign(campaign_id: str, settings: Settings | None = None) -> Optional[Dict[str, str]]:
    settings = settings or get_settings()
    for row in sheets.get_all_records(settings.sheet_campaigns, settings):
        if row.get("campaign_id") == campaign_id:
            return row
    return None


def assign_coupon(campaign_id: str, member_id: str, settings: Settings | None = None) -> Optional[str]:
    settings = settings or get_settings()
    ws = sheets.get_worksheet(settings.sheet_coupons, settings)
    values = ws.get_all_values()
    if not values:
        return None
    headers = values[0]
    hmap = sheets.header_map(headers)
    code_idx = hmap.get("coupon_code", 0)
    camp_idx = hmap.get("campaign_id", 1)
    member_idx = hmap.get("member_id", 2)
    time_idx = hmap.get("派發時間", 3)
    status_idx = hmap.get("使用狀態", 4)

    for row_num, row in enumerate(values[1:], start=2):
        if camp_idx >= len(row):
            continue
        if (row[camp_idx] if camp_idx < len(row) else "") != campaign_id:
            continue
        status = row[status_idx] if status_idx < len(row) else ""
        if status != "unused":
            continue
        code = row[code_idx] if code_idx < len(row) else ""
        ws.update_cell(row_num, member_idx + 1, member_id)
        ws.update_cell(row_num, time_idx + 1, _now_iso())
        ws.update_cell(row_num, status_idx + 1, "used")
        return code
    return None


def redeem(
    *,
    member_id: str,
    campaign_id: str,
    hotel: str,
    staff_id: str,
    social_platform: str = "",
    note: str = "",
    settings: Settings | None = None,
) -> Dict[str, Any]:
    settings = settings or get_settings()
    lock_key = f"{member_id}:{campaign_id}"
    lock = get_redemption_lock(lock_key)
    with lock:
        member = member_service.find_member_by_id(member_id, settings)
        if not member:
            raise ValueError("member_not_found")

        campaign = find_campaign(campaign_id, settings)
        if not campaign or campaign.get("狀態") != "active":
            raise ValueError("campaign_not_active")

        hotels = [h.strip() for h in campaign.get("適用館別", "").split(",") if h.strip()]
        if hotels and hotel not in hotels:
            raise ValueError("hotel_not_allowed")

        if has_redeemed(member_id, campaign_id, settings):
            raise ValueError("already_redeemed")

        reward_type = campaign.get("獎勵類型", "physical")
        coupon_code = None
        if reward_type in ("digital_coupon", "both"):
            coupon_code = assign_coupon(campaign_id, member_id, settings)

        redemption_id = str(uuid.uuid4())
        sheets.append_row(
            settings.sheet_redemptions,
            [
                redemption_id,
                member_id,
                campaign_id,
                hotel,
                _now_iso(),
                staff_id,
                social_platform,
                note,
                reward_type,
                coupon_code or "",
                "completed",
            ],
            settings,
        )
        return {
            "redemption_id": redemption_id,
            "member": member,
            "campaign": campaign,
            "coupon_code": coupon_code,
            "reward_type": reward_type,
        }
