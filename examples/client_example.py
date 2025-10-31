"""
Example client for the yfinance gRPC service

This demonstrates how to call the various endpoints from Python.
"""

import sys
from pathlib import Path

# Add both project root and gen directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

import grpc
from yfinance_grpc.v1 import ticker_pb2, ticker_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta


def run_examples():
    """Run example calls to the yfinance gRPC service"""
    
    # Connect to the server
    channel = grpc.insecure_channel('localhost:50059')
    stub = ticker_pb2_grpc.TickerServiceStub(channel)
    
    ticker_symbol = "AAPL"
    
    print(f"\n{'='*80}")
    print(f"yfinance gRPC Client Examples - {ticker_symbol}")
    print(f"{'='*80}\n")
    
    # Example 1: Get Info
    print("1. GetInfo - Basic ticker information")
    print("-" * 80)
    try:
        request = ticker_pb2.GetInfoRequest(ticker=ticker_symbol)
        response = stub.GetInfo(request)
        
        info = response.info
        print(f"Symbol: {info.symbol}")
        print(f"Name: {info.long_name}")
        print(f"Sector: {info.sector}")
        print(f"Industry: {info.industry}")
        print(f"Current Price: ${info.current_price:.2f} {info.currency}")
        print(f"Market Cap: ${info.market_cap:,}")
        print(f"P/E Ratio: {info.trailing_pe:.2f}")
        print(f"Dividend Yield: {info.dividend_yield*100:.2f}%")
        print(f"52 Week Range: ${info.fifty_two_week_low:.2f} - ${info.fifty_two_week_high:.2f}")
    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    
    # Example 2: Get Historical Data
    print(f"\n2. GetHistory - Last 5 days of historical data")
    print("-" * 80)
    try:
        request = ticker_pb2.GetHistoryRequest(
            ticker=ticker_symbol,
            period="5d",
            interval="1d"
        )
        response = stub.GetHistory(request)
        
        print(f"{'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12}")
        print("-" * 80)
        for row in response.rows:
            date_str = datetime.fromtimestamp(row.date.seconds).strftime('%Y-%m-%d')
            print(f"{date_str:<12} ${row.open:>9.2f} ${row.high:>9.2f} ${row.low:>9.2f} ${row.close:>9.2f} {row.volume:>12,}")
    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    
    # Example 3: Get Dividends
    print(f"\n3. GetDividends - Recent dividend history")
    print("-" * 80)
    try:
        request = ticker_pb2.GetDividendsRequest(
            ticker=ticker_symbol,
            period="1y"
        )
        response = stub.GetDividends(request)
        
        if response.rows:
            print(f"{'Date':<12} {'Amount':>10}")
            print("-" * 40)
            for row in response.rows[-5:]:  # Last 5 dividends
                date_str = datetime.fromtimestamp(row.date.seconds).strftime('%Y-%m-%d')
                print(f"{date_str:<12} ${row.amount:>9.4f}")
        else:
            print("No dividend data available")
    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    
    # Example 4: Get News
    print(f"\n4. GetNews - Recent news articles")
    print("-" * 80)
    try:
        request = ticker_pb2.GetNewsRequest(
            ticker=ticker_symbol,
            count=5
        )
        response = stub.GetNews(request)
        
        for i, article in enumerate(response.articles, 1):
            pub_time = datetime.fromtimestamp(article.provider_publish_time.seconds)
            print(f"\n{i}. {article.title}")
            print(f"   Publisher: {article.publisher}")
            print(f"   Published: {pub_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Link: {article.link}")
    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    
    # Example 5: Get Options
    print(f"\n5. GetOptions - Available option expiration dates")
    print("-" * 80)
    try:
        request = ticker_pb2.GetOptionsRequest(ticker=ticker_symbol)
        response = stub.GetOptions(request)
        
        print(f"Available expiration dates: {', '.join(response.expiration_dates[:10])}")
        
        # Get option chain for the first available date
        if response.expiration_dates:
            first_date = response.expiration_dates[0]
            print(f"\n6. GetOptionChain - Options for {first_date}")
            print("-" * 80)
            
            chain_request = ticker_pb2.GetOptionChainRequest(
                ticker=ticker_symbol,
                date=first_date
            )
            chain_response = stub.GetOptionChain(chain_request)
            
            print(f"\nCalls (first 5):")
            print(f"{'Strike':>10} {'Last':>10} {'Bid':>10} {'Ask':>10} {'Volume':>10} {'OI':>10}")
            print("-" * 70)
            for call in chain_response.calls[:5]:
                print(f"${call.strike:>9.2f} ${call.last_price:>9.2f} ${call.bid:>9.2f} ${call.ask:>9.2f} {call.volume:>10} {call.open_interest:>10}")
            
            print(f"\nPuts (first 5):")
            print(f"{'Strike':>10} {'Last':>10} {'Bid':>10} {'Ask':>10} {'Volume':>10} {'OI':>10}")
            print("-" * 70)
            for put in chain_response.puts[:5]:
                print(f"${put.strike:>9.2f} ${put.last_price:>9.2f} ${put.bid:>9.2f} ${put.ask:>9.2f} {put.volume:>10} {put.open_interest:>10}")
    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    
    # Example 6: Get Recommendations
    print(f"\n7. GetRecommendations - Analyst recommendations")
    print("-" * 80)
    try:
        request = ticker_pb2.GetRecommendationsRequest(ticker=ticker_symbol)
        response = stub.GetRecommendations(request)
        
        if response.rows:
            print(f"{'Date':<12} {'Firm':<30} {'Action':<10} {'Grade':<15}")
            print("-" * 80)
            for row in response.rows[-10:]:  # Last 10 recommendations
                date_str = datetime.fromtimestamp(row.date.seconds).strftime('%Y-%m-%d')
                grade = row.to_grade if row.to_grade else "N/A"
                print(f"{date_str:<12} {row.firm:<30} {row.action:<10} {grade:<15}")
        else:
            print("No recommendation data available")
    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    
    # Example 7: Get Institutional Holders
    print(f"\n8. GetInstitutionalHolders - Top institutional holders")
    print("-" * 80)
    try:
        request = ticker_pb2.GetInstitutionalHoldersRequest(ticker=ticker_symbol)
        response = stub.GetInstitutionalHolders(request)
        
        if response.holders:
            print(f"{'Holder':<40} {'Shares':>15} {'% Out':>8} {'Value':>15}")
            print("-" * 80)
            for holder in response.holders[:10]:
                print(f"{holder.holder:<40} {holder.shares:>15,} {holder.pct_out:>7.2%} ${holder.value:>14,.0f}")
        else:
            print("No institutional holder data available")
    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    
    print(f"\n{'='*80}")
    print("Examples completed!")
    print(f"{'='*80}\n")
    
    channel.close()


if __name__ == '__main__':
    run_examples()
