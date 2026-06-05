import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import health, line_webhook, members, staff

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="福泰會員優惠活動 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(members.router)
app.include_router(staff.router)
app.include_router(line_webhook.router)

_web_dir = Path(__file__).resolve().parent.parent.parent / "web"
if _web_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(_web_dir), html=True), name="web")


@app.get("/api/config/public")
def public_config():
    settings = get_settings()
    return {
        "environment": settings.environment,
        "liff_id_register": settings.liff_id_register,
        "liff_id_member_qr": settings.liff_id_member_qr,
        "qr_ttl_seconds": settings.qr_ttl_seconds,
    }
