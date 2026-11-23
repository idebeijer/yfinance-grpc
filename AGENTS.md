# AGENTS.md

`yfinance-grpc` serves the [yfinance](https://github.com/ranaroussi/yfinance) library over gRPC (port 50059, reflection on). The `.proto` files in `api/proto/yfinance_grpc/v1alpha1/` are the contract; `src/yfinance_grpc_server/` implements it. `make help` lists every command, and `make check` is the gate: run it before calling work done.

## Conventions

- **Generated code is output.** `gen/` comes from `buf generate`. Edit the `.proto`, regenerate, and commit the regenerated `gen/` with it; CI fails when they drift. Run `make breaking` after proto edits.
- **Proto package is `yfinance_grpc`**, not `yfinance`, so the generated Python package cannot shadow the yfinance library. RPCs use `Get<Entity>Request` / `Get<Entity>Response` (buf lint enforces it).
- **Every servicer method is `@rpc`-decorated** (`errors.py`). Handlers raise `invalid_argument(...)`, `not_found(...)` or `unimplemented(...)`, or let exceptions propagate; `@rpc` maps them to status codes, so handlers never call `context.set_code` or `context.abort`. Validate a required string with `require(value, "field")`; single-ticker handlers get their `yf.Ticker` from `_ticker(request)`, which does this.
- **Missing data is the zero value, not an error.** Route every yfinance/pandas value through `convert.py` (`safe_float`, `safe_int`, `safe_str`, `to_timestamp`); yfinance returns NaN, `pd.NA`, `NaT`, `None` and `datetime.date` freely and protobuf rejects them. An RPC with nothing to report returns `OK` and an empty response.
- **Partial success is reported in trailing metadata.** Multi-ticker RPCs list failed symbols in `missing-tickers` (`MISSING_TICKERS_KEY`).
- **The status-code contract lives in `docs/rpc-reference.md#errors`.** Change it there when a handler's error behaviour changes, alongside the RPC's row in the table.

## Testing

Unit tests call servicers directly with a `Mock()` context and patch yfinance where the module looks it up (`yfinance_grpc_server.ticker.yf.Ticker`). Assert failures on `context.abort`. A mock `abort` returns instead of raising, so the handler returns `None`. `test_integration.py` carries the `integration` marker, is deselected by default, and needs `make run` plus network access.

## Gotchas

- **yfinance renames DataFrame columns silently** (`% Out` became `pctHeld`; `Ticker.earnings` now always returns `None`). A wrong column name reads as missing data and yields zeros, with no test failure against mocks. When bumping yfinance, check the column names each handler reads against the installed source in `.venv/lib/python3.14/site-packages/yfinance/`, and run the integration tests.
- **The protobuf runtime and the buf Python plugins move together.** `protobuf` 7.36 needs `buf.build/protocolbuffers/python:v36.x` (and `pyi`) in `buf.gen.yaml`; grpcio-reflection pins the protobuf major. Bump both, then `make generate`.
- **`astral-sh/setup-uv` publishes no floating major tag.** Pin it to a commit SHA with the version in a comment, as `release.yml` does for every action.
- **Python gRPC reflection cannot resolve method symbols**, so `grpcurl describe Service.Method` fails. Describe the service or the message.
