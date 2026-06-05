"""Member QR generation and verification."""

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import time
from typing import Tuple

import qrcode

from app.config import Settings, get_settings


def _sign(payload: str, secret: str) -> str:
    digest = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest[:12]).decode().rstrip("=")


def build_qr_content(member_id: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    ts = int(time.time())
    payload = f"{member_id}:{ts}"
    sig = _sign(payload, settings.qr_signing_secret)
    return f"FTM:{member_id}:{ts}:{sig}"


def verify_qr_content(content: str, settings: Settings | None = None) -> Tuple[bool, str]:
    settings = settings or get_settings()
    parts = (content or "").strip().split(":")
    if len(parts) != 4 or parts[0] != "FTM":
        return False, "invalid_format"
    _, member_id, ts_str, sig = parts
    try:
        ts = int(ts_str)
    except ValueError:
        return False, "invalid_timestamp"
    if time.time() - ts > settings.qr_ttl_seconds:
        return False, "expired"
    expected = _sign(f"{member_id}:{ts}", settings.qr_signing_secret)
    if not hmac.compare_digest(expected, sig):
        return False, "invalid_signature"
    return True, member_id


def qr_image_base64(content: str) -> str:
    img = qrcode.make(content)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()
