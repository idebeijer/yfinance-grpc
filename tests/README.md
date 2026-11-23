# Tests

| File | Covers | Needs |
|------|--------|-------|
| `test_convert.py`, `test_errors.py` | Shared value conversion and status-code mapping | nothing |
| `test_ticker.py`, `test_search.py`, `test_market.py`, `test_sector.py` | One servicer each, yfinance mocked | nothing |
| `test_integration.py` | Every service over a real gRPC channel | a server on `localhost:50059` and network access |

```bash
make test               # unit tests (the default `pytest` run)
make test-integration   # integration tests; start the server first with `make run`
make test-all           # both
uv run pytest tests/test_ticker.py -k GetInfo   # a subset
```

Integration tests carry the `integration` marker, and `pyproject.toml` deselects that marker by default (`-m "not integration"`).

## Writing unit tests

Patch yfinance where the servicer module looks it up, call the servicer directly with a `Mock()` context, and assert on the response, or on `context.abort` for failures:

```python
from unittest.mock import ANY, Mock, patch

import grpc
from yfinance_grpc.v1alpha1 import ticker_pb2

from yfinance_grpc_server.ticker import TickerServiceServicer


@patch("yfinance_grpc_server.ticker.yf.Ticker")
def test_get_isin(mock_ticker_class):
    mock_ticker_class.return_value.get_isin.return_value = "US0378331005"

    response = TickerServiceServicer().GetIsin(ticker_pb2.GetIsinRequest(ticker="AAPL"), Mock())

    assert response.isin == "US0378331005"


def test_get_isin_empty_ticker():
    context = Mock()
    TickerServiceServicer().GetIsin(ticker_pb2.GetIsinRequest(ticker=""), context)
    context.abort.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT, ANY)
```

A real `ServicerContext.abort` raises; a `Mock()` one returns, so the call above returns `None` after aborting. Tests that need the real control flow give the mock `abort.side_effect` (see `test_errors.py`).
