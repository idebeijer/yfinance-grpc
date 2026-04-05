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
- **DownloadHistory**: Stream historical data for multiple tickers concurrently (server-streaming RPC)

### Corporate Actions

- **GetDividends**: Dividend payment history
- **GetSplits**: Stock split history
- **GetCapitalGains**: Capital gains distributions (ETFs/funds)
- **GetActions**: All corporate actions combined (dividends, splits, capital gains)

### Financial Statements

- **GetFinancials**: Income statements (yearly/quarterly/trailing)
- **GetBalanceSheet**: Balance sheet data
- **GetCashFlow**: Cash flow statements
- **GetEarnings**: Earnings revenue and EPS data

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

- **GetMarketStatus**: Current session type (REGULAR/PRE/POST), open/close timestamps and timezone for a market (e.g. `us_market`, `gb_market`)
- **GetMarketSummary**: Price snapshot of major instruments in a market — price, change and change %

### Sector & Industry (SectorService)

- **GetSector**: Sector overview, top companies, top ETFs, top mutual funds, and list of constituent industries (e.g. key `technology`)
- **GetIndustry**: Industry overview, top companies, top performing companies (YTD return/last price/target price) and top growth companies (e.g. key `consumer-electronics`)

## Quick Start

### Using Docker (Recommended)

The easiest way to get started is using Docker:

```bash
# Build and run using Make
make docker-build
make docker-run

# Or using docker-compose
docker-compose up -d

# View logs
make docker-logs
# or
docker-compose logs -f
```

The server will be available at `localhost:50059`.

### Using Make

The project includes a Makefile for common tasks:

```bash
make help          # Show all available commands
make install       # Install dependencies
make generate      # Generate protobuf code
make run           # Start the server
make test          # Run client example
make docker-build  # Build Docker image
make docker-run    # Run in Docker
```

## Installation

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) for Python environment management
- [buf](https://buf.build/) for protocol buffer compilation
- Docker (optional, for containerized deployment)
- Make (optional, for convenience commands)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/idebeijer/yfinance-grpc.git
cd yfinance-grpc
```

2. Install dependencies using uv:

```bash
uv sync
# or
make install
```

3. Generate the protocol buffer code:

```bash
buf generate
# or
make generate
```

## Usage

### Starting the Server

**Option 1: Run directly with Python**

```bash
uv run python main.py
# or
make run
```

**Option 2: Run with docker-compose**

```bash
docker-compose up -d
# or
make up
```

The server will start on port `50059` by default.

### Running the Python Client Example

To see examples of all the available endpoints:

```bash
uv run python examples/client_example.py
# or
make test
```

This will demonstrate:

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
grpcurl -plaintext -d '{"market": "us_market"}' \
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
import (
    "context"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    pb "github.com/idebeijer/yfinance-grpc/gen/go/yfinance_grpc/v1alpha1"
)

func main() {
    conn, _ := grpc.NewClient("localhost:50059",
        grpc.WithTransportCredentials(insecure.NewCredentials()))
    defer conn.Close()

    client := pb.NewTickerServiceClient(conn)
    resp, _ := client.GetInfo(context.Background(), &pb.GetInfoRequest{Ticker: "AAPL"})
    fmt.Printf("Price: $%.2f\n", resp.Info.CurrentPrice)
}
```

#### Node.js

```bash
npm install @grpc/grpc-js @grpc/proto-loader
```

```javascript
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");

const packageDefinition = protoLoader.loadSync(
  "api/proto/yfinance_grpc/v1alpha1/ticker.proto",
);
const proto = grpc.loadPackageDefinition(packageDefinition).yfinance_grpc.v1alpha1;

const client = new proto.TickerService(
  "localhost:50059",
  grpc.credentials.createInsecure(),
);

client.getInfo({ ticker: "AAPL" }, (error, response) => {
  console.log(`Price: $${response.info.currentPrice}`);
});
```

## API Documentation

See [docs/rpc-reference.md](docs/rpc-reference.md) for a full mapping of every RPC to its yfinance equivalent, parameters, and return type.

The complete protobuf definitions are in `api/proto/yfinance_grpc/v1alpha1/`.

## Development

### Regenerating Protocol Buffers

After modifying `ticker.proto`:

```bash
buf generate
# or
make generate
```

### Adding New Endpoints

1. Define the RPC method in the appropriate `api/proto/yfinance_grpc/v1alpha1/*.proto` file (or add a new proto file for a new service)
2. Add request/response message types
3. Run `buf generate` or `make generate`
4. Implement the method in the corresponding servicer in `src/`
5. Add an example to `examples/client_example.py`

## Error Handling

The server returns standard gRPC status codes:

- `OK`: Request succeeded
- `NOT_FOUND`: Ticker has no data or doesn't exist (e.g. invalid symbol passed to `DownloadHistory`)
- `INVALID_ARGUMENT`: Bad request parameters (e.g. empty tickers list)
- `INTERNAL`: Unexpected yfinance or data processing error

Error details are included in the status message.

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
