# Stage 1: Build Stage (deps only)
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

# Force uv to use system Python and create fresh venv
ENV UV_PYTHON=/usr/local/bin/python3 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_PYTHON_PREFERENCE=only-system

RUN uv venv /app/.venv && uv sync --frozen --no-install-project --compile-bytecode


# Stage 2: Runtime Stage
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY . .

ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UVICORN_WORKERS=2

RUN useradd -m appuser
USER appuser

EXPOSE 8002

CMD ["/app/.venv/bin/python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "2"]
