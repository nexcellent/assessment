# syntax=docker/dockerfile:1
# Build context is the repository root: the image needs backend/ and fixtures/.
FROM python:3.13-slim-trixie AS base

# The uv that wrote uv.lock, so the lockfile format matches.
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock backend/.python-version ./

# --- Checks: the full environment with the sources and tests ------------------
# `docker compose run --build --rm backend-checks`
FROM base AS checks
RUN uv sync --frozen
COPY backend/ ./
COPY fixtures/ /app/fixtures/
CMD ["sh", "-c", "uv run --no-sync ruff check . && uv run --no-sync mypy app && uv run --no-sync pytest && uv run --no-sync ruff format --check ."]

# --- Runtime: dependencies only, no dev tools --------------------------------
FROM base AS runtime
RUN uv sync --frozen --no-dev
COPY backend/app ./app
COPY fixtures/ /app/fixtures/

ENV PATH="/app/backend/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
