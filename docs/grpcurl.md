# Using grpcurl with yfinance-grpc

The server now supports gRPC reflection, which means you can use `grpcurl` without needing to provide proto files.

## Installing grpcurl

### macOS
```bash
brew install grpcurl
```

### Linux
```bash
# Download latest release
wget https://github.com/fullstorydev/grpcurl/releases/download/v1.9.1/grpcurl_1.9.1_linux_x86_64.tar.gz
tar -xvzf grpcurl_1.9.1_linux_x86_64.tar.gz
sudo mv grpcurl /usr/local/bin/
```

### Or using Go
```bash
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
```

## Usage Examples

### List all services
```bash
grpcurl -plaintext localhost:50059 list
```

Expected output:
```
grpc.reflection.v1alpha.ServerReflection
yfinance_grpc.v1.TickerService
```

### List all methods in TickerService
```bash
grpcurl -plaintext localhost:50059 list yfinance_grpc.v1.TickerService
```

Expected output:
```
yfinance_grpc.v1.TickerService.GetInfo
yfinance_grpc.v1.TickerService.GetHistory
yfinance_grpc.v1.TickerService.GetDividends
yfinance_grpc.v1.TickerService.GetSplits
yfinance_grpc.v1.TickerService.GetActions
yfinance_grpc.v1.TickerService.GetFinancials
yfinance_grpc.v1.TickerService.GetBalanceSheet
yfinance_grpc.v1.TickerService.GetCashFlow
yfinance_grpc.v1.TickerService.GetEarnings
yfinance_grpc.v1.TickerService.GetRecommendations
yfinance_grpc.v1.TickerService.GetOptions
yfinance_grpc.v1.TickerService.GetOptionChain
yfinance_grpc.v1.TickerService.GetCalendar
yfinance_grpc.v1.TickerService.GetNews
yfinance_grpc.v1.TickerService.GetMajorHolders
yfinance_grpc.v1.TickerService.GetInstitutionalHolders
yfinance_grpc.v1.TickerService.GetMutualFundHolders
```

### Describe a method
```bash
grpcurl -plaintext localhost:50059 describe yfinance_grpc.v1.TickerService.GetInfo
```

### Call GetInfo
```bash
grpcurl -plaintext -d '{"ticker": "AAPL"}' localhost:50059 yfinance_grpc.v1.TickerService.GetInfo
```

### Call GetHistory
```bash
grpcurl -plaintext -d '{"ticker": "AAPL", "period": "5d", "interval": "1d"}' \
  localhost:50059 yfinance_grpc.v1.TickerService.GetHistory
```

### Call GetNews
```bash
grpcurl -plaintext -d '{"ticker": "AAPL", "count": 5}' \
  localhost:50059 yfinance_grpc.v1.TickerService.GetNews
```

### Call GetRecommendations
```bash
grpcurl -plaintext -d '{"ticker": "AAPL"}' \
  localhost:50059 yfinance_grpc.v1.TickerService.GetRecommendations
```

### Call GetOptions
```bash
grpcurl -plaintext -d '{"ticker": "AAPL"}' \
  localhost:50059 yfinance_grpc.v1.TickerService.GetOptions
```

### Call GetOptionChain
```bash
# First get available dates
grpcurl -plaintext -d '{"ticker": "AAPL"}' \
  localhost:50059 yfinance_grpc.v1.TickerService.GetOptions

# Then use one of the dates
grpcurl -plaintext -d '{"ticker": "AAPL", "date": "2025-11-15"}' \
  localhost:50059 yfinance_grpc.v1.TickerService.GetOptionChain
```

## Pretty Print Output

Use `jq` to format JSON output:

```bash
grpcurl -plaintext -d '{"ticker": "AAPL"}' \
  localhost:50059 yfinance_grpc.v1.TickerService.GetInfo | jq .
```

## Using with Docker

If running the server in Docker:

```bash
# Start the server
docker compose up -d

# Call from host
grpcurl -plaintext -d '{"ticker": "AAPL"}' localhost:50059 yfinance_grpc.v1.TickerService.GetInfo
```

## Troubleshooting

### Connection refused
Make sure the server is running:
```bash
make run
# or
docker compose up
```

### "Failed to dial target host"
Check that port 50059 is not blocked by firewall and the server is listening:
```bash
netstat -an | grep 50059
# or
lsof -i :50059
```

### "Method not found"
Make sure you're using the correct service and method names. List available methods:
```bash
grpcurl -plaintext localhost:50059 list yfinance_grpc.v1.TickerService
```
