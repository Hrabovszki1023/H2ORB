from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from h2orb.api.dependencies import get_aqua_client, require_csrf_token
from h2orb.aqua.client import (
    AquaApiError,
    AquaAuthenticationError,
    AquaClient,
    AquaConfigurationError,
)
from h2orb.auth import SESSION_COOKIE_NAME, UserSession
from h2orb.config import get_settings
from h2orb.services.navigation import map_projects, map_scenarios, map_subfolders
from h2orb.services.report import build_markdown_report, build_report

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    settings = get_settings()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
            "environment": settings.environment,
        },
    )


@router.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/v1/status", tags=["application"])
def application_status() -> dict[str, str]:
    return {
        "application": "ready",
        "aquaIntegration": "awaiting-swagger-mapping",
    }


@router.get("/api/v1/auth/session", tags=["authentication"])
async def authentication_session(request: Request) -> JSONResponse:
    session = await request.app.state.session_store.get(
        request.cookies.get(SESSION_COOKIE_NAME)
    )
    if session is None:
        return JSONResponse(
            {"authenticated": False}, headers={"Cache-Control": "no-store"}
        )
    return JSONResponse(
        {"authenticated": True, "csrfToken": session.csrf_token},
        headers={"Cache-Control": "no-store"},
    )


@router.post("/api/v1/auth/login", tags=["authentication"])
async def login(request: Request) -> JSONResponse:
    content_length = request.headers.get("content-length")
    try:
        if content_length and int(content_length) > 4096:
            raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Invalid login request")
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid login request") from exc
    if request.headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Invalid login request")
    try:
        body = await request.body()
        if len(body) > 4096:
            raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Invalid login request")
        payload = json.loads(body)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid login request") from exc
    username = payload.get("username") if isinstance(payload, dict) else None
    password = payload.get("password") if isinstance(payload, dict) else None
    if (
        not isinstance(username, str)
        or not isinstance(password, str)
        or not username.strip()
        or not password
        or len(username) > 256
        or len(password) > 1024
    ):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid login request")

    client_key = request.client.host if request.client else "unknown"
    limiter = request.app.state.login_rate_limiter
    if not await limiter.allowed(client_key):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many login attempts")

    try:
        session_id, session = await request.app.state.session_store.create(
            username.strip(), password
        )
    except (AquaApiError, AquaConfigurationError):
        await limiter.record_failure(client_key)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Login failed") from None

    await limiter.reset(client_key)
    await request.app.state.session_store.delete(
        request.cookies.get(SESSION_COOKIE_NAME)
    )
    settings = get_settings()
    response = JSONResponse(
        {"authenticated": True, "csrfToken": session.csrf_token},
        headers={"Cache-Control": "no-store"},
    )
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_id,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="strict",
        path="/",
    )
    return response


@router.post("/api/v1/auth/logout", tags=["authentication"])
async def logout(
    request: Request,
    _session: Annotated[UserSession, Depends(require_csrf_token)],
) -> JSONResponse:
    await request.app.state.session_store.delete(request.state.session_id)
    response = JSONResponse(
        {"authenticated": False}, headers={"Cache-Control": "no-store"}
    )
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return response


@router.get("/api/v1/aqua/projects", tags=["aqua"])
async def aqua_projects(
    client: Annotated[AquaClient, Depends(get_aqua_client)],
) -> dict[str, object]:
    try:
        payload = await client.get_project_tree([], include_projects=True)
    except AquaAuthenticationError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required") from exc
    except AquaConfigurationError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    except AquaApiError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return {"items": map_projects(payload)}


@router.get("/api/v1/aqua/projects/{project_id}/folders", tags=["aqua"])
async def aqua_folders(
    project_id: int,
    client: Annotated[AquaClient, Depends(get_aqua_client)],
    folder_id: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, object]:
    try:
        payload = await client.get_project_tree([f"{project_id}_{folder_id}"])
    except AquaAuthenticationError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required") from exc
    except AquaConfigurationError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    except AquaApiError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return {"items": map_subfolders(payload)}


@router.get("/api/v1/aqua/projects/{project_id}/scenarios", tags=["aqua"])
async def aqua_scenarios(
    project_id: int,
    client: Annotated[AquaClient, Depends(get_aqua_client)],
    folder_id: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, object]:
    try:
        items = await client.get_all_test_scenarios(project_id, folder_id)
    except AquaAuthenticationError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required") from exc
    except AquaConfigurationError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    except AquaApiError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    scenarios = map_scenarios(items)
    return {"count": len(scenarios), "items": scenarios}


@router.get("/api/v1/aqua/projects/{project_id}/report", tags=["aqua"])
async def aqua_report(
    project_id: int,
    client: Annotated[AquaClient, Depends(get_aqua_client)],
    folder_id: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, object]:
    settings = get_settings()
    try:
        raw_scenarios = await client.get_all_test_scenarios(project_id, folder_id)
        scenarios = map_scenarios(raw_scenarios)
        report = await build_report(
            client,
            scenarios,
            selected_folder_id=folder_id,
            aqua_web_base_url=str(settings.aqua_web_base_url),
            noise_marker=settings.noise_marker,
        )
    except AquaAuthenticationError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required") from exc
    except AquaConfigurationError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    except AquaApiError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return {"projectId": project_id, "folderId": folder_id, **report}


@router.post("/api/v1/report/markdown", tags=["application"])
async def markdown_report(
    payload: dict[str, object],
    _session: Annotated[UserSession, Depends(require_csrf_token)],
) -> dict[str, str]:
    tree = payload.get("tree")
    if not isinstance(tree, dict):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Missing report tree")
    generated_at = str(payload.get("generatedAt") or "")
    language = str(payload.get("language") or "de")
    if language not in {"de", "en"}:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Unsupported language")
    raw_keys = payload.get("summaryKeys") or []
    if not isinstance(raw_keys, list) or not all(isinstance(key, str) for key in raw_keys):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid summary keys")
    return {
        "markdown": build_markdown_report(
            tree,
            generated_at=generated_at,
            language=language,
            summary_keys=raw_keys,
        )
    }
