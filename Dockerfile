FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN python -m pip wheel --wheel-dir /wheels .


FROM builder AS verify

COPY tests ./tests

RUN python -m pip install ".[dev]" \
    && python -m pytest -p no:asyncio \
    && python -m ruff check .


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    ARB_HOST=0.0.0.0 \
    ARB_PORT=8000

RUN groupadd --system h2orb \
    && useradd --system --gid h2orb --create-home --home-dir /home/h2orb h2orb

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN python -m pip install /wheels/*.whl \
    && rm -rf /wheels

USER h2orb

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"]

CMD ["python", "-m", "h2orb"]
