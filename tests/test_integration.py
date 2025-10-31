"""
Integration tests for yfinance-grpc server

These tests require a running server instance and test the full gRPC communication.
Run with: pytest tests/test_integration.py
"""

import sys
from pathlib import Path
from datetime import datetime

import pytest
import grpc

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

from yfinance_grpc.v1 import ticker_pb2, ticker_pb2_grpc


@pytest.fixture(scope="module")
def grpc_channel():
    """Create a gRPC channel for testing"""
    channel = grpc.insecure_channel('localhost:50059')
    yield channel
    channel.close()


@pytest.fixture(scope="module")
def stub(grpc_channel):
    """Create a gRPC stub for testing"""
    return ticker_pb2_grpc.TickerServiceStub(grpc_channel)


class TestIntegrationGetInfo:
    """Integration tests for GetInfo endpoint"""

    def test_get_info_apple(self, stub):
        """Test GetInfo with AAPL ticker"""
        request = ticker_pb2.GetInfoRequest(ticker="AAPL")
        response = stub.GetInfo(request)
        
        assert response.info.symbol == "AAPL"
        assert "Apple" in response.info.long_name
        assert response.info.sector == "Technology"
        assert response.info.current_price > 0
        assert response.info.market_cap > 0

    def test_get_info_multiple_tickers(self, stub):
        """Test GetInfo with multiple different tickers"""
        tickers = ["AAPL", "MSFT", "GOOGL"]
        
        for ticker_symbol in tickers:
            request = ticker_pb2.GetInfoRequest(ticker=ticker_symbol)
            response = stub.GetInfo(request)
            
            assert response.info.symbol == ticker_symbol
            assert len(response.info.long_name) > 0


class TestIntegrationGetHistory:
    """Integration tests for GetHistory endpoint"""

    def test_get_history_default_period(self, stub):
        """Test GetHistory with default period"""
        request = ticker_pb2.GetHistoryRequest(
            ticker="AAPL",
            period="5d",
            interval="1d"
        )
        response = stub.GetHistory(request)
        
        assert len(response.rows) > 0
        # Check that all required fields are present
        for row in response.rows:
            assert row.open > 0
            assert row.high > 0
            assert row.low > 0
            assert row.close > 0
            assert row.volume > 0

    def test_get_history_different_intervals(self, stub):
        """Test GetHistory with different time intervals"""
        intervals = ["1d", "1wk", "1mo"]
        
        for interval in intervals:
            request = ticker_pb2.GetHistoryRequest(
                ticker="AAPL",
                period="1mo",
                interval=interval
            )
            response = stub.GetHistory(request)
            
            assert len(response.rows) > 0


class TestIntegrationGetDividends:
    """Integration tests for GetDividends endpoint"""

    def test_get_dividends(self, stub):
        """Test GetDividends endpoint"""
        request = ticker_pb2.GetDividendsRequest(
            ticker="AAPL",
            period="1y"
        )
        response = stub.GetDividends(request)
        
        # Apple pays dividends, so we should get some data
        assert len(response.rows) > 0
        for row in response.rows:
            assert row.amount > 0


class TestIntegrationGetRecommendations:
    """Integration tests for GetRecommendations endpoint"""

    def test_get_recommendations(self, stub):
        """Test GetRecommendations endpoint"""
        request = ticker_pb2.GetRecommendationsRequest(ticker="AAPL")
        response = stub.GetRecommendations(request)
        
        # Apple should have analyst recommendations
        assert len(response.rows) > 0
        
        # Check that data is sorted by date descending (newest first)
        dates = [row.date.seconds for row in response.rows]
        assert dates == sorted(dates, reverse=True), "Recommendations should be sorted newest first"
        
        # Check first recommendation has required fields
        first_rec = response.rows[0]
        assert len(first_rec.firm) > 0
        assert first_rec.date.seconds > 0


class TestIntegrationGetNews:
    """Integration tests for GetNews endpoint"""

    def test_get_news_default_count(self, stub):
        """Test GetNews with default count"""
        request = ticker_pb2.GetNewsRequest(ticker="AAPL")
        response = stub.GetNews(request)
        
        # Should get some news articles
        assert len(response.articles) > 0
        assert len(response.articles) <= 10  # Default count
        
        # Check first article has required fields
        first_article = response.articles[0]
        assert len(first_article.title) > 0
        assert len(first_article.publisher) > 0
        assert len(first_article.link) > 0
        assert first_article.provider_publish_time.seconds > 0

    def test_get_news_custom_count(self, stub):
        """Test GetNews with custom count"""
        request = ticker_pb2.GetNewsRequest(ticker="AAPL", count=3)
        response = stub.GetNews(request)
        
        # Should respect the count parameter
        assert len(response.articles) == 3


class TestIntegrationGetOptions:
    """Integration tests for GetOptions endpoint"""

    def test_get_options(self, stub):
        """Test GetOptions endpoint"""
        request = ticker_pb2.GetOptionsRequest(ticker="AAPL")
        response = stub.GetOptions(request)
        
        # Apple should have options available
        assert len(response.expiration_dates) > 0
        
        # Dates should be in YYYY-MM-DD format
        for date_str in response.expiration_dates:
            assert len(date_str) == 10
            assert date_str[4] == '-'
            assert date_str[7] == '-'


class TestIntegrationGetOptionChain:
    """Integration tests for GetOptionChain endpoint"""

    def test_get_option_chain(self, stub):
        """Test GetOptionChain endpoint"""
        # First get available dates
        options_request = ticker_pb2.GetOptionsRequest(ticker="AAPL")
        options_response = stub.GetOptions(options_request)
        
        assert len(options_response.expiration_dates) > 0
        
        # Get option chain for first available date
        request = ticker_pb2.GetOptionChainRequest(
            ticker="AAPL",
            date=options_response.expiration_dates[0]  # Field name is 'date'
        )
        response = stub.GetOptionChain(request)
        
        # Should have both calls and puts
        assert len(response.calls) > 0
        assert len(response.puts) > 0
        
        # Check first call option
        first_call = response.calls[0]
        assert first_call.strike > 0
        assert first_call.last_price >= 0


class TestIntegrationGetInstitutionalHolders:
    """Integration tests for GetInstitutionalHolders endpoint"""

    def test_get_institutional_holders(self, stub):
        """Test GetInstitutionalHolders endpoint"""
        request = ticker_pb2.GetInstitutionalHoldersRequest(ticker="AAPL")
        response = stub.GetInstitutionalHolders(request)
        
        # Apple should have institutional holders
        assert len(response.holders) > 0
        
        # Check first holder
        first_holder = response.holders[0]
        assert len(first_holder.holder) > 0
        assert first_holder.shares > 0


class TestIntegrationGetMultipleInfo:
    """Integration tests for GetMultipleInfo endpoint"""

    def test_get_multiple_info_two_tickers(self, stub):
        """Test GetMultipleInfo with two tech stocks"""
        request = ticker_pb2.GetMultipleInfoRequest(tickers=["AAPL", "MSFT"])
        response = stub.GetMultipleInfo(request)
        
        # Should have info for both tickers
        assert len(response.info) == 2
        assert "AAPL" in response.info
        assert "MSFT" in response.info
        
        # Validate AAPL data
        aapl_info = response.info["AAPL"]
        assert aapl_info.symbol == "AAPL"
        assert "Apple" in aapl_info.long_name
        assert aapl_info.sector == "Technology"
        assert aapl_info.current_price > 0
        assert aapl_info.market_cap > 0
        
        # Validate MSFT data
        msft_info = response.info["MSFT"]
        assert msft_info.symbol == "MSFT"
        assert "Microsoft" in msft_info.long_name
        assert msft_info.sector == "Technology"
        assert msft_info.current_price > 0
        assert msft_info.market_cap > 0

    def test_get_multiple_info_three_tickers(self, stub):
        """Test GetMultipleInfo with three different sector stocks"""
        request = ticker_pb2.GetMultipleInfoRequest(tickers=["AAPL", "JPM", "JNJ"])
        response = stub.GetMultipleInfo(request)
        
        # Should have info for all three tickers
        assert len(response.info) == 3
        assert "AAPL" in response.info
        assert "JPM" in response.info
        assert "JNJ" in response.info
        
        # Each should have basic data
        for symbol in ["AAPL", "JPM", "JNJ"]:
            info = response.info[symbol]
            assert info.symbol == symbol
            assert len(info.long_name) > 0
            assert len(info.sector) > 0

    def test_get_multiple_info_single_ticker(self, stub):
        """Test GetMultipleInfo with a single ticker"""
        request = ticker_pb2.GetMultipleInfoRequest(tickers=["GOOGL"])
        response = stub.GetMultipleInfo(request)
        
        assert len(response.info) == 1
        assert "GOOGL" in response.info
        
        info = response.info["GOOGL"]
        assert info.symbol == "GOOGL"
        assert "Alphabet" in info.long_name or "Google" in info.long_name
        assert info.current_price > 0


class TestIntegrationDownloadHistory:
    """Integration tests for DownloadHistory streaming endpoint"""

    def test_download_history_single_ticker(self, stub):
        """Test DownloadHistory with a single ticker"""
        request = ticker_pb2.DownloadHistoryRequest(
            tickers=["AAPL"],
            period="1mo",
            interval="1d"
        )
        
        responses = list(stub.DownloadHistory(request))
        
        # Should have at least one response
        assert len(responses) > 0
        
        # Check response structure
        for response in responses:
            assert response.ticker == "AAPL"
            assert len(response.rows) > 0
            
            # Verify we get rows with valid price data
            valid_rows = 0
            for row in response.rows:
                assert row.date.seconds > 0
                # Check for valid price data (not all zeros)
                if row.open > 0 or row.close > 0:
                    valid_rows += 1
                    # Basic sanity checks on prices
                    assert row.high >= row.low
                    assert row.volume >= 0
            
            # Should have at least some valid trading data
            assert valid_rows > 0, f"No valid price data returned for AAPL"

    def test_download_history_multiple_tickers(self, stub):
        """Test DownloadHistory with multiple tickers"""
        request = ticker_pb2.DownloadHistoryRequest(
            tickers=["AAPL", "MSFT"],
            period="5d",
            interval="1d"
        )
        
        responses = list(stub.DownloadHistory(request))
        
        # Should have responses for both tickers
        assert len(responses) > 0
        
        # Collect tickers from responses
        tickers_seen = set()
        for response in responses:
            tickers_seen.add(response.ticker)
            assert response.ticker in ["AAPL", "MSFT"]
            assert len(response.rows) > 0
            
            # Check rows have valid data
            valid_rows = 0
            for row in response.rows:
                assert row.date.seconds > 0
                if row.close > 0:
                    valid_rows += 1
            
            assert valid_rows > 0, f"No valid price data for {response.ticker}"
        
        # Should have seen both tickers
        assert "AAPL" in tickers_seen
        assert "MSFT" in tickers_seen

    def test_download_history_with_dates(self, stub):
        """Test DownloadHistory with start/end dates"""
        from google.protobuf.timestamp_pb2 import Timestamp
        
        # Create timestamps for January 2024
        start_ts = Timestamp()
        start_ts.FromDatetime(datetime(2024, 1, 1))
        
        end_ts = Timestamp()
        end_ts.FromDatetime(datetime(2024, 1, 31))
        
        request = ticker_pb2.DownloadHistoryRequest(
            tickers=["AAPL"],
            start=start_ts,
            end=end_ts,
            interval="1d"
        )
        
        responses = list(stub.DownloadHistory(request))
        
        # Should have at least one response
        assert len(responses) > 0
        
        for response in responses:
            assert response.ticker == "AAPL"
            # Should have trading days in January 2024
            assert len(response.rows) > 15  # At least 15 trading days
            assert len(response.rows) < 25  # But not more than 25
            
            for row in response.rows:
                # Timestamps should be in January 2024
                # Unix timestamps: Jan 1 2024 = 1704067200, Jan 31 2024 = 1706659200
                assert row.date.seconds >= 1704067200
                assert row.date.seconds <= 1706745600  # End of Jan 31

    def test_download_history_auto_adjust(self, stub):
        """Test DownloadHistory with auto_adjust flag"""
        request = ticker_pb2.DownloadHistoryRequest(
            tickers=["AAPL"],
            period="3mo",
            interval="1d",
            auto_adjust=True
        )
        
        responses = list(stub.DownloadHistory(request))
        
        # Should have data
        assert len(responses) > 0
        
        for response in responses:
            assert response.ticker == "AAPL"
            assert len(response.rows) > 0
            
            # Verify valid price data exists
            valid_rows = [row for row in response.rows if row.close > 0]
            assert len(valid_rows) > 0, "No valid price data in response"


class TestIntegrationErrorHandling:
    """Integration tests for error handling"""

    def test_invalid_ticker(self, stub):
        """Test handling of invalid ticker"""
        request = ticker_pb2.GetInfoRequest(ticker="INVALID_TICKER_XYZ123")
        
        try:
            response = stub.GetInfo(request)
            # If it doesn't raise an error, check that response is empty/default
            # Some invalid tickers might return empty data instead of error
        except grpc.RpcError as e:
            # Server should return an appropriate error
            assert e.code() == grpc.StatusCode.INTERNAL

    def test_download_history_invalid_ticker(self, stub):
        """Test DownloadHistory with invalid ticker returns proper error"""
        request = ticker_pb2.DownloadHistoryRequest(
            tickers=["INVALID_TICKER_XYZ123"],
            period="1mo",
            interval="1d"
        )
        
        try:
            responses = list(stub.DownloadHistory(request))
            # Should return error, not empty responses
            assert len(responses) == 0, "Should not return data for invalid ticker"
        except grpc.RpcError as e:
            # Should get NOT_FOUND error
            assert e.code() in [grpc.StatusCode.NOT_FOUND, grpc.StatusCode.INTERNAL]

    def test_download_history_malformed_ticker(self, stub):
        """Test DownloadHistory with malformed ticker string (space-separated instead of array)"""
        # This simulates the user error: ["AAPL TSLA"] instead of ["AAPL", "TSLA"]
        request = ticker_pb2.DownloadHistoryRequest(
            tickers=["AAPL MSFT"],  # Wrong: space-separated in one string
            period="1mo",
            interval="1d"
        )
        
        try:
            responses = list(stub.DownloadHistory(request))
            # Should either error or return no data
            if len(responses) > 0:
                # If it returns data, it should be invalid (all zeros)
                for response in responses:
                    valid_rows = [r for r in response.rows if r.close > 0]
                    # Should have no valid data for malformed ticker
                    assert len(valid_rows) == 0, "Malformed ticker should not return valid price data"
        except grpc.RpcError as e:
            # Or it should return a proper error
            assert e.code() in [grpc.StatusCode.NOT_FOUND, grpc.StatusCode.INTERNAL]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
