from __future__ import annotations

import asyncio
from typing import Any

import httpx
import respx
from fastapi.testclient import TestClient

from h2orb.aqua.client import AquaAuthenticationError, AquaClient
from h2orb.auth import LoginRateLimiter, SessionStore
from h2orb.config import Settings
from h2orb.main import create_app


class FakeAquaClient:
    def __init__(self, _settings: Settings) -> None:
        self.credentials: tuple[str, str] | None = None
        self.closed = False

    async def authenticate(self, username: str, password: str) -> None:
        if password == "wrong":
            raise AquaAuthenticationError("rejected")
        self.credentials = (username, password)

    async def close(self) -> None:
        self.closed = True


def test_session_store_isolates_clients_and_closes_them() -> None:
    async def exercise() -> None:
        store = SessionStore(Settings(), client_factory=FakeAquaClient)  # type: ignore[arg-type]

        first_id, first = await store.create("alice", "one")
        second_id, second = await store.create("bob", "two")

        assert first_id != second_id
        assert first.client is not second.client
        assert await store.get(first_id) is first
        await store.delete(first_id)
        assert first.client.closed  # type: ignore[attr-defined]
        assert await store.get(first_id) is None

        await store.close()
        assert second.client.closed  # type: ignore[attr-defined]

    asyncio.run(exercise())


def test_rate_limiter_blocks_after_failed_attempts() -> None:
    async def exercise() -> None:
        limiter = LoginRateLimiter(attempts=2, window_seconds=300)

        assert await limiter.allowed("client")
        await limiter.record_failure("client")
        assert await limiter.allowed("client")
        await limiter.record_failure("client")
        assert not await limiter.allowed("client")
        await limiter.reset("client")
        assert await limiter.allowed("client")

    asyncio.run(exercise())


def test_aqua_endpoint_requires_login() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/aqua/projects")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_login_session_and_logout(monkeypatch: Any) -> None:
    async def authenticate(_client: AquaClient, username: str, password: str) -> None:
        assert username == "alice"
        assert password == "secret"

    monkeypatch.setattr(AquaClient, "authenticate", authenticate)

    with TestClient(create_app()) as client:
        initial = client.get("/api/v1/auth/session")
        login = client.post(
            "/api/v1/auth/login",
            json={"username": "alice", "password": "secret"},
        )
        session = client.get("/api/v1/auth/session")
        csrf_token = session.json()["csrfToken"]
        rejected_logout = client.post("/api/v1/auth/logout")
        logout = client.post(
            "/api/v1/auth/logout", headers={"X-CSRF-Token": csrf_token}
        )
        final = client.get("/api/v1/auth/session")

    assert initial.json() == {"authenticated": False}
    assert login.status_code == 200
    assert login.json()["authenticated"] is True
    assert "h2orb_session=" in login.headers["set-cookie"]
    assert "HttpOnly" in login.headers["set-cookie"]
    assert "SameSite=strict" in login.headers["set-cookie"]
    assert session.json()["authenticated"] is True
    assert rejected_logout.status_code == 403
    assert logout.json() == {"authenticated": False}
    assert final.json() == {"authenticated": False}


def test_aqua_client_does_not_retain_password() -> None:
    async def exercise() -> None:
        settings = Settings(aqua_base_url="https://aqua.example.test/")
        with respx.mock(base_url="https://aqua.example.test/") as router:
            token_request = router.post("api/token").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "access_token": "access-token",
                        "refresh_token": "refresh-token",
                        "expires_in": 300,
                    },
                )
            )
            router.delete("api/Session").mock(return_value=httpx.Response(204))
            client = AquaClient(settings)
            await client.authenticate("alice", "top-secret")

            assert token_request.called
            assert not hasattr(client, "_username")
            assert not hasattr(client, "_password")
            assert "top-secret" not in repr(client)
            await client.close()

    asyncio.run(exercise())


def test_failed_logins_are_rate_limited(monkeypatch: Any) -> None:
    async def reject(_client: AquaClient, _username: str, _password: str) -> None:
        raise AquaAuthenticationError("internal AQUA detail")

    monkeypatch.setattr(AquaClient, "authenticate", reject)

    with TestClient(create_app()) as client:
        responses = [
            client.post(
                "/api/v1/auth/login",
                json={"username": "alice", "password": "wrong"},
            )
            for _ in range(6)
        ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401, 401, 429]
    assert all("internal AQUA detail" not in response.text for response in responses)
