# Using grpcurl with yfinance-grpc

The server has gRPC reflection enabled, so [grpcurl](https://github.com/fullstorydev/grpcurl) works without proto files. All examples assume the server is running on `localhost:50059` (`make run` or `make up`).

## Install grpcurl

```bash
brew install grpcurl                                          # macOS
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest # anywhere with Go
```

Linux binaries are on the [releases page](https://github.com/fullstorydev/grpcurl/releases).

## Discover the API

```bash
grpcurl -plaintext localhost:50059 list
```

```
grpc.reflection.v1alpha.ServerReflection
yfinance_grpc.v1alpha1.MarketService
yfinance_grpc.v1alpha1.SearchService
yfinance_grpc.v1alpha1.SectorService
yfinance_grpc.v1alpha1.TickerService
```

```bash
# Methods of one service
grpcurl -plaintext localhost:50059 list yfinance_grpc.v1alpha1.TickerService

# Full service definition, including request/response types
grpcurl -plaintext localhost:50059 describe yfinance_grpc.v1alpha1.TickerService

# One message type
grpcurl -plaintext localhost:50059 describe yfinance_grpc.v1alpha1.GetHistoryRequest
```

Python's reflection service cannot resolve individual methods, so `describe Service.Method` fails with "Symbol not found". Describe the service or the message instead.

Field names in `-d` JSON may be written as in the proto (`max_results`) or in lowerCamelCase (`maxResults`).

## TickerService

```bash
# Company info and fast price snapshot
grpcurl -plaintext -d '{"ticker": "AAPL"}' localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetInfo
grpcurl -plaintext -d '{"ticker": "AAPL"}' localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetFastInfo

# Several tickers at once
grpcurl -plaintext -d '{"tickers": ["AAPL", "MSFT", "GOOGL"]}' \
  localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetMultipleInfo

# Price history by period, or by date range
grpcurl -plaintext -d '{"ticker": "AAPL", "period": "1mo", "interval": "1d"}' \
  localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetHistory
grpcurl -plaintext -d '{"ticker": "AAPL", "start": "2025-01-01T00:00:00Z", "end": "2025-02-01T00:00:00Z"}' \
  localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetHistory

# Financial statements: freq is "yearly" (default), "quarterly" or "trailing"
grpcurl -plaintext -d '{"ticker": "AAPL", "freq": "quarterly"}' \
  localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetFinancials

# Options: list expirations, then fetch one chain
grpcurl -plaintext -d '{"ticker": "AAPL"}' localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetOptions
grpcurl -plaintext -d '{"ticker": "AAPL", "date": "2026-12-18"}' \
  localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetOptionChain

# News, holders, analyst data
grpcurl -plaintext -d '{"ticker": "AAPL", "count": 5}' localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetNews
grpcurl -plaintext -d '{"ticker": "AAPL"}' localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetInstitutionalHolders
grpcurl -plaintext -d '{"ticker": "AAPL"}' localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetAnalystPriceTargets
```

### Streaming history for many tickers

`DownloadHistory` is server-streaming: each response message carries up to 500 rows for one ticker. Pass one symbol per list entry. `["AAPL MSFT"]` is rejected with `INVALID_ARGUMENT`.

```bash
grpcurl -plaintext -v -d '{"tickers": ["AAPL", "MSFT", "NOPE_XYZ"], "period": "5d", "interval": "1d"}' \
  localhost:50059 yfinance_grpc.v1alpha1.TickerService/DownloadHistory
```

With `-v`, the trailers at the end list symbols that returned no data:

```
Response trailers received:
missing-tickers: NOPE_XYZ
```

If none of the symbols has data, the call fails with `NOT_FOUND` instead.

## SearchService

```bash
# Quotes and news matching a query
grpcurl -plaintext -d '{"query": "Apple", "max_results": 5}' \
  localhost:50059 yfinance_grpc.v1alpha1.SearchService/Search

# Instruments of one type: LOOKUP_TYPE_EQUITY, _ETF, _INDEX, _FUTURE, _CURRENCY, _CRYPTOCURRENCY, _MUTUALFUND
grpcurl -plaintext -d '{"query": "S&P 500", "type": "LOOKUP_TYPE_ETF", "count": 5}' \
  localhost:50059 yfinance_grpc.v1alpha1.SearchService/Lookup
```

## MarketService

```bash
grpcurl -plaintext -d '{"market": "US"}' localhost:50059 yfinance_grpc.v1alpha1.MarketService/GetMarketStatus
grpcurl -plaintext -d '{"market": "US"}' localhost:50059 yfinance_grpc.v1alpha1.MarketService/GetMarketSummary
```

## SectorService

```bash
grpcurl -plaintext -d '{"key": "technology"}' localhost:50059 yfinance_grpc.v1alpha1.SectorService/GetSector
grpcurl -plaintext -d '{"key": "consumer-electronics"}' \
  localhost:50059 yfinance_grpc.v1alpha1.SectorService/GetIndustry
```

## Errors

Failures come back as gRPC status codes (see [Errors in the RPC reference](rpc-reference.md#errors)):

```bash
grpcurl -plaintext -d '{"ticker": ""}' localhost:50059 yfinance_grpc.v1alpha1.TickerService/GetInfo
```

```
ERROR:
  Code: InvalidArgument
  Message: ticker must not be empty
```
