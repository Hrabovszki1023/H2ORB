from __future__ import annotations

import uvicorn

from h2orb.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "h2orb.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()

