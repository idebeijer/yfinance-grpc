// Example gRPC client for yfinance-grpc in Go.
// Requires a running server: make run (or make up)
package main

import (
	"context"
	"fmt"
	"log"
	"time"

	pb "github.com/idebeijer/yfinance-grpc/gen/go/yfinance_grpc/v1alpha1"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

const serverAddr = "localhost:50059"

func main() {
	conn, err := grpc.NewClient(serverAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("failed to connect: %v", err)
	}
	defer conn.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	tickerClient := pb.NewTickerServiceClient(conn)
	searchClient := pb.NewSearchServiceClient(conn)
	marketClient := pb.NewMarketServiceClient(conn)
	sectorClient := pb.NewSectorServiceClient(conn)

	// --- TickerService ---
	fmt.Println("=== GetInfo: AAPL ===")
	info, err := tickerClient.GetInfo(ctx, &pb.GetInfoRequest{Ticker: "AAPL"})
	if err != nil {
		log.Printf("GetInfo error: %v", err)
	} else {
		fmt.Printf("  Name:    %s\n", info.Info.LongName)
		fmt.Printf("  Sector:  %s\n", info.Info.Sector)
		fmt.Printf("  Price:   %.2f %s\n", info.Info.CurrentPrice, info.Info.Currency)
	}

	fmt.Println("\n=== GetFastInfo: AAPL ===")
	fastInfo, err := tickerClient.GetFastInfo(ctx, &pb.GetFastInfoRequest{Ticker: "AAPL"})
	if err != nil {
		log.Printf("GetFastInfo error: %v", err)
	} else {
		fmt.Printf("  Last price: %.2f %s\n", fastInfo.Info.LastPrice, fastInfo.Info.Currency)
		fmt.Printf("  Open:       %.2f\n", fastInfo.Info.Open)
		fmt.Printf("  Market cap: %d\n", fastInfo.Info.MarketCap)
	}

	fmt.Println("\n=== GetMultipleInfo: AAPL, MSFT, GOOGL ===")
	multi, err := tickerClient.GetMultipleInfo(ctx, &pb.GetMultipleInfoRequest{
		Tickers: []string{"AAPL", "MSFT", "GOOGL"},
	})
	if err != nil {
		log.Printf("GetMultipleInfo error: %v", err)
	} else {
		for ticker, i := range multi.Info {
			fmt.Printf("  %s: %s (%.2f %s)\n", ticker, i.LongName, i.CurrentPrice, i.Currency)
		}
	}

	// --- SearchService ---
	fmt.Println("\n=== Search: 'Apple' ===")
	searchResp, err := searchClient.Search(ctx, &pb.SearchRequest{
		Query:      "Apple",
		MaxResults: 3,
		NewsCount:  2,
	})
	if err != nil {
		log.Printf("Search error: %v", err)
	} else {
		fmt.Printf("  Quotes (%d):\n", len(searchResp.Quotes))
		for _, q := range searchResp.Quotes {
			fmt.Printf("    %s - %s (%s)\n", q.Symbol, q.ShortName, q.Exchange)
		}
		fmt.Printf("  News (%d):\n", len(searchResp.News))
		for _, n := range searchResp.News {
			fmt.Printf("    [%s] %s\n", n.Publisher, n.Title)
		}
	}

	fmt.Println("\n=== Lookup: equity 'Tesla' ===")
	lookupResp, err := searchClient.Lookup(ctx, &pb.LookupRequest{
		Query: "Tesla",
		Type:  pb.LookupType_LOOKUP_TYPE_EQUITY,
		Count: 3,
	})
	if err != nil {
		log.Printf("Lookup error: %v", err)
	} else {
		for _, r := range lookupResp.Results {
			fmt.Printf("  %s - %s (%s)\n", r.Symbol, r.Name, r.Exchange)
		}
	}

	// --- MarketService ---
	fmt.Println("\n=== GetMarketStatus: us_market ===")
	status, err := marketClient.GetMarketStatus(ctx, &pb.GetMarketStatusRequest{Market: "us_market"})
	if err != nil {
		log.Printf("GetMarketStatus error: %v", err)
	} else {
		fmt.Printf("  Type:     %s\n", status.Status.MarketType)
		fmt.Printf("  Timezone: %s\n", status.Status.TimezoneShort)
	}

	fmt.Println("\n=== GetMarketSummary: us_market ===")
	summary, err := marketClient.GetMarketSummary(ctx, &pb.GetMarketSummaryRequest{Market: "us_market"})
	if err != nil {
		log.Printf("GetMarketSummary error: %v", err)
	} else {
		for symbol, item := range summary.Summary {
			fmt.Printf("  %s (%s): %.2f (%.2f%%)\n",
				symbol, item.ShortName, item.RegularMarketPrice, item.RegularMarketChangePercent)
		}
	}

	// --- SectorService ---
	fmt.Println("\n=== GetSector: technology ===")
	sector, err := sectorClient.GetSector(ctx, &pb.GetSectorRequest{Key: "technology"})
	if err != nil {
		log.Printf("GetSector error: %v", err)
	} else {
		fmt.Printf("  Name:       %s\n", sector.Name)
		fmt.Printf("  Symbol:     %s\n", sector.Symbol)
		fmt.Printf("  Companies:  %d\n", sector.Overview.CompaniesCount)
		fmt.Printf("  Industries: %d\n", len(sector.Industries))
		if len(sector.TopCompanies) > 0 {
			fmt.Printf("  Top company: %s (%s)\n", sector.TopCompanies[0].Name, sector.TopCompanies[0].Symbol)
		}
	}

	fmt.Println("\n=== GetIndustry: consumer-electronics ===")
	industry, err := sectorClient.GetIndustry(ctx, &pb.GetIndustryRequest{Key: "consumer-electronics"})
	if err != nil {
		log.Printf("GetIndustry error: %v", err)
	} else {
		fmt.Printf("  Name:        %s\n", industry.Name)
		fmt.Printf("  Sector:      %s\n", industry.SectorName)
		fmt.Printf("  Companies:   %d\n", industry.Overview.CompaniesCount)
		if len(industry.TopCompanies) > 0 {
			fmt.Printf("  Top company: %s (%s)\n", industry.TopCompanies[0].Name, industry.TopCompanies[0].Symbol)
		}
	}
}
