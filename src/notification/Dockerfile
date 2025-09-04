# Stage 1: Build Stage (deps only)
FROM python:3.12-alpine AS builder

# Copy uv binary (pinned for smaller size; adjust version as needed)
COPY --from=ghcr.io/astral-sh/uv:0.4.18 /uv /usr/local/bin/uv

WORKDIR /app

# Copy lockfiles first for layer caching
COPY pyproject.toml uv.lock ./

# Force uv to use system Python and create fresh venv
ENV UV_PYTHON=/usr/local/bin/python3 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_PYTHON_PREFERENCE=only-system \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN uv venv /app/.venv && \
    uv sync --frozen --no-install-project --compile-bytecode --no-cache

# Stage 2: Runtime Stage
FROM python:3.12-alpine

# Install system dependencies for moviepy/ffmpeg (Alpine equivalents)
RUN apk add --no-cache \
    ffmpeg \
    libsm \
    libxext \
    libxrender

WORKDIR /app

# Copy only the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
# Copy application code
COPY consumer.py main.py ./
COPY send ./send

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN adduser -D appuser && \
    chown -R appuser:appuser /app

USER appuser

# Run consumer
CMD ["/app/.venv/bin/python", "consumer.py"]