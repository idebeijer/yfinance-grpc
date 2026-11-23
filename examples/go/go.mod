module github.com/idebeijer/yfinance-grpc/examples/go

go 1.26.1

require (
	github.com/idebeijer/yfinance-grpc/gen/go v0.0.0
	google.golang.org/grpc v1.85.0
)

require (
	golang.org/x/net v0.63.0 // indirect
	golang.org/x/sys v0.50.0 // indirect
	golang.org/x/text v0.44.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20261118221215-c8830f628b3f // indirect
	google.golang.org/protobuf v1.36.12 // indirect
)

replace github.com/idebeijer/yfinance-grpc/gen/go => ../../gen/go
