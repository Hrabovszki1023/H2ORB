from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ARB_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "H2ORB – H2O Result Browser"
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: str = "INFO"
    reload: bool = False

    aqua_base_url: HttpUrl = HttpUrl("https://aqua.example.invalid")
    aqua_web_base_url: HttpUrl = HttpUrl("https://app.aqua-cloud.io/aquaWebNG")
    noise_marker: str = "[NOISE]"
    aqua_verify_tls: bool = True
    aqua_ca_bundle: Path | None = None
    aqua_timeout_seconds: float = Field(default=30.0, gt=0)
    aqua_max_connections: int = Field(default=20, ge=1)

    session_ttl_seconds: int = Field(default=1800, ge=60, le=86400)
    session_cookie_secure: bool = False
    login_max_attempts: int = Field(default=5, ge=1, le=100)
    login_window_seconds: int = Field(default=300, ge=10, le=3600)


@lru_cache
def get_settings() -> Settings:
    return Settings()

