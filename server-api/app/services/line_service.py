"""LINE Messaging API helpers."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import httpx

from app.config import Settings, get_settings

log = logging.getLogger(__name__)

LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


def _headers(settings: Settings) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.line_channel_access_token}",
        "Content-Type": "application/json",
    }


async def reply_text(reply_token: str, text: str, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if not settings.line_channel_access_token:
        log.warning("LINE_CHANNEL_ACCESS_TOKEN not set, skip reply")
        return
    body = {"replyToken": reply_token, "messages": [{"type": "text", "text": text}]}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(LINE_REPLY_URL, headers=_headers(settings), json=body)
        resp.raise_for_status()


async def push_messages(user_id: str, messages: List[Dict[str, Any]], settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if not settings.line_channel_access_token:
        log.warning("LINE_CHANNEL_ACCESS_TOKEN not set, skip push")
        return
    body = {"to": user_id, "messages": messages}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(LINE_PUSH_URL, headers=_headers(settings), json=body)
        resp.raise_for_status()


async def push_text(user_id: str, text: str, settings: Settings | None = None) -> None:
    await push_messages(user_id, [{"type": "text", "text": text}], settings)


async def push_redeem_success(
    user_id: str,
    campaign_name: str,
    coupon_code: str | None,
    settings: Settings | None = None,
) -> None:
    lines = [f"✅ 兌換成功：{campaign_name}"]
    if coupon_code:
        lines.append(f"您的優惠券碼：{coupon_code}")
    await push_text(user_id, "\n".join(lines), settings)
