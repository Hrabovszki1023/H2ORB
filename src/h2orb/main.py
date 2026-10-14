from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from h2orb.api.routes import router
from h2orb.auth import LoginRateLimiter, SessionStore
from h2orb.config import get_settings

PACKAGE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.session_store = SessionStore(settings)
    app.state.login_rate_limiter = LoginRateLimiter(
        attempts=settings.login_max_attempts,
        window_seconds=settings.login_window_seconds,
    )
    try:
        yield
    finally:
        await app.state.session_store.close()


def create_app() -> FastAPI:
    settings = get_settings()
    if (
        settings.environment.lower() in {"prod", "production"}
        and not settings.session_cookie_secure
    ):
        raise RuntimeError("ARB_SESSION_COOKIE_SECURE must be true in production")
    application = FastAPI(
        title=settings.app_name,
        version="0.2.0",
        lifespan=lifespan,
    )
    application.mount(
        "/static",
        StaticFiles(directory=PACKAGE_DIR / "static"),
        name="static",
    )
    application.include_router(router)
    return application


app = create_app()
