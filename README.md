# yfinance-grpc

A gRPC server wrapper around the [yfinance](https://github.com/ranaroussi/yfinance) Python library, enabling access to Yahoo Finance data from any programming language that supports gRPC.

## Why?

The yfinance library is excellent for accessing Yahoo Finance data in Python, but if you're working in other languages like Go, Rust, Java, or C#, you need to either find an alternative library (which may not exist or be maintained) or implement your own Yahoo Finance client.

This project solves that problem by wrapping yfinance in a gRPC service, allowing you to:

- Access Yahoo Finance data from **any language** that supports gRPC
- Maintain a **single source of truth** for Yahoo Finance data across your microservices
- Use strongly-typed protocol buffers for data exchange

## Features

The server exposes 44 RPCs across four gRPC services currently covering a subset of the yfinance API (more to come). See [docs/rpc-reference.md](docs/rpc-reference.md) for a complete mapping to yfinance methods.

### Ticker Information

- **GetInfo**: Comprehensive ticker information (price, market cap, P/E, dividends, targets, etc.)
- **GetFastInfo**: Lightweight price/market snapshot — faster than `GetInfo`
- **GetMultipleInfo**: Bulk info fetch for multiple tickers in one call
- **GetIsin**: ISIN code for a ticker
- **GetHistoryMetadata**: Exchange metadata, valid intervals, timezone info

### Price History

- **GetHistory**: Historical OHLCV data with configurable period, interval and adjustments
- **DownloadHistory**: Stream historical data for multiple tickers (server-streaming RPC); symbols without data are reported in `missing-tickers` trailing metadata

### Corporate Actions

- **GetDividends**: Dividend payment history
- **GetSplits**: Stock split history
- **GetCapitalGains**: Capital gains distributions (ETFs/funds)
- **GetActions**: All corporate actions combined (dividends, splits, capital gains)

### Financial Statements

- **GetFinancials**: Income statements (yearly/quarterly/trailing)
- **GetBalanceSheet**: Balance sheet data
- **GetCashFlow**: Cash flow statements
- **GetEarnings**: *Deprecated*, always returns `UNIMPLEMENTED` (Yahoo Finance dropped this data; use `GetFinancials` or `GetEarningsHistory`)

### Analyst Data & Estimates

- **GetRecommendations**: Individual analyst upgrades/downgrades with firm and grade
- **GetRecommendationsSummary**: Period-based aggregated counts (strongBuy/buy/hold/sell/strongSell)
- **GetAnalystPriceTargets**: Consensus price target (current/low/high/mean/median)
- **GetEarningsEstimate**: Forward EPS estimates by period (0q/+1q/0y/+1y)
- **GetRevenueEstimate**: Forward revenue estimates by period
- **GetEarningsHistory**: Historical EPS actuals vs estimates with surprise %
- **GetEpsTrend**: EPS estimate trend across 7/30/60/90-day revision windows
- **GetEpsRevisions**: Counts of upward/downward EPS revisions
- **GetGrowthEstimates**: Growth estimates for stock, industry, sector and index

### Calendar & Events

- **GetCalendar**: Upcoming earnings dates and ex-dividend dates
- **GetEarningsDates**: Past and upcoming earnings dates with EPS data

### Options

- **GetOptions**: Available option expiration dates
- **GetOptionChain**: Full option chain (calls and puts) for a specific expiration

### Ownership

- **GetMajorHolders**: Major holder breakdown (% held by insiders, institutions, etc.)
- **GetInstitutionalHolders**: Institutional ownership with shares, value, and date reported
- **GetMutualFundHolders**: Mutual fund ownership data
- **GetInsiderPurchases**: Summary table of insider buying/selling activity
- **GetInsiderTransactions**: Individual insider transaction records
- **GetInsiderRosterHolders**: Roster of current insider holders with positions

### ESG & Filings

- **GetSustainability**: ESG scores (environment, social, governance) and 15 controversy flags
- **GetSecFilings**: SEC filing history (10-K, 10-Q, 8-K, etc.)

### Shares

- **GetSharesHistory**: Full history of shares outstanding

### Search & Lookup (SearchService)

- **Search**: Full-text search returning matching quotes (symbol, name, exchange, sector, score) and news articles
- **Lookup**: Typed instrument lookup filtered by class — equity, ETF, index, future, currency, cryptocurrency, or mutual fund

### Market (MarketService)

- **GetMarketStatus**: Current session type (REGULAR/PRE/POST), open/close timestamps and timezone for a market (e.g. `US`, `GB`)
- **GetMarketSummary**: Price snapshot of major instruments in a market — price, change and change %

### Sector & Industry (SectorService)

- **GetSector**: Sector overview, top companies, top ETFs, top mutual funds, and list of constituent industries (e.g. key `technology`)
- **GetIndustry**: Industry overview, top companies, top performing companies (YTD return/last price/target price) and top growth companies (e.g. key `consumer-electronics`)

## Quick Start

### Using Docker (Recommended)

```bash
docker compose up -d      # or: make up
docker compose logs -f    # or: make logs
```

Or use the published image:

```bash
docker run -p 50059:50059 ghcr.io/idebeijer/yfinance-grpc:latest
```

The server listens on `localhost:50059`.

### From Source

Prerequisites: Python 3.14+ and [uv](https://github.com/astral-sh/uv). The generated protobuf code is committed, so [buf](https://buf.build/) is only needed if you change the `.proto` files.

```bash
git clone https://github.com/idebeijer/yfinance-grpc.git
cd yfinance-grpc
uv sync        # or: make install
make run       # or: uv run yfinance-grpc
```

Run `make help` to see every available target.

## Usage

### Starting the Server

```bash
uv run yfinance-grpc                      # or: make run
uv run yfinance-grpc --port 6000 --log-level debug
```

| Flag | Environment variable | Default |
|------|----------------------|---------|
| `--port` | `PORT` | `50059` |
| `--log-level` | `LOG_LEVEL` | `INFO` |
| `--max-workers` | — | `10` |

### Running the Python Client Example

With the server running:

```bash
uv run python examples/client_example.py
# or
make example
```

This demonstrates:

- Fetching ticker information
- Getting historical data
- Retrieving dividends and news
- Accessing option chains

### Using with grpcurl (Reflection Enabled)

The server supports gRPC reflection, so you can use `grpcurl` without proto files:

```bash
# List all services
grpcurl -plaintext localhost:50059 list

# List methods on a service
grpcurl -plaintext localhost:50059 list yfinance_grpc.v1alpha1.TickerService

# Get ticker info
grpcurl -plaintext -d '{"ticker": "AAPL"}' \
  localhost:50059 yfinance_grpc.v1alpha1.TickerService.GetInfo

# Get historical data
grpcurl -plaintext -d '{"ticker": "AAPL", "period": "5d", "interval": "1d"}' \
  localhost:50059 yfinance_grpc.v1alpha1.TickerService.GetHistory

# Search for a symbol
grpcurl -plaintext -d '{"query": "Apple", "max_results": 5}' \
  localhost:50059 yfinance_grpc.v1alpha1.SearchService.Search

# Get market status
grpcurl -plaintext -d '{"market": "US"}' \
  localhost:50059 yfinance_grpc.v1alpha1.MarketService.GetMarketStatus

# Get sector overview
grpcurl -plaintext -d '{"key": "technology"}' \
  localhost:50059 yfinance_grpc.v1alpha1.SectorService.GetSector
```

See [docs/grpcurl.md](docs/grpcurl.md) for more examples.

### Client Examples

#### Python

A full Python client example covering all four services is in [`examples/client_example.py`](examples/client_example.py):

```bash
uv run python examples/client_example.py
```

#### Go

A runnable Go client example covering all four services is in [`examples/go/main.go`](examples/go/main.go). Pre-generated Go bindings are already included in `gen/go/` — no need to run `buf generate`.

```bash
cd examples/go
go mod tidy
go run main.go
```

The Go client uses the generated package at `github.com/idebeijer/yfinance-grpc/gen/go/yfinance_grpc/v1alpha1`. To use the generated bindings in your own Go project:

```go
package main

import (
    "context"
    "fmt"
    "log"

    pb "github.com/idebeijer/yfinance-grpc/gen/go/yfinance_grpc/v1alpha1"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
)

func main() {
    conn, err := grpc.NewClient("localhost:50059",
        grpc.WithTransportCredentials(insecure.NewCredentials()))
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()

    client := pb.NewTickerServiceClient(conn)
    resp, err := client.GetInfo(context.Background(), &pb.GetInfoRequest{Ticker: "AAPL"})
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Price: $%.2f\n", resp.Info.CurrentPrice)
}
```

#### Node.js

```bash
npm install @grpc/grpc-js @grpc/proto-loader
```

Copy `api/proto` from this repository into your project, then load every service:

```javascript
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");

const packageDefinition = protoLoader.loadSync(
  ["ticker.proto", "search.proto", "market.proto", "sector.proto"].map(
    (f) => `yfinance_grpc/v1alpha1/${f}`,
  ),
  { includeDirs: [`${__dirname}/api/proto`] },
);
const proto = grpc.loadPackageDefinition(packageDefinition).yfinance_grpc.v1alpha1;

const ticker = new proto.TickerService("localhost:50059", grpc.credentials.createInsecure());

ticker.getInfo({ ticker: "AAPL" }, (error, response) => {
  if (error) throw error;
  console.log(`Price: $${response.info.currentPrice}`);
});
```

## API Documentation

See [docs/rpc-reference.md](docs/rpc-reference.md) for a full mapping of every RPC to its yfinance equivalent, parameters, return type and error codes.

The complete protobuf definitions are in `api/proto/yfinance_grpc/v1alpha1/`.

## Development

### Layout

```
api/proto/yfinance_grpc/v1alpha1/   Proto definitions (the API contract)
gen/                                Generated code (buf generate; do not edit)
src/yfinance_grpc_server/           Server package
  ticker.py search.py market.py sector.py   One servicer per service
  convert.py                        yfinance/pandas values -> protobuf values
  errors.py                         @rpc decorator: exceptions -> gRPC status codes
  server.py  __main__.py            Server wiring and CLI entry point
tests/                              Unit tests; test_integration.py needs a live server
```

### Checks

```bash
make check              # ruff lint + format check, buf lint, mypy, unit tests
make format             # auto-fix lint and formatting
make test-integration   # integration tests; start the server first with `make run`
```

### Changing the API

1. Edit the RPC and its messages in `api/proto/yfinance_grpc/v1alpha1/*.proto`
2. Regenerate the Python and Go code with `make generate`, then run `make breaking` to check compatibility
3. Implement the method in the matching servicer in `src/yfinance_grpc_server/`, decorated with `@rpc`
4. Add unit tests (mock `yf.Ticker`), an integration test, and a row in [docs/rpc-reference.md](docs/rpc-reference.md)

## Error Handling

Failures are returned as standard gRPC status codes (`INVALID_ARGUMENT`, `NOT_FOUND`, `RESOURCE_EXHAUSTED`, `UNIMPLEMENTED`, `INTERNAL`). Missing data is not an error: an RPC with nothing to report returns `OK` with an empty response. See [docs/rpc-reference.md#errors](docs/rpc-reference.md#errors) for when each code is returned.

## Limitations

- Inherits rate limiting from Yahoo Finance
- Some data may not be available for all tickers
- Real-time data is delayed per Yahoo Finance terms
- Options data is only available for tickers with listed options
- Yahoo Finance API is not officially supported to be consumed by third parties, so expect potential breaking changes, downtime or other issues

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) - The excellent Python library this project wraps
- [buf](https://buf.build/) - For making protocol buffer development easier
- Yahoo Finance - For providing the data

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by Yahoo or Yahoo Finance nor the yfinance library. Use at your own risk and ensure compliance with Yahoo Finance's terms of service.
