# Build stage: resolve dependencies from uv.lock into a self-contained venv.
FROM python:3.14-alpine AS builder

RUN apk add --no-cache gcc musl-dev libffi-dev

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies first, so source edits reuse this layer.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project

COPY gen/yfinance_grpc gen/yfinance_grpc
COPY src src
RUN uv sync --locked --no-dev --no-editable

# Runtime stage
FROM python:3.14-alpine

RUN apk add --no-cache libstdc++ && \
    adduser -D -u 1000 appuser

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 50059

CMD ["yfinance-grpc"]
