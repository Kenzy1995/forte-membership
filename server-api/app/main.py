import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import get_settings
from app.db.session import get_engine
from app.routes import health, line_webhook, members, staff

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="福泰會員優惠活動 API", version="0.2.0")

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


@app.on_event("startup")
def verify_database():
    settings = get_settings()
    if not settings.database_url:
        log.warning("DATABASE_URL not set — API will fail on data requests")
        return
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        log.info("Database connection OK")
    except Exception as exc:
        log.error("Database connection failed: %s", exc)


@app.get("/api/config/public")
def public_config():
    settings = get_settings()
    return {
        "environment": settings.environment,
        "liff_id_register": settings.liff_id_register,
        "liff_id_member_qr": settings.liff_id_member_qr,
        "qr_ttl_seconds": settings.qr_ttl_seconds,
    }
