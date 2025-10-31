"""
Tests for the yfinance gRPC server

These tests verify the server implementation without requiring a running server.
They use mocking to avoid hitting the actual Yahoo Finance API.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import pytest
import pandas as pd
import grpc
from google.protobuf.timestamp_pb2 import Timestamp

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

from src.server import TickerServiceServicer, datetime_to_timestamp, safe_float, safe_int, safe_str
from yfinance_grpc.v1 import ticker_pb2


class TestHelperFunctions:
    """Test helper functions used in the server"""

    def test_datetime_to_timestamp_with_datetime(self):
        """Test converting datetime to protobuf timestamp"""
        dt = datetime(2025, 1, 15, 12, 30, 45)
        ts = datetime_to_timestamp(dt)
        
        assert ts is not None
        assert ts.seconds > 0
        # Convert back to verify
        converted = datetime.fromtimestamp(ts.seconds)
        assert converted.year == 2025
        assert converted.month == 1
        assert converted.day == 15

    def test_datetime_to_timestamp_with_pandas_timestamp(self):
        """Test converting pandas Timestamp to protobuf timestamp"""
        pd_ts = pd.Timestamp('2025-01-15 12:30:45')
        ts = datetime_to_timestamp(pd_ts)
        
        assert ts is not None
        assert ts.seconds > 0

    def test_datetime_to_timestamp_with_nan(self):
        """Test that NaN returns None"""
        result = datetime_to_timestamp(pd.NaT)
        assert result is None

    def test_safe_float_with_valid_number(self):
        """Test safe_float with valid numbers"""
        assert safe_float(42.5) == 42.5
        assert safe_float(100) == 100.0

    def test_safe_float_with_nan(self):
        """Test safe_float with NaN returns 0"""
        assert safe_float(float('nan')) == 0.0
        assert safe_float(pd.NA) == 0.0
        assert safe_float(None) == 0.0

    def test_safe_int_with_valid_number(self):
        """Test safe_int with valid numbers"""
        assert safe_int(42) == 42
        assert safe_int(42.7) == 42

    def test_safe_int_with_nan(self):
        """Test safe_int with NaN returns 0"""
        assert safe_int(float('nan')) == 0
        assert safe_int(pd.NA) == 0
        assert safe_int(None) == 0

    def test_safe_str_with_valid_string(self):
        """Test safe_str with valid strings"""
        assert safe_str("test") == "test"
        assert safe_str(123) == "123"

    def test_safe_str_with_none(self):
        """Test safe_str with None returns empty string"""
        assert safe_str(None) == ""
        assert safe_str(float('nan')) == ""


class TestTickerServiceGetInfo:
    """Test GetInfo endpoint"""

    @patch('src.server.yf.Ticker')
    def test_get_info_success(self, mock_ticker_class):
        """Test successful GetInfo call"""
        # Setup mock
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        mock_info = {
            'symbol': 'AAPL',
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'currentPrice': 150.0,
            'marketCap': 2500000000000,
            'trailingPE': 25.5,
            'dividendYield': 0.005,
            'fiftyTwoWeekLow': 120.0,
            'fiftyTwoWeekHigh': 180.0,
            'currency': 'USD'
        }
        # ticker.info should return the dict directly, not be a method
        mock_ticker.info = mock_info
        
        # Create servicer and call
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetInfoRequest(ticker="AAPL")
        
        response = servicer.GetInfo(request, context)
        
        # Assertions
        assert response.info.symbol == 'AAPL'
        assert response.info.long_name == 'Apple Inc.'
        assert response.info.sector == 'Technology'
        assert response.info.current_price == 150.0
        assert response.info.market_cap == 2500000000000
        mock_ticker_class.assert_called_once_with("AAPL")

    @patch('src.server.yf.Ticker')
    def test_get_info_error(self, mock_ticker_class):
        """Test GetInfo with error"""
        mock_ticker_class.side_effect = Exception("API Error")
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetInfoRequest(ticker="INVALID")
        
        response = servicer.GetInfo(request, context)
        
        # Should return empty response and set error context
        context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)
        context.set_details.assert_called_once()


class TestTickerServiceGetHistory:
    """Test GetHistory endpoint"""

    @patch('src.server.yf.Ticker')
    def test_get_history_success(self, mock_ticker_class):
        """Test successful GetHistory call"""
        # Setup mock
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        # Create mock history dataframe
        dates = pd.date_range('2025-01-01', periods=3, freq='D')
        mock_history = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [105.0, 106.0, 107.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [104.0, 105.0, 106.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=dates)
        mock_ticker.history.return_value = mock_history
        
        # Create servicer and call
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetHistoryRequest(
            ticker="AAPL",
            period="3d",
            interval="1d"
        )
        
        response = servicer.GetHistory(request, context)
        
        # Assertions
        assert len(response.rows) == 3
        assert response.rows[0].open == 100.0
        assert response.rows[0].high == 105.0
        assert response.rows[0].close == 104.0
        assert response.rows[0].volume == 1000000


class TestTickerServiceGetDividends:
    """Test GetDividends endpoint"""

    @patch('src.server.yf.Ticker')
    def test_get_dividends_success(self, mock_ticker_class):
        """Test successful GetDividends call"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        # Create mock dividends series
        dates = pd.date_range('2024-01-01', periods=4, freq='Q')
        mock_dividends = pd.Series([0.25, 0.25, 0.26, 0.26], index=dates)
        # get_dividends should return the series
        mock_ticker.get_dividends.return_value = mock_dividends
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetDividendsRequest(ticker="AAPL", period="1y")
        
        response = servicer.GetDividends(request, context)
        
        assert len(response.rows) == 4
        assert response.rows[0].amount == 0.25


class TestTickerServiceGetRecommendations:
    """Test GetRecommendations endpoint"""

    @patch('src.server.yf.Ticker')
    def test_get_recommendations_success(self, mock_ticker_class):
        """Test successful GetRecommendations call"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        # Create mock recommendations dataframe
        dates = pd.DatetimeIndex([
            '2025-10-31 13:28:05',
            '2025-10-30 12:00:00',
            '2025-10-29 11:00:00'
        ], name='GradeDate')
        
        mock_recs = pd.DataFrame({
            'Firm': ['Goldman Sachs', 'Morgan Stanley', 'JP Morgan'],
            'ToGrade': ['Buy', 'Overweight', 'Neutral'],
            'FromGrade': ['Neutral', 'Neutral', 'Buy'],
            'Action': ['up', 'up', 'down']
        }, index=dates)
        
        mock_ticker.upgrades_downgrades = mock_recs
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetRecommendationsRequest(ticker="AAPL")
        
        response = servicer.GetRecommendations(request, context)
        
        # Should be sorted by date descending (most recent first)
        assert len(response.rows) == 3
        assert response.rows[0].firm == 'Goldman Sachs'  # Most recent
        assert response.rows[0].to_grade == 'Buy'
        assert response.rows[0].action == 'up'
        assert response.rows[2].firm == 'JP Morgan'  # Oldest

    @patch('src.server.yf.Ticker')
    def test_get_recommendations_empty(self, mock_ticker_class):
        """Test GetRecommendations with no data"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.upgrades_downgrades = pd.DataFrame()
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetRecommendationsRequest(ticker="AAPL")
        
        response = servicer.GetRecommendations(request, context)
        
        assert len(response.rows) == 0


class TestTickerServiceGetNews:
    """Test GetNews endpoint"""

    @patch('src.server.yf.Ticker')
    def test_get_news_success(self, mock_ticker_class):
        """Test successful GetNews call"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        # Mock news with nested structure
        mock_news = [
            {
                'id': 'article-1',
                'content': {
                    'id': 'article-1',
                    'title': 'Apple Reports Strong Earnings',
                    'contentType': 'STORY',
                    'pubDate': '2025-10-31T14:20:57Z',
                    'provider': {
                        'displayName': 'Yahoo Finance'
                    },
                    'canonicalUrl': {
                        'url': 'https://finance.yahoo.com/news/article-1.html'
                    },
                    'thumbnail': {
                        'resolutions': [
                            {'url': 'https://example.com/thumb1.jpg'}
                        ]
                    }
                }
            },
            {
                'id': 'article-2',
                'content': {
                    'id': 'article-2',
                    'title': 'Apple Stock Rises',
                    'contentType': 'VIDEO',
                    'pubDate': '2025-10-30T12:00:00Z',
                    'provider': {
                        'displayName': 'Bloomberg'
                    },
                    'canonicalUrl': {
                        'url': 'https://finance.yahoo.com/news/article-2.html'
                    }
                }
            }
        ]
        mock_ticker.news = mock_news
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetNewsRequest(ticker="AAPL", count=5)
        
        response = servicer.GetNews(request, context)
        
        assert len(response.articles) == 2
        assert response.articles[0].title == 'Apple Reports Strong Earnings'
        assert response.articles[0].publisher == 'Yahoo Finance'
        assert response.articles[0].type == 'STORY'
        assert response.articles[0].link == 'https://finance.yahoo.com/news/article-1.html'
        assert response.articles[0].thumbnail == 'https://example.com/thumb1.jpg'

    @patch('src.server.yf.Ticker')
    def test_get_news_respects_count(self, mock_ticker_class):
        """Test that GetNews respects the count parameter"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        # Create 10 mock articles
        mock_news = []
        for i in range(10):
            mock_news.append({
                'id': f'article-{i}',
                'content': {
                    'id': f'article-{i}',
                    'title': f'Article {i}',
                    'contentType': 'STORY',
                    'pubDate': '2025-10-31T14:20:57Z',
                    'provider': {'displayName': 'Yahoo Finance'},
                    'canonicalUrl': {'url': f'https://example.com/{i}'}
                }
            })
        mock_ticker.news = mock_news
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetNewsRequest(ticker="AAPL", count=3)
        
        response = servicer.GetNews(request, context)
        
        # Should only return 3 articles
        assert len(response.articles) == 3


class TestTickerServiceGetOptions:
    """Test GetOptions endpoint"""

    @patch('src.server.yf.Ticker')
    def test_get_options_success(self, mock_ticker_class):
        """Test successful GetOptions call"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.options = ('2025-11-15', '2025-12-20', '2026-01-17')
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetOptionsRequest(ticker="AAPL")
        
        response = servicer.GetOptions(request, context)
        
        assert len(response.expiration_dates) == 3
        assert '2025-11-15' in response.expiration_dates


class TestTickerServiceGetOptionChain:
    """Test GetOptionChain endpoint"""

    @patch('src.server.yf.Ticker')
    def test_get_option_chain_success(self, mock_ticker_class):
        """Test successful GetOptionChain call"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        
        # Mock option chain data
        mock_calls = pd.DataFrame({
            'strike': [100.0, 110.0],
            'lastPrice': [10.5, 5.2],
            'bid': [10.4, 5.1],
            'ask': [10.6, 5.3],
            'volume': [1000, 500],
            'openInterest': [5000, 2500],
            'impliedVolatility': [0.25, 0.28]
        })
        
        mock_puts = pd.DataFrame({
            'strike': [100.0, 110.0],
            'lastPrice': [2.5, 5.2],
            'bid': [2.4, 5.1],
            'ask': [2.6, 5.3],
            'volume': [800, 600],
            'openInterest': [4000, 3000],
            'impliedVolatility': [0.22, 0.26]
        })
        
        mock_chain = Mock()
        mock_chain.calls = mock_calls
        mock_chain.puts = mock_puts
        mock_ticker.option_chain.return_value = mock_chain
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetOptionChainRequest(
            ticker="AAPL",
            date="2025-11-15"  # Field name is 'date', not 'expiration_date'
        )
        
        response = servicer.GetOptionChain(request, context)
        
        assert len(response.calls) == 2
        assert len(response.puts) == 2
        assert response.calls[0].strike == 100.0
        assert response.calls[0].last_price == 10.5
        assert response.puts[0].strike == 100.0
        assert response.puts[0].last_price == 2.5


class TestTickerServiceGetMultipleInfo:
    """Test GetMultipleInfo endpoint"""

    @patch('src.server.yf.Tickers')
    def test_get_multiple_info_success(self, mock_tickers_class):
        """Test successful GetMultipleInfo call"""
        # Setup mock
        mock_tickers = Mock()
        mock_tickers_class.return_value = mock_tickers
        
        # Create mock ticker objects
        mock_aapl = Mock()
        mock_aapl.info = {
            'symbol': 'AAPL',
            'longName': 'Apple Inc.',
            'currentPrice': 150.0,
            'marketCap': 2500000000000,
        }
        
        mock_msft = Mock()
        mock_msft.info = {
            'symbol': 'MSFT',
            'longName': 'Microsoft Corporation',
            'currentPrice': 300.0,
            'marketCap': 2200000000000,
        }
        
        mock_tickers.tickers = {
            'AAPL': mock_aapl,
            'MSFT': mock_msft,
        }
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetMultipleInfoRequest(tickers=["AAPL", "MSFT"])
        
        response = servicer.GetMultipleInfo(request, context)
        
        assert len(response.info) == 2
        assert 'AAPL' in response.info
        assert 'MSFT' in response.info
        assert response.info['AAPL'].long_name == 'Apple Inc.'
        assert response.info['MSFT'].long_name == 'Microsoft Corporation'


class TestTickerServiceDownloadHistory:
    """Test DownloadHistory endpoint"""

    @patch('src.server.yf.download')
    def test_download_history_single_ticker(self, mock_download):
        """Test DownloadHistory with a single ticker"""
        # Setup mock
        dates = pd.date_range('2025-01-01', periods=3, freq='D')
        mock_data = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [105.0, 106.0, 107.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [104.0, 105.0, 106.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=dates)
        mock_download.return_value = mock_data
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.DownloadHistoryRequest(
            tickers=["AAPL"],
            period="3d",
            interval="1d"
        )
        
        # Collect streaming responses
        responses = list(servicer.DownloadHistory(request, context))
        
        assert len(responses) == 1
        assert responses[0].ticker == 'AAPL'
        assert len(responses[0].rows) == 3
        assert responses[0].rows[0].open == 100.0

    @patch('src.server.yf.download')
    def test_download_history_multiple_tickers(self, mock_download):
        """Test DownloadHistory with multiple tickers"""
        # Setup mock - multi-level columns
        dates = pd.date_range('2025-01-01', periods=2, freq='D')
        mock_data = pd.DataFrame({
            ('AAPL', 'Open'): [100.0, 101.0],
            ('AAPL', 'High'): [105.0, 106.0],
            ('AAPL', 'Low'): [99.0, 100.0],
            ('AAPL', 'Close'): [104.0, 105.0],
            ('AAPL', 'Volume'): [1000000, 1100000],
            ('MSFT', 'Open'): [200.0, 201.0],
            ('MSFT', 'High'): [205.0, 206.0],
            ('MSFT', 'Low'): [199.0, 200.0],
            ('MSFT', 'Close'): [204.0, 205.0],
            ('MSFT', 'Volume'): [2000000, 2100000],
        }, index=dates)
        mock_download.return_value = mock_data
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.DownloadHistoryRequest(
            tickers=["AAPL", "MSFT"],
            period="2d",
            interval="1d"
        )
        
        # Collect streaming responses
        responses = list(servicer.DownloadHistory(request, context))
        
        assert len(responses) == 2
        tickers = [r.ticker for r in responses]
        assert 'AAPL' in tickers
        assert 'MSFT' in tickers


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
