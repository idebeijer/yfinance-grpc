# Testing Guide

This project includes comprehensive unit and integration tests for the yfinance-grpc service.

## Test Structure

- `tests/test_server.py` - Unit tests that mock yfinance calls
- `tests/test_integration.py` - Integration tests that require a running server

## Running Tests

### Install Test Dependencies

```bash
uv sync --extra dev
# or
uv add --dev pytest pytest-mock
```

### Run Unit Tests

Unit tests don't require a running server and use mocking:

```bash
make test-unit
```

### Run Integration Tests

Integration tests require the server to be running:

```bash
# Terminal 1: Start the server
make run

# Terminal 2: Run integration tests
make test-integration
```

### Run All Tests

```bash
make test-all
```

### Run Specific Test Classes or Methods

```bash
# Run a specific test file
uv run pytest tests/test_server.py -v

# Run a specific test class
uv run pytest tests/test_server.py::TestTickerServiceGetInfo -v

# Run a specific test method
uv run pytest tests/test_server.py::TestTickerServiceGetInfo::test_get_info_success -v
```

## Writing New Tests

### Unit Test Example

```python
@patch('src.server.yf.Ticker')
def test_new_endpoint(self, mock_ticker_class):
    """Test description"""
    # Setup mock
    mock_ticker = Mock()
    mock_ticker_class.return_value = mock_ticker
    mock_ticker.some_method.return_value = "data"

    # Create servicer and call
    servicer = TickerServiceServicer()
    context = Mock()
    request = ticker_pb2.SomeRequest(ticker="AAPL")

    response = servicer.SomeMethod(request, context)

    # Assertions
    assert response.some_field == "expected"
```

### Integration Test Example

```python
def test_new_endpoint_integration(self, stub):
    """Test description"""
    request = ticker_pb2.SomeRequest(ticker="AAPL")
    response = stub.SomeMethod(request)

    assert len(response.items) > 0
    assert response.items[0].field == "expected"
```
