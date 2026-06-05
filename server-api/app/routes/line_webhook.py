import base64
import hashlib
import hmac
import json
import logging

from fastapi import APIRouter, HTTPException, Request

from app.config import get_settings
from app.services import line_service, member_service

router = APIRouter(prefix="/api/line", tags=["line"])
log = logging.getLogger(__name__)


def _verify_signature(body: bytes, signature: str, secret: str) -> bool:
    if not secret or not signature:
        return False
    digest = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature)


@router.post("/webhook")
async def line_webhook(request: Request):
    settings = get_settings()
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")
    if settings.line_channel_secret and not _verify_signature(body, signature, settings.line_channel_secret):
        raise HTTPException(status_code=403, detail="invalid_signature")

    payload = json.loads(body.decode("utf-8"))
    for event in payload.get("events", []):
        await _handle_event(event)
    return {"ok": True}


async def _handle_event(event: dict) -> None:
    event_type = event.get("type")
    if event_type == "follow":
        reply_token = event.get("replyToken")
        if reply_token:
            await line_service.reply_text(
                reply_token,
                "歡迎加入福泰會員優惠活動！\n請點選下方選單「會員註冊」填寫資料，完成後即可參加各項優惠活動。",
            )
        return

    if event_type == "message":
        msg = event.get("message", {})
        if msg.get("type") != "text":
            return
        text = (msg.get("text") or "").strip()
        user_id = event.get("source", {}).get("userId")
        reply_token = event.get("replyToken")
        if text in ("會員卡", "QR", "qr", "會員QR"):
            member = member_service.find_member_by_line(user_id) if user_id else None
            if not member:
                if reply_token:
                    await line_service.reply_text(reply_token, "您尚未註冊，請先點選「會員註冊」填寫資料。")
                return
            settings = get_settings()
            liff_qr = settings.liff_id_member_qr
            if reply_token:
                hint = f"line://app/{liff_qr}" if liff_qr else "請使用圖文選單「我的會員 QR」"
                await line_service.reply_text(reply_token, f"請開啟會員 QR 頁面：\n{hint}")
