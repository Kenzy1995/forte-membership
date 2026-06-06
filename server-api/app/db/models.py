"""Database models for Forte membership platform."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Member(Base):
    __tablename__ = "members"

    member_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    line_user_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), default="")
    gender: Mapped[str] = mapped_column(String(16), default="")
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    first_hotel: Mapped[str] = mapped_column(String(100), default="")
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)


class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    campaign_type: Mapped[str] = mapped_column(String(32), default="custom")
    hotels: Mapped[str] = mapped_column(Text, default="")  # comma-separated
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    reward_type: Mapped[str] = mapped_column(String(32), default="physical")
    reward_description: Mapped[str] = mapped_column(Text, default="")
    max_per_member: Mapped[int] = mapped_column(default=1)
    redeem_note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)


class Redemption(Base):
    __tablename__ = "redemptions"
    __table_args__ = (
        UniqueConstraint("member_id", "campaign_id", name="uq_redemption_member_campaign"),
        Index("ix_redemptions_member", "member_id"),
    )

    redemption_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id: Mapped[str] = mapped_column(String(36), nullable=False)
    campaign_id: Mapped[str] = mapped_column(String(64), nullable=False)
    hotel: Mapped[str] = mapped_column(String(100), nullable=False)
    redeemed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    staff_id: Mapped[str] = mapped_column(String(64), default="")
    social_platform: Mapped[str] = mapped_column(String(32), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    reward_type: Mapped[str] = mapped_column(String(32), default="physical")
    coupon_code: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(20), default="completed")


class Coupon(Base):
    __tablename__ = "coupons"
    __table_args__ = (Index("ix_coupons_campaign_status", "campaign_id", "status"),)

    coupon_code: Mapped[str] = mapped_column(String(64), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    member_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="unused")
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
