from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.services import member_service, qr_service

router = APIRouter(prefix="/api/members", tags=["members"])


class RegisterRequest(BaseModel):
    line_user_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    phone: str = Field(min_length=8)
    email: str = ""
    gender: str = ""
    birth_date: str = ""
    first_hotel: str = ""


@router.post("/register")
def register_member(body: RegisterRequest):
    try:
        result = member_service.register_member(
            line_user_id=body.line_user_id,
            name=body.name,
            phone=body.phone,
            email=body.email,
            gender=body.gender,
            birth_date=body.birth_date,
            first_hotel=body.first_hotel,
        )
        return result
    except ValueError as exc:
        if str(exc) == "phone_already_registered":
            raise HTTPException(status_code=409, detail="此電話已被其他會員使用") from exc
        raise


@router.get("/by-line/{line_user_id}")
def get_member_by_line(line_user_id: str):
    member = member_service.find_member_by_line(line_user_id)
    if not member:
        raise HTTPException(status_code=404, detail="member_not_found")
    return member


@router.get("/{member_id}/qr")
def get_member_qr(member_id: str):
    member = member_service.find_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="member_not_found")
    content = qr_service.build_qr_content(member_id)
    return {
        "member_id": member_id,
        "qr_content": content,
        "qr_image_base64": qr_service.qr_image_base64(content),
        "ttl_seconds": get_settings().qr_ttl_seconds,
    }


@router.get("/campaigns/active")
def list_active_campaigns():
    return {"campaigns": member_service.list_active_campaigns()}
