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
from yfinance_grpc.v1alpha1 import ticker_pb2


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
        dates = pd.date_range('2024-01-01', periods=4, freq='QE')
        mock_dividends = pd.Series([0.25, 0.25, 0.26, 0.26], index=dates)
        # get_dividends should return the series
        mock_ticker.get_dividends.return_value = mock_dividends
        
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetDividendsRequest(ticker="AAPL", period="1y")
        
        response = servicer.GetDividends(request, context)
        
        assert len(response.rows) == 4
        assert response.rows[0].amount == 0.25
        mock_ticker.get_dividends.assert_called_once_with(period="1y")


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
    def test_get_news_thumbnail_fallback(self, mock_ticker_class):
        """Test GetNews uses originalUrl when resolutions list is absent"""
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker

        mock_news = [
            {
                'id': 'article-1',
                'content': {
                    'id': 'article-1',
                    'title': 'Fallback Thumbnail Test',
                    'contentType': 'STORY',
                    'pubDate': '2025-10-31T14:20:57Z',
                    'provider': {'displayName': 'Test Publisher'},
                    'canonicalUrl': {'url': 'https://example.com/article'},
                    'thumbnail': {
                        'originalUrl': 'https://example.com/original.jpg'
                        # no 'resolutions' key
                    }
                }
            }
        ]
        mock_ticker.news = mock_news

        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetNewsRequest(ticker="AAPL", count=5)

        response = servicer.GetNews(request, context)

        assert len(response.articles) == 1
        assert response.articles[0].thumbnail == 'https://example.com/original.jpg'

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


class TestTickerServiceGetCapitalGains:
    @patch('src.server.yf.Ticker')
    def test_get_capital_gains_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        dates = pd.date_range('2024-01-01', periods=2, freq='QE')
        mock_ticker.get_capital_gains.return_value = pd.Series([0.1, 0.2], index=dates)

        servicer = TickerServiceServicer()
        response = servicer.GetCapitalGains(
            ticker_pb2.GetCapitalGainsRequest(ticker="SPY", period="1y"), Mock()
        )

        assert len(response.rows) == 2
        assert response.rows[0].amount == pytest.approx(0.1)
        mock_ticker.get_capital_gains.assert_called_once_with(period="1y")


class TestTickerServiceGetSharesHistory:
    @patch('src.server.yf.Ticker')
    def test_get_shares_history_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        dates = pd.date_range('2024-01-01', periods=3, freq='QE')
        mock_ticker.get_shares_full.return_value = pd.Series([1_000_000, 1_050_000, 1_100_000], index=dates)

        servicer = TickerServiceServicer()
        response = servicer.GetSharesHistory(
            ticker_pb2.GetSharesHistoryRequest(ticker="AAPL"), Mock()
        )

        assert len(response.rows) == 3
        assert response.rows[0].shares == 1_000_000


class TestTickerServiceGetIsin:
    @patch('src.server.yf.Ticker')
    def test_get_isin_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.get_isin.return_value = "US0378331005"

        servicer = TickerServiceServicer()
        response = servicer.GetIsin(ticker_pb2.GetIsinRequest(ticker="AAPL"), Mock())

        assert response.isin == "US0378331005"

    @patch('src.server.yf.Ticker')
    def test_get_isin_none_returns_empty_string(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.get_isin.return_value = None

        servicer = TickerServiceServicer()
        response = servicer.GetIsin(ticker_pb2.GetIsinRequest(ticker="AAPL"), Mock())

        assert response.isin == ""


class TestTickerServiceGetFastInfo:
    @patch('src.server.yf.Ticker')
    def test_get_fast_info_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        fi = Mock()
        # Set all numeric/string attributes to avoid Mock objects reaching safe_int/safe_float
        fi.currency = "USD"
        fi.exchange = "NMS"
        fi.exchange_data_delayed_by = 0
        fi.exchange_timezone_name = "America/New_York"
        fi.last_price = 175.5
        fi.last_volume = 50_000_000
        fi.market_cap = 2_500_000_000_000
        fi.open = 174.0
        fi.previous_close = 173.5
        fi.quote_type = "EQUITY"
        fi.regular_market_day_high = 176.0
        fi.regular_market_day_low = 173.0
        fi.regular_market_previous_close = 173.5
        fi.regular_market_price = 175.5
        fi.shares = 15_000_000_000
        fi.three_month_average_volume = 55_000_000.0
        fi.timezone = "EST"
        fi.fifty_day_average = 172.0
        fi.two_hundred_day_average = 165.0
        fi.year_change = 0.15
        fi.year_high = 200.0
        fi.year_low = 130.0
        mock_ticker.get_fast_info.return_value = fi

        servicer = TickerServiceServicer()
        response = servicer.GetFastInfo(ticker_pb2.GetFastInfoRequest(ticker="AAPL"), Mock())

        assert response.info.currency == "USD"
        assert response.info.last_price == pytest.approx(175.5)
        assert response.info.market_cap == 2_500_000_000_000
        assert response.info.quote_type == "EQUITY"


class TestTickerServiceGetSustainability:
    @patch('src.server.yf.Ticker')
    def test_get_sustainability_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.get_sustainability.return_value = {
            'totalEsg': 16.5,
            'esgPerformance': 'AVG_PERF',
            'environmentScore': 3.5,
            'socialScore': 8.5,
            'governanceScore': 4.5,
            'percentile': 42.0,
            'peerGroup': 'Technology Hardware',
            'adult': False,
            'coal': False,
            'tobacco': True,
        }

        servicer = TickerServiceServicer()
        response = servicer.GetSustainability(
            ticker_pb2.GetSustainabilityRequest(ticker="AAPL"), Mock()
        )

        assert response.total_esg == pytest.approx(16.5)
        assert response.esg_performance == 'AVG_PERF'
        assert response.environment_score == pytest.approx(3.5)
        assert response.tobacco is True
        assert response.coal is False

    @patch('src.server.yf.Ticker')
    def test_get_sustainability_no_data(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.get_sustainability.return_value = None

        servicer = TickerServiceServicer()
        response = servicer.GetSustainability(
            ticker_pb2.GetSustainabilityRequest(ticker="AAPL"), Mock()
        )

        assert response.total_esg == 0.0


class TestTickerServiceGetInsiderPurchases:
    @patch('src.server.yf.Ticker')
    def test_get_insider_purchases_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        data = pd.DataFrame(
            {'Shares': [5000, 12000], 'Trans': [2, 3]},
            index=['Purchases', 'Sales']
        )
        mock_ticker.get_insider_purchases.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetInsiderPurchases(
            ticker_pb2.GetInsiderPurchasesRequest(ticker="AAPL"), Mock()
        )

        assert len(response.rows) == 2
        labels = [r.label for r in response.rows]
        assert 'Purchases' in labels


class TestTickerServiceGetInsiderTransactions:
    @patch('src.server.yf.Ticker')
    def test_get_insider_transactions_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        dates = pd.DatetimeIndex(['2024-01-15', '2024-02-20'])
        data = pd.DataFrame({
            'Start Date': dates,
            'Insider': ['John Doe', 'Jane Smith'],
            'Position': ['CEO', 'CFO'],
            'Transaction': ['Sale', 'Purchase'],
            'Shares': [10000, 5000],
            'Value': [1_750_000.0, 875_000.0],
            'Text': ['Sold shares', 'Bought shares'],
            'URL': ['https://example.com/1', 'https://example.com/2'],
        }, index=dates)
        mock_ticker.get_insider_transactions.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetInsiderTransactions(
            ticker_pb2.GetInsiderTransactionsRequest(ticker="AAPL"), Mock()
        )

        assert len(response.transactions) == 2
        assert response.transactions[0].insider == 'John Doe'
        assert response.transactions[0].shares == 10000


class TestTickerServiceGetInsiderRosterHolders:
    @patch('src.server.yf.Ticker')
    def test_get_insider_roster_holders_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        data = pd.DataFrame({
            'Name': ['Tim Cook', 'Luca Maestri'],
            'Position': ['CEO', 'CFO'],
            'URL': ['https://example.com/1', 'https://example.com/2'],
            'Most Recent Transaction': pd.to_datetime(['2024-01-15', '2024-02-20']),
            'Latest Transaction Shares': [5000, 3000],
        })
        mock_ticker.get_insider_roster_holders.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetInsiderRosterHolders(
            ticker_pb2.GetInsiderRosterHoldersRequest(ticker="AAPL"), Mock()
        )

        assert len(response.holders) == 2
        assert response.holders[0].name == 'Tim Cook'
        assert response.holders[0].position == 'CEO'
        assert response.holders[0].latest_transaction_shares == 5000


class TestTickerServiceGetAnalystPriceTargets:
    @patch('src.server.yf.Ticker')
    def test_get_analyst_price_targets_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.get_analyst_price_targets.return_value = {
            'current': 175.0,
            'low': 140.0,
            'high': 220.0,
            'mean': 185.0,
            'median': 183.0,
        }

        servicer = TickerServiceServicer()
        response = servicer.GetAnalystPriceTargets(
            ticker_pb2.GetAnalystPriceTargetsRequest(ticker="AAPL"), Mock()
        )

        assert response.current == pytest.approx(175.0)
        assert response.low == pytest.approx(140.0)
        assert response.high == pytest.approx(220.0)
        assert response.mean == pytest.approx(185.0)
        assert response.median == pytest.approx(183.0)


class TestTickerServiceGetRecommendationsSummary:
    @patch('src.server.yf.Ticker')
    def test_get_recommendations_summary_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        data = pd.DataFrame({
            'strongBuy': [15, 14],
            'buy': [20, 18],
            'hold': [8, 9],
            'sell': [2, 3],
            'strongSell': [0, 1],
        }, index=['0m', '-1m'])

        mock_ticker.get_recommendations.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetRecommendationsSummary(
            ticker_pb2.GetRecommendationsSummaryRequest(ticker="AAPL"), Mock()
        )

        assert len(response.rows) == 2
        assert response.rows[0].period == '0m'
        assert response.rows[0].strong_buy == 15
        assert response.rows[0].buy == 20


class TestTickerServiceGetEarningsEstimate:
    @patch('src.server.yf.Ticker')
    def test_get_earnings_estimate_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        data = pd.DataFrame({
            'numberOfAnalysts': [30, 28],
            'avg': [1.55, 6.80],
            'low': [1.40, 6.20],
            'high': [1.70, 7.30],
            'yearAgoEps': [1.46, 6.43],
            'growth': [0.062, 0.058],
        }, index=['0q', '0y'])
        mock_ticker.get_earnings_estimate.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetEarningsEstimate(
            ticker_pb2.GetEarningsEstimateRequest(ticker="AAPL"), Mock()
        )

        assert len(response.rows) == 2
        assert response.rows[0].period == '0q'
        assert response.rows[0].number_of_analysts == 30
        assert response.rows[0].avg == pytest.approx(1.55)


class TestTickerServiceGetRevenueEstimate:
    @patch('src.server.yf.Ticker')
    def test_get_revenue_estimate_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        data = pd.DataFrame({
            'numberOfAnalysts': [25, 22],
            'avg': [94_000_000_000.0, 410_000_000_000.0],
            'low': [90_000_000_000.0, 390_000_000_000.0],
            'high': [98_000_000_000.0, 430_000_000_000.0],
            'yearAgoRevenue': [89_498_000_000.0, 383_285_000_000.0],
            'growth': [0.051, 0.070],
        }, index=['0q', '0y'])
        mock_ticker.get_revenue_estimate.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetRevenueEstimate(
            ticker_pb2.GetRevenueEstimateRequest(ticker="AAPL"), Mock()
        )

        assert len(response.rows) == 2
        assert response.rows[0].period == '0q'
        assert response.rows[0].number_of_analysts == 25


class TestTickerServiceGetEarningsHistory:
    @patch('src.server.yf.Ticker')
    def test_get_earnings_history_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        dates = pd.DatetimeIndex(['2023-10-26', '2024-01-25'])
        data = pd.DataFrame({
            'epsEstimate': [1.39, 2.10],
            'epsActual': [1.46, 2.18],
            'epsDifference': [0.07, 0.08],
            'surprisePercent': [5.04, 3.81],
        }, index=dates)
        mock_ticker.get_earnings_history.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetEarningsHistory(
            ticker_pb2.GetEarningsHistoryRequest(ticker="AAPL"), Mock()
        )

        assert len(response.rows) == 2
        assert response.rows[0].eps_estimate == pytest.approx(1.39)
        assert response.rows[0].eps_actual == pytest.approx(1.46)
        assert response.rows[0].surprise_percent == pytest.approx(5.04)


class TestTickerServiceGetEpsTrend:
    @patch('src.server.yf.Ticker')
    def test_get_eps_trend_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        data = pd.DataFrame({
            'current': [1.55, 6.80],
            '7daysAgo': [1.54, 6.79],
            '30daysAgo': [1.53, 6.75],
            '60daysAgo': [1.51, 6.70],
            '90daysAgo': [1.50, 6.65],
        }, index=['0q', '0y'])
        mock_ticker.get_eps_trend.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetEpsTrend(
            ticker_pb2.GetEpsTrendRequest(ticker="AAPL"), Mock()
        )

        assert len(response.rows) == 2
        assert response.rows[0].period == '0q'
        assert response.rows[0].current == pytest.approx(1.55)
        assert response.rows[0].seven_days_ago == pytest.approx(1.54)
        assert response.rows[0].ninety_days_ago == pytest.approx(1.50)


class TestTickerServiceGetEpsRevisions:
    @patch('src.server.yf.Ticker')
    def test_get_eps_revisions_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        data = pd.DataFrame({
            'upLast7days': [3, 5],
            'upLast30days': [8, 12],
            'downLast7days': [1, 2],
            'downLast30days': [2, 3],
        }, index=['0q', '0y'])
        mock_ticker.get_eps_revisions.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetEpsRevisions(
            ticker_pb2.GetEpsRevisionsRequest(ticker="AAPL"), Mock()
        )

        assert len(response.rows) == 2
        assert response.rows[0].period == '0q'
        assert response.rows[0].up_last_7days == 3
        assert response.rows[0].down_last_30days == 2


class TestTickerServiceGetGrowthEstimates:
    @patch('src.server.yf.Ticker')
    def test_get_growth_estimates_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        data = pd.DataFrame({
            'stock': [0.062, 0.058, 0.120, 0.150],
            'industry': [0.045, 0.050, 0.095, 0.110],
            'sector': [0.040, 0.045, 0.090, 0.100],
            'index': [0.035, 0.038, 0.080, 0.095],
        }, index=['0q', '+1q', '0y', '+1y'])
        mock_ticker.get_growth_estimates.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetGrowthEstimates(
            ticker_pb2.GetGrowthEstimatesRequest(ticker="AAPL"), Mock()
        )

        assert len(response.rows) == 4
        assert response.rows[0].period == '0q'
        assert response.rows[0].stock == pytest.approx(0.062)
        assert response.rows[0].industry == pytest.approx(0.045)


class TestTickerServiceGetEarningsDates:
    @patch('src.server.yf.Ticker')
    def test_get_earnings_dates_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        dates = pd.DatetimeIndex(['2024-10-31', '2025-01-30'])
        data = pd.DataFrame({
            'EPS Estimate': [1.55, float('nan')],
            'Reported EPS': [1.64, float('nan')],
            'Surprise(%)': [5.81, float('nan')],
        }, index=dates)
        mock_ticker.get_earnings_dates.return_value = data

        servicer = TickerServiceServicer()
        response = servicer.GetEarningsDates(
            ticker_pb2.GetEarningsDatesRequest(ticker="AAPL", limit=12), Mock()
        )

        assert len(response.rows) == 2
        # Past date has data
        assert response.rows[0].HasField('eps_estimate')
        assert response.rows[0].eps_estimate == pytest.approx(1.55)
        assert response.rows[0].reported_eps == pytest.approx(1.64)
        # Future date has no data
        assert not response.rows[1].HasField('eps_estimate')

        mock_ticker.get_earnings_dates.assert_called_once_with(limit=12)

    @patch('src.server.yf.Ticker')
    def test_get_earnings_dates_default_limit(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.get_earnings_dates.return_value = pd.DataFrame()

        servicer = TickerServiceServicer()
        servicer.GetEarningsDates(ticker_pb2.GetEarningsDatesRequest(ticker="AAPL"), Mock())

        mock_ticker.get_earnings_dates.assert_called_once_with(limit=12)


class TestTickerServiceGetHistoryMetadata:
    @patch('src.server.yf.Ticker')
    def test_get_history_metadata_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.get_history_metadata.return_value = {
            'currency': 'USD',
            'symbol': 'AAPL',
            'exchangeName': 'NMS',
            'fullExchangeName': 'NasdaqGS',
            'instrumentType': 'EQUITY',
            'firstTradeDate': 345479400,
            'regularMarketTime': 1704067200,
            'hasPrePostMarketData': True,
            'gmtoffset': -18000,
            'timezone': 'EST',
            'exchangeTimezoneName': 'America/New_York',
            'regularMarketPrice': 175.0,
            'fiftyTwoWeekHigh': 200.0,
            'fiftyTwoWeekLow': 130.0,
            'dataGranularity': '1d',
            'range': '',
            'validRanges': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
        }

        servicer = TickerServiceServicer()
        response = servicer.GetHistoryMetadata(
            ticker_pb2.GetHistoryMetadataRequest(ticker="AAPL"), Mock()
        )

        assert response.currency == 'USD'
        assert response.symbol == 'AAPL'
        assert response.exchange_name == 'NMS'
        assert response.instrument_type == 'EQUITY'
        assert response.has_pre_post_market_data is True
        assert response.gmt_offset == -18000
        assert 'max' in response.valid_ranges


class TestTickerServiceGetSecFilings:
    @patch('src.server.yf.Ticker')
    def test_get_sec_filings_success(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.get_sec_filings.return_value = {
            'filings': [
                {
                    'date': '2024-11-01',
                    'type': '10-K',
                    'title': 'Annual Report',
                    'edgarUrl': 'https://www.sec.gov/Archives/edgar/data/320193/000032019324000123',
                },
                {
                    'date': '2024-08-02',
                    'type': '10-Q',
                    'title': 'Quarterly Report',
                    'edgarUrl': 'https://www.sec.gov/Archives/edgar/data/320193/000032019324000099',
                },
            ]
        }

        servicer = TickerServiceServicer()
        response = servicer.GetSecFilings(
            ticker_pb2.GetSecFilingsRequest(ticker="AAPL"), Mock()
        )

        assert len(response.filings) == 2
        assert response.filings[0].type == '10-K'
        assert response.filings[0].title == 'Annual Report'
        assert 'sec.gov' in response.filings[0].url
        assert response.filings[0].date.seconds > 0

    @patch('src.server.yf.Ticker')
    def test_get_sec_filings_empty(self, mock_ticker_class):
        mock_ticker = Mock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.get_sec_filings.return_value = {}

        servicer = TickerServiceServicer()
        response = servicer.GetSecFilings(
            ticker_pb2.GetSecFilingsRequest(ticker="AAPL"), Mock()
        )

        assert len(response.filings) == 0


class TestTickerServiceEmptyTickers:
    """Test validation of empty tickers lists"""

    def test_download_history_empty_tickers_returns_invalid_argument(self):
        """Test DownloadHistory with empty tickers returns INVALID_ARGUMENT"""
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.DownloadHistoryRequest(
            tickers=[],
            period="1d",
            interval="1d"
        )

        responses = list(servicer.DownloadHistory(request, context))

        assert len(responses) == 0
        context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)
        context.set_details.assert_called_once()

    @patch('src.server.yf.Tickers')
    def test_get_multiple_info_empty_tickers_returns_invalid_argument(self, mock_tickers_class):
        """Test GetMultipleInfo with empty tickers returns INVALID_ARGUMENT without calling yfinance"""
        servicer = TickerServiceServicer()
        context = Mock()
        request = ticker_pb2.GetMultipleInfoRequest(tickers=[])

        servicer.GetMultipleInfo(request, context)

        context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)
        context.set_details.assert_called_once()
        mock_tickers_class.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
