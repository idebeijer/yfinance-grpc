# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`yfinance-grpc` is a Python gRPC server that wraps the [yfinance](https://github.com/ranaroussi/yfinance) library, exposing Yahoo Finance data to any gRPC-capable client. The server listens on port 50059 and includes gRPC reflection for easy discovery.

## Common Commands

```bash
# Install dependencies
uv sync

# Run the server
uv run python -m src.main
# or
make run

# Run unit tests (no server required)
uv run pytest tests/test_server.py -v

# Run integration tests (requires running server on :50059)
uv run pytest tests/test_integration.py -v

# Run all tests
make test-all

# Regenerate protobuf code from .proto files
buf generate
# or
make generate

# Lint proto files
buf lint

# Check for breaking proto changes
buf breaking --against '.git#branch=main'

# Format proto files
buf format api -w

# Docker
make up      # docker-compose up -d
make down    # docker-compose down
```

## Architecture

```
api/proto/yfinance_grpc/v1/ticker.proto  # API contract (single TickerService)
gen/yfinance_grpc/v1/                    # Generated protobuf/gRPC Python code (do not edit)
src/server.py                            # TickerServiceServicer — all RPC implementations
src/main.py                              # Entry point: starts server on port 50059
tests/test_server.py                     # Unit tests (mock yfinance)
tests/test_integration.py               # Integration tests (live server)
```

**Data flow**: gRPC client → `src/server.py` (TickerServiceServicer) → yfinance library → Yahoo Finance HTTP API

**Proto management**: Buf is used for linting, code generation, and breaking change detection. Config in `buf.yaml` and `buf.gen.yaml`. Generated code goes to `gen/`.

## Key Implementation Details

`src/server.py` contains the full `TickerServiceServicer` with 19 RPC methods and several helper utilities:

- `safe_float()`, `safe_int()`, `safe_str()`: Handle NaN/None values from yfinance (pandas DataFrames frequently produce these)
- `datetime_to_timestamp()`: Converts Python datetime to protobuf `Timestamp`
- `create_ticker_info()`: Maps yfinance's info dict to the `TickerInfo` protobuf message

`DownloadHistory` is the only server-streaming RPC — it yields `HistoryBar` messages rather than returning a single response.

## Proto Conventions

Lint rules enforce: `STANDARD`, `FILE_LOWER_SNAKE_CASE`, `RPC_REQUEST_STANDARD_NAME`, `RPC_RESPONSE_STANDARD_NAME`. All new RPCs must follow the `Get<Entity>Request` / `Get<Entity>Response` naming pattern.

## Testing

Unit tests mock `yfinance.Ticker` via `pytest-mock`. Integration tests connect to a live server — start the server first with `make run` or `make up`.
