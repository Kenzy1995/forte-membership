from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    settings_ok = bool(__import__("app.config", fromlist=["get_settings"]).get_settings().database_url)
    return {
        "status": "ok",
        "service": "futai-member-api",
        "database_configured": settings_ok,
    }
