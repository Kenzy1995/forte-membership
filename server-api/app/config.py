"""Application configuration from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "staging"
    base_url: str = "http://localhost:8080"

    spreadsheet_id: str = ""
    google_cloud_project: str = ""

    line_channel_secret: str = ""
    line_channel_access_token: str = ""

    liff_id_register: str = ""
    liff_id_member_qr: str = ""

    qr_signing_secret: str = "dev-change-me"
    qr_ttl_seconds: int = 60

    staff_pin_hash: str = ""

    sheet_members: str = "Members"
    sheet_campaigns: str = "Campaigns"
    sheet_redemptions: str = "Redemptions"
    sheet_coupons: str = "Coupons"


@lru_cache
def get_settings() -> Settings:
    return Settings()
