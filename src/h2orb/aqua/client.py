from __future__ import annotations

import asyncio
import json
import ssl
import time
from dataclasses import dataclass
from typing import Any

import httpx

from h2orb.config import Settings


class AquaApiError(RuntimeError):
    """Raised when AQUA cannot fulfil a request."""


class AquaConfigurationError(RuntimeError):
    """Raised when required AQUA connection settings are missing."""


@dataclass(slots=True)
class _OAuthToken:
    access_token: str
    refresh_token: str | None
    expires_at: float

    def is_valid(self) -> bool:
        return time.monotonic() < self.expires_at


class AquaClient:
    """Shared asynchronous AQUA client safe for concurrent application requests.

    Endpoint-specific methods are added after mapping the v26.29.0.0 Swagger document.
    Keeping raw requests private prevents AQUA transport details leaking into services.
    """

    def __init__(self, settings: Settings) -> None:
        self._username = settings.aqua_username
        self._password = settings.aqua_password
        self._token: _OAuthToken | None = None
        self._token_lock = asyncio.Lock()
        verify: bool | ssl.SSLContext = settings.aqua_verify_tls
        if settings.aqua_verify_tls and settings.aqua_ca_bundle is not None:
            verify = ssl.create_default_context(cafile=str(settings.aqua_ca_bundle))
        self._client = httpx.AsyncClient(
            base_url=str(settings.aqua_base_url).rstrip("/") + "/",
            verify=verify,
            timeout=httpx.Timeout(settings.aqua_timeout_seconds),
            limits=httpx.Limits(
                max_connections=settings.aqua_max_connections,
                max_keepalive_connections=settings.aqua_max_connections,
            ),
            headers={"Accept": "application/json"},
            trust_env=False,
        )

    async def close(self) -> None:
        try:
            if self._token is not None:
                await self._client.delete(
                    "api/Session",
                    headers={"Authorization": f"Bearer {self._token.access_token}"},
                )
        except httpx.HTTPError:
            pass
        finally:
            self._token = None
            await self._client.aclose()

    async def get_project_tree(
        self,
        parent_folders: list[str],
        *,
        include_projects: bool = False,
        include_archived: bool = False,
    ) -> dict[str, Any]:
        return await self._get(
            "api/Navigation/Tree",
            parentFolders=json.dumps(parent_folders),
            includeProjects=include_projects,
            includeArchived=include_archived,
        )

    async def get_test_scenarios(
        self,
        project_id: int,
        folder_id: int = 0,
        *,
        include_subfolders: bool = True,
        start_at: int = 0,
        max_results: int = 50,
    ) -> dict[str, Any]:
        return await self._get(
            "api/TestScenario/ItemList",
            projectId=project_id,
            folderId=folder_id,
            includeSubfolders=include_subfolders,
            includeArchived=False,
            startAt=start_at,
            maxResults=max_results,
        )

    async def get_all_test_scenarios(
        self,
        project_id: int,
        folder_id: int = 0,
        *,
        include_subfolders: bool = True,
        page_size: int = 200,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        start_at = 0
        while True:
            page = await self.get_test_scenarios(
                project_id,
                folder_id,
                include_subfolders=include_subfolders,
                start_at=start_at,
                max_results=page_size,
            )
            page_items = page.get("Items") or []
            items.extend(page_items)
            total = int(page.get("Count", len(items)))
            if not page_items or len(items) >= total:
                return items
            start_at += len(page_items)

    async def get_test_jobs(self, scenario_id: int) -> list[dict[str, Any]]:
        return await self._get(f"api/TestScenario/{scenario_id}/TestJob")

    async def get_scenario_executions(
        self,
        scenario_id: int,
        *,
        start_at: int = 0,
        max_results: int = 100,
    ) -> dict[str, Any]:
        return await self._get(
            f"api/TestScenario/{scenario_id}/Execution",
            startAt=start_at,
            maxResults=max_results,
            orderBy="ExecutionDate DESC",
            includeStatistics=True,
        )

    async def get_all_scenario_executions(
        self, scenario_id: int, *, page_size: int = 200
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        start_at = 0
        while True:
            page = await self.get_scenario_executions(
                scenario_id, start_at=start_at, max_results=page_size
            )
            page_items = page.get("Items") or []
            items.extend(item for item in page_items if not item.get("Irrelevant"))
            total = int(page.get("Count", len(items)))
            if not page_items or start_at + len(page_items) >= total:
                return items
            start_at += len(page_items)

    async def get_test_execution(self, execution_id: int) -> dict[str, Any]:
        return await self._get(
            f"api/TestExecution/{execution_id}",
            richTextFormatToInclude="None",
        )

    async def get_defect(
        self, defect_id: int, *, with_enclosure: bool = False
    ) -> dict[str, Any]:
        return await self._get(
            f"api/Defect/{defect_id}",
            withEnclosure=with_enclosure,
        )

    async def get_execution_relations(self, execution_id: int) -> dict[str, Any]:
        return await self._get(f"api/TestExecution/{execution_id}/Relation")

    async def _get(self, path: str, **params: Any) -> Any:
        return await self._request("GET", path, params=params or None)

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        token = await self._access_token()
        try:
            response = await self._client.request(
                method,
                path,
                headers={"Authorization": f"Bearer {token}"},
                **kwargs,
            )
            if response.status_code == httpx.codes.UNAUTHORIZED:
                self._token = None
                token = await self._access_token()
                response = await self._client.request(
                    method,
                    path,
                    headers={"Authorization": f"Bearer {token}"},
                    **kwargs,
                )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            status = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
            suffix = f" with status {status}" if status is not None else ""
            raise AquaApiError(f"AQUA request failed{suffix}") from exc
        return response.json()

    async def _access_token(self) -> str:
        if self._token is not None and self._token.is_valid():
            return self._token.access_token

        async with self._token_lock:
            if self._token is not None and self._token.is_valid():
                return self._token.access_token
            self._token = await self._request_token()
            return self._token.access_token

    async def _request_token(self) -> _OAuthToken:
        if not self._username or not self._password:
            raise AquaConfigurationError(
                "ARB_AQUA_USERNAME and ARB_AQUA_PASSWORD must be configured"
            )

        try:
            response = await self._client.post(
                "api/token",
                data={
                    "grant_type": "password",
                    "username": self._username,
                    "password": self._password,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            payload = response.json()
            access_token = payload["access_token"]
        except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
            raise AquaApiError("AQUA authentication failed") from exc

        expires_in = max(float(payload.get("expires_in", 300)), 1.0)
        return _OAuthToken(
            access_token=access_token,
            refresh_token=payload.get("refresh_token"),
            expires_at=time.monotonic() + max(expires_in - 30.0, 1.0),
        )
