# yfinance-grpc

A gRPC server wrapper around the [yfinance](https://github.com/ranaroussi/yfinance) Python library, enabling access to Yahoo Finance data from any programming language that supports gRPC.

## Why?

The yfinance library is excellent for accessing Yahoo Finance data in Python, but if you're working in other languages like Go, Rust, Java, or C#, you need to either find an alternative library (which may not exist or be maintained) or implement your own Yahoo Finance client.

This project solves that problem by wrapping yfinance in a gRPC service, allowing you to:

- Access Yahoo Finance data from **any language** that supports gRPC
- Maintain a **single source of truth** for Yahoo Finance data across your microservices
- Leverage yfinance's robust implementation and maintenance
- Use strongly-typed protocol buffers for data exchange

## Features

The gRPC service provides access to the following yfinance functionality:

### Ticker Information

- **GetInfo**: Get comprehensive ticker information (price, market cap, P/E ratios, dividends, etc.)
- **GetHistory**: Get historical price data with configurable intervals and date ranges
- **GetDividends**: Get dividend payment history
- **GetSplits**: Get stock split history
- **GetActions**: Get all corporate actions (dividends, splits, capital gains)

### Financial Statements

- **GetFinancials**: Get income statements (yearly/quarterly/trailing)
- **GetBalanceSheet**: Get balance sheet data
- **GetCashFlow**: Get cash flow statements
- **GetEarnings**: Get earnings data

### Analysis & Research

- **GetRecommendations**: Get analyst recommendations and upgrades/downgrades
- **GetNews**: Get recent news articles for a ticker
- **GetCalendar**: Get upcoming earnings and dividend dates

### Options

- **GetOptions**: Get available option expiration dates
- **GetOptionChain**: Get detailed option chain data (calls and puts)

### Ownership

- **GetMajorHolders**: Get major shareholders information
- **GetInstitutionalHolders**: Get institutional ownership data
- **GetMutualFundHolders**: Get mutual fund ownership data

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
uv run python client_example.py
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

# List methods
grpcurl -plaintext localhost:50059 list yfinance_grpc.v1.TickerService

# Get ticker info
grpcurl -plaintext -d '{"ticker": "AAPL"}' \
  localhost:50059 yfinance_grpc.v1.TickerService.GetInfo

# Get historical data
grpcurl -plaintext -d '{"ticker": "AAPL", "period": "5d", "interval": "1d"}' \
  localhost:50059 yfinance_grpc.v1.TickerService.GetHistory
```

See [docs/grpcurl.md](docs/grpcurl.md) for more examples.

### Using from Other Languages

The protocol buffer definitions are in `api/proto/yfinance/v1/ticker.proto`. Use `buf` to generate client code for your language:

#### Go Example

```bash
buf generate --template buf.gen.go.yaml
```

Then in your Go code:

```go
import (
    "context"
    "google.golang.org/grpc"
    pb "your-module/gen/yfinance/v1"
)

func main() {
    conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
    defer conn.Close()

    client := pb.NewTickerServiceClient(conn)

    resp, _ := client.GetInfo(context.Background(), &pb.GetInfoRequest{
        Ticker: "AAPL",
    })

    fmt.Printf("Price: $%.2f\n", resp.Info.CurrentPrice)
}
```

#### Node.js Example

```bash
npm install @grpc/grpc-js @grpc/proto-loader
```

```javascript
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");

const packageDefinition = protoLoader.loadSync(
  "api/proto/yfinance/v1/ticker.proto"
);
const proto = grpc.loadPackageDefinition(packageDefinition).yfinance.v1;

const client = new proto.TickerService(
  "localhost:50051",
  grpc.credentials.createInsecure()
);

client.getInfo({ ticker: "AAPL" }, (error, response) => {
  console.log(`Price: $${response.info.currentPrice}`);
});
```

## API Documentation

### GetInfo

Get comprehensive information about a ticker.

**Request:**

```protobuf
message GetInfoRequest {
  string ticker = 1; // e.g., "AAPL", "GOOGL"
}
```

**Response:** Returns `TickerInfo` with 100+ fields including:

- Basic info (symbol, name, sector, industry)
- Trading data (current price, volume, market cap)
- Valuation metrics (P/E ratios, price-to-book)
- Dividends (rate, yield, payout ratio)
- Financial metrics (profit margins, ROE, ROA)
- 52-week ranges and moving averages
- Analyst targets

### GetHistory

Get historical price data.

**Request:**

```protobuf
message GetHistoryRequest {
  string ticker = 1;
  optional string period = 2;  // "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
  optional Timestamp start = 3;  // Alternative to period
  optional Timestamp end = 4;
  string interval = 5;  // "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"
  bool prepost = 6;  // Include pre/post market
  bool actions = 7;  // Include dividends/splits
  bool auto_adjust = 8;  // Auto-adjust OHLC
}
```

**Response:** Array of `HistoryRow` with OHLCV data plus optional dividends/splits.

### GetOptionChain

Get option chain data for a specific expiration date.

**Request:**

```protobuf
message GetOptionChainRequest {
  string ticker = 1;
  optional string date = 2;  // YYYY-MM-DD format
  optional string tz = 3;    // Timezone
}
```

**Response:** Arrays of calls and puts with strike prices, bid/ask, volume, open interest, implied volatility, etc.

See `api/proto/yfinance_grpc/v1/ticker.proto` for complete API documentation.

## Development

### Regenerating Protocol Buffers

After modifying `ticker.proto`:

```bash
buf generate
# or
make generate
```

### Adding New Endpoints

1. Define the RPC method in `api/proto/yfinance_grpc/v1/ticker.proto`
2. Add request/response message types
3. Run `buf generate` or `make generate`
4. Implement the method in `server.py`'s `TickerServiceServicer` class
5. Add an example to `client_example.py`

## Error Handling

The server returns gRPC status codes:

- `OK`: Request succeeded
- `INTERNAL`: yfinance error or data processing error
- Error details are included in the status message

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
