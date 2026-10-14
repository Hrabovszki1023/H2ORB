from __future__ import annotations

import asyncio
import getpass

from h2orb.aqua.client import AquaClient
from h2orb.config import get_settings


async def check_connection() -> int:
    client = AquaClient(get_settings())
    try:
        username = input("AQUA username: ").strip()
        password = getpass.getpass("AQUA password: ")
        await client.authenticate(username, password)
        data = await client.get_project_tree([], include_projects=True)
        project_count = len(data.get("Projects") or [])
        print(f"AQUA connection successful; visible projects: {project_count}")
        return 0
    finally:
        await client.close()


def main() -> None:
    raise SystemExit(asyncio.run(check_connection()))


if __name__ == "__main__":
    main()
