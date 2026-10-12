from __future__ import annotations

from fastapi import Request

from h2orb.aqua.client import AquaClient


def get_aqua_client(request: Request) -> AquaClient:
    return request.app.state.aqua_client

