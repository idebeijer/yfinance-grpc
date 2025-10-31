# Build stage
FROM python:3.14-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install Python dependencies
COPY pyproject.toml ./
RUN uv pip install --python=/usr/local/bin/python3.14 --target=/app/deps -r pyproject.toml

# Final stage
FROM python:3.14-alpine

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache libstdc++ && \
    adduser -D -u 1000 appuser

# Copy dependencies and code
COPY --from=builder /app/deps /app/deps
COPY gen/ ./gen/
COPY server.py main.py ./

ENV PYTHONPATH=/app/deps
ENV PYTHONUNBUFFERED=1

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 50059

CMD ["python", "main.py"]
