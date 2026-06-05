import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.services import member_service, qr_service, redemption_service
from app.services import line_service

router = APIRouter(prefix="/api/staff", tags=["staff"])


class StaffLoginRequest(BaseModel):
    hotel: str
    staff_id: str
    pin: str


class RedeemRequest(BaseModel):
    qr_content: str
    campaign_id: str
    hotel: str
    staff_id: str
    social_platform: str = ""
    note: str = ""


def _verify_pin(pin: str) -> bool:
    settings = get_settings()
    if not settings.staff_pin_hash:
        return True  # dev mode when pin not configured
    try:
        return bcrypt.checkpw(pin.encode(), settings.staff_pin_hash.encode())
    except Exception:
        return False


@router.post("/login")
def staff_login(body: StaffLoginRequest):
    if not _verify_pin(body.pin):
        raise HTTPException(status_code=401, detail="invalid_pin")
    return {"ok": True, "hotel": body.hotel, "staff_id": body.staff_id}


@router.post("/lookup")
def staff_lookup(body: RedeemRequest):
    ok, member_id_or_reason = qr_service.verify_qr_content(body.qr_content)
    if not ok:
        raise HTTPException(status_code=400, detail=member_id_or_reason)
    member = member_service.find_member_by_id(member_id_or_reason)
    if not member:
        raise HTTPException(status_code=404, detail="member_not_found")
    redemptions = redemption_service.get_redemptions_for_member(member_id_or_reason)
    campaigns = member_service.list_active_campaigns()
    return {
        "member": {
            "member_id": member.get("member_id"),
            "name": member.get("姓名"),
            "phone_tail": (member.get("電話") or "")[-4:],
        },
        "redemptions": redemptions,
        "active_campaigns": campaigns,
    }


@router.post("/redeem")
async def staff_redeem(body: RedeemRequest):
    ok, member_id_or_reason = qr_service.verify_qr_content(body.qr_content)
    if not ok:
        raise HTTPException(status_code=400, detail=member_id_or_reason)
    try:
        result = redemption_service.redeem(
            member_id=member_id_or_reason,
            campaign_id=body.campaign_id,
            hotel=body.hotel,
            staff_id=body.staff_id,
            social_platform=body.social_platform,
            note=body.note,
        )
    except ValueError as exc:
        code = str(exc)
        status = 409 if code == "already_redeemed" else 400
        raise HTTPException(status_code=status, detail=code) from exc

    member = result["member"]
    line_user_id = member.get("line_user_id")
    if line_user_id:
        await line_service.push_redeem_success(
            line_user_id,
            result["campaign"].get("活動名稱", body.campaign_id),
            result.get("coupon_code"),
        )
    return result
