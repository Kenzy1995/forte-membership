"""Member registration and lookup."""

from __future__ import annotations

from typing import Any

from app.db import repository as repo
from app.db.session import session_scope


def find_member_by_line(line_user_id: str) -> dict[str, str] | None:
    with session_scope() as session:
        member = repo.find_member_by_line(session, line_user_id)
        return repo.member_to_dict(member) if member else None


def find_member_by_id(member_id: str) -> dict[str, str] | None:
    with session_scope() as session:
        member = repo.find_member_by_id(session, member_id)
        return repo.member_to_dict(member) if member else None


def phone_exists(phone: str, exclude_line_user_id: str | None = None) -> bool:
    with session_scope() as session:
        return repo.phone_taken(session, phone, exclude_line_user_id)


def register_member(
    *,
    line_user_id: str,
    name: str,
    phone: str,
    email: str,
    gender: str,
    birth_date: str,
    first_hotel: str,
) -> dict[str, Any]:
    with session_scope() as session:
        existing = repo.find_member_by_line(session, line_user_id)
        if existing:
            return {"status": "exists", "member": repo.member_to_dict(existing)}

        if repo.phone_taken(session, phone, exclude_line_user_id=line_user_id):
            raise ValueError("phone_already_registered")

        member = repo.create_member(
            session,
            line_user_id=line_user_id,
            name=name,
            phone=phone,
            email=email,
            gender=gender,
            birth_date=birth_date,
            first_hotel=first_hotel,
        )
        return {"status": "created", "member": repo.member_to_dict(member)}


def list_active_campaigns() -> list[dict[str, str]]:
    with session_scope() as session:
        return [repo.campaign_to_dict(c) for c in repo.list_active_campaigns(session)]
