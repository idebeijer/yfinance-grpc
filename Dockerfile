# Build stage: resolve dependencies from uv.lock into a venv built against
# Debian 13's system Python, the same interpreter (/usr/bin/python3.13) the
# distroless runtime ships, so the venv's python symlink resolves there too.
FROM debian:13-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=/usr/bin/python3.13

WORKDIR /app

# Dependencies first, so source edits reuse this layer.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project

COPY gen/yfinance_grpc gen/yfinance_grpc
COPY src src
RUN uv sync --locked --no-dev --no-editable

# Runtime stage: no shell, no package manager; runs as uid 65532 (nonroot).
FROM gcr.io/distroless/python3-debian13:nonroot

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 50059

ENTRYPOINT ["/app/.venv/bin/yfinance-grpc"]
