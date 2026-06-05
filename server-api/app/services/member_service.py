"""Member registration and lookup."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import Settings, get_settings
from app import sheets


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_member_by_line(line_user_id: str, settings: Settings | None = None) -> Optional[Dict[str, str]]:
    settings = settings or get_settings()
    for row in sheets.get_all_records(settings.sheet_members, settings):
        if row.get("line_user_id") == line_user_id and row.get("狀態", "active") == "active":
            return row
    return None


def find_member_by_id(member_id: str, settings: Settings | None = None) -> Optional[Dict[str, str]]:
    settings = settings or get_settings()
    for row in sheets.get_all_records(settings.sheet_members, settings):
        if row.get("member_id") == member_id:
            return row
    return None


def phone_exists(phone: str, exclude_line_user_id: str | None = None, settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    for row in sheets.get_all_records(settings.sheet_members, settings):
        if row.get("電話") == phone and row.get("line_user_id") != exclude_line_user_id:
            return True
    return False


def register_member(
    *,
    line_user_id: str,
    name: str,
    phone: str,
    email: str,
    gender: str,
    birth_date: str,
    first_hotel: str,
    settings: Settings | None = None,
) -> Dict[str, Any]:
    settings = settings or get_settings()
    existing = find_member_by_line(line_user_id, settings)
    if existing:
        return {"status": "exists", "member": existing}

    if phone_exists(phone, exclude_line_user_id=line_user_id, settings=settings):
        raise ValueError("phone_already_registered")

    member_id = str(uuid.uuid4())
    row = [
        member_id,
        line_user_id,
        name,
        phone,
        email,
        gender,
        birth_date,
        first_hotel,
        _now_iso(),
        "active",
    ]
    sheets.append_row(settings.sheet_members, row, settings)
    member = find_member_by_id(member_id, settings)
    return {"status": "created", "member": member}


def list_active_campaigns(settings: Settings | None = None) -> List[Dict[str, str]]:
    settings = settings or get_settings()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = []
    for row in sheets.get_all_records(settings.sheet_campaigns, settings):
        if row.get("狀態") != "active":
            continue
        start = row.get("開始日期", "")
        end = row.get("結束日期", "")
        if start and today < start:
            continue
        if end and today > end:
            continue
        result.append(row)
    return result
