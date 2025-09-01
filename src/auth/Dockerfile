# Stage 1: Build stage
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy only dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Force uv to use Python 3.12 from the base image
ENV UV_PYTHON=/usr/local/bin/python3 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Install dependencies in a virtual environment
RUN uv sync --frozen --no-install-project

# Stage 2: Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy only the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code (changes frequently, so after .venv)
COPY models.py schema.py server.py init.sql ./

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8001

# Run the app
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]