from __future__ import annotations

import asyncio
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass

from h2orb.aqua.client import AquaClient
from h2orb.config import Settings

SESSION_COOKIE_NAME = "h2orb_session"


@dataclass(slots=True)
class UserSession:
    client: AquaClient
    csrf_token: str
    expires_at: float


class SessionStore:
    """In-memory AQUA sessions indexed by opaque, random browser identifiers."""

    def __init__(
        self,
        settings: Settings,
        client_factory: Callable[[Settings], AquaClient] = AquaClient,
    ) -> None:
        self._settings = settings
        self._client_factory = client_factory
        self._sessions: dict[str, UserSession] = {}
        self._lock = asyncio.Lock()

    async def create(self, username: str, password: str) -> tuple[str, UserSession]:
        await self._purge_expired()
        client = self._client_factory(self._settings)
        try:
            await client.authenticate(username, password)
        except Exception:
            await client.close()
            raise

        session_id = secrets.token_urlsafe(32)
        session = UserSession(
            client=client,
            csrf_token=secrets.token_urlsafe(32),
            expires_at=time.monotonic() + self._settings.session_ttl_seconds,
        )
        async with self._lock:
            self._sessions[session_id] = session
        return session_id, session

    async def get(self, session_id: str | None) -> UserSession | None:
        if not session_id:
            return None
        expired: UserSession | None = None
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            if time.monotonic() >= session.expires_at:
                expired = self._sessions.pop(session_id)
            else:
                return session
        if expired is not None:
            await expired.client.close()
        return None

    async def delete(self, session_id: str | None) -> None:
        if not session_id:
            return
        async with self._lock:
            session = self._sessions.pop(session_id, None)
        if session is not None:
            await session.client.close()

    async def close(self) -> None:
        async with self._lock:
            sessions = list(self._sessions.values())
            self._sessions.clear()
        await asyncio.gather(*(session.client.close() for session in sessions))

    async def _purge_expired(self) -> None:
        now = time.monotonic()
        async with self._lock:
            expired = [
                self._sessions.pop(session_id)
                for session_id, session in list(self._sessions.items())
                if now >= session.expires_at
            ]
        await asyncio.gather(*(session.client.close() for session in expired))


class LoginRateLimiter:
    def __init__(self, *, attempts: int, window_seconds: int) -> None:
        self._attempts = attempts
        self._window_seconds = window_seconds
        self._failures: dict[str, list[float]] = {}
        self._lock = asyncio.Lock()

    async def allowed(self, key: str) -> bool:
        now = time.monotonic()
        async with self._lock:
            recent = [
                attempt
                for attempt in self._failures.get(key, [])
                if now - attempt < self._window_seconds
            ]
            if recent:
                self._failures[key] = recent
            else:
                self._failures.pop(key, None)
            return len(recent) < self._attempts

    async def record_failure(self, key: str) -> None:
        async with self._lock:
            self._failures.setdefault(key, []).append(time.monotonic())

    async def reset(self, key: str) -> None:
        async with self._lock:
            self._failures.pop(key, None)
