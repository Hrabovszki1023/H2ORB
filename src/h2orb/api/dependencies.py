from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from h2orb.aqua.client import AquaClient
from h2orb.auth import SESSION_COOKIE_NAME, UserSession


async def get_user_session(request: Request) -> UserSession:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    session = await request.app.state.session_store.get(session_id)
    if session is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
    request.state.session_id = session_id
    return session


def get_aqua_client(
    session: Annotated[UserSession, Depends(get_user_session)],
) -> AquaClient:
    return session.client


def require_csrf_token(
    session: Annotated[UserSession, Depends(get_user_session)],
    csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> UserSession:
    if csrf_token is None or not secrets.compare_digest(csrf_token, session.csrf_token):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid request token")
    return session

