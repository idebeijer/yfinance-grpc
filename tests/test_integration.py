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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
