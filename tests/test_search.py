"""Unit tests for SearchService (Search and Lookup RPCs)."""

from unittest.mock import ANY, Mock, patch

import grpc
import pandas as pd
import pytest
from yfinance_grpc.v1alpha1 import search_pb2

from yfinance_grpc_server.search import SearchServiceServicer


class TestSearchServiceSearch:
    @patch("yfinance_grpc_server.search.yf.Search")
    def test_search_success(self, mock_search_cls):
        mock_result = Mock()
        mock_result.quotes = [
            {
                "symbol": "AAPL",
                "shortName": "Apple Inc.",
                "longName": "Apple Inc.",
                "exchange": "NMS",
                "quoteType": "EQUITY",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "typeDisp": "Equity",
                "score": 1893881.0,
            }
        ]
        mock_result.news = [
            {
                "id": "abc123",
                "title": "Apple Reports Record Revenue",
                "publisher": "Reuters",
                "link": "https://example.com",
                "providerPublishTime": 1704067200,
                "type": "STORY",
            }
        ]
        mock_search_cls.return_value = mock_result

        servicer = SearchServiceServicer()
        context = Mock()
        request = search_pb2.SearchRequest(query="Apple", max_results=5, news_count=3)

        response = servicer.Search(request, context)

        mock_search_cls.assert_called_once_with(
            query="Apple", max_results=5, news_count=3, enable_fuzzy_query=False
        )
        assert len(response.quotes) == 1
        assert response.quotes[0].symbol == "AAPL"
        assert response.quotes[0].short_name == "Apple Inc."
        assert response.quotes[0].exchange == "NMS"
        assert response.quotes[0].quote_type == "EQUITY"
        assert response.quotes[0].sector == "Technology"
        assert response.quotes[0].score == 1893881.0

        assert len(response.news) == 1
        assert response.news[0].uuid == "abc123"
        assert response.news[0].title == "Apple Reports Record Revenue"
        assert response.news[0].publisher == "Reuters"
        assert response.news[0].provider_publish_time.seconds == 1704067200

    @patch("yfinance_grpc_server.search.yf.Search")
    def test_search_defaults_max_results_and_news_count(self, mock_search_cls):
        mock_result = Mock()
        mock_result.quotes = []
        mock_result.news = []
        mock_search_cls.return_value = mock_result

        # max_results=0 and news_count=0 should fall back to defaults (8)
        SearchServiceServicer().Search(search_pb2.SearchRequest(query="Apple"), Mock())

        mock_search_cls.assert_called_once_with(
            query="Apple", max_results=8, news_count=8, enable_fuzzy_query=False
        )

    def test_search_empty_query_returns_invalid_argument(self):
        context = Mock()
        SearchServiceServicer().Search(search_pb2.SearchRequest(query=""), context)
        context.abort.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT, ANY)

    @patch("yfinance_grpc_server.search.yf.Search")
    def test_search_exception_returns_internal_error(self, mock_search_cls):
        mock_search_cls.side_effect = Exception("network error")
        context = Mock()
        SearchServiceServicer().Search(search_pb2.SearchRequest(query="Apple"), context)
        context.abort.assert_called_once_with(grpc.StatusCode.INTERNAL, ANY)

    @patch("yfinance_grpc_server.search.yf.Search")
    def test_search_empty_results(self, mock_search_cls):
        mock_result = Mock()
        mock_result.quotes = []
        mock_result.news = []
        mock_search_cls.return_value = mock_result

        response = SearchServiceServicer().Search(search_pb2.SearchRequest(query="xyzxyzxyz"), Mock())

        assert response.quotes == []
        assert response.news == []


class TestSearchServiceLookup:
    @patch("yfinance_grpc_server.search.yf.Lookup")
    def test_lookup_success(self, mock_lookup_cls):
        mock_lookup = Mock()
        mock_lookup_cls.return_value = mock_lookup
        mock_lookup.get_stock.return_value = pd.DataFrame(
            {
                "shortName": ["Apple Inc."],
                "exchange": ["NMS"],
                "quoteType": ["EQUITY"],
                "score": [1893881.0],
            },
            index=pd.Index(["AAPL"], name="symbol"),
        )

        context = Mock()
        request = search_pb2.LookupRequest(query="Apple", type=search_pb2.LOOKUP_TYPE_EQUITY, count=10)

        response = SearchServiceServicer().Lookup(request, context)

        mock_lookup.get_stock.assert_called_once_with(count=10)
        assert len(response.results) == 1
        assert response.results[0].symbol == "AAPL"
        assert response.results[0].name == "Apple Inc."
        assert response.results[0].exchange == "NMS"
        assert response.results[0].quote_type == "EQUITY"
        assert response.results[0].score == 1893881.0

    @patch("yfinance_grpc_server.search.yf.Lookup")
    def test_lookup_type_all_is_default(self, mock_lookup_cls):
        mock_lookup = Mock()
        mock_lookup_cls.return_value = mock_lookup
        mock_lookup.get_all.return_value = pd.DataFrame()

        SearchServiceServicer().Lookup(search_pb2.LookupRequest(query="Apple"), Mock())

        mock_lookup.get_all.assert_called_once_with(count=25)

    @pytest.mark.parametrize(
        ("pb_type", "method"),
        [
            (search_pb2.LOOKUP_TYPE_ALL, "get_all"),
            (search_pb2.LOOKUP_TYPE_EQUITY, "get_stock"),
            (search_pb2.LOOKUP_TYPE_MUTUALFUND, "get_mutualfund"),
            (search_pb2.LOOKUP_TYPE_ETF, "get_etf"),
            (search_pb2.LOOKUP_TYPE_INDEX, "get_index"),
            (search_pb2.LOOKUP_TYPE_FUTURE, "get_future"),
            (search_pb2.LOOKUP_TYPE_CURRENCY, "get_currency"),
            (search_pb2.LOOKUP_TYPE_CRYPTOCURRENCY, "get_cryptocurrency"),
        ],
    )
    @patch("yfinance_grpc_server.search.yf.Lookup")
    def test_lookup_type_calls_public_method(self, mock_lookup_cls, pb_type, method):
        mock_lookup = mock_lookup_cls.return_value
        getattr(mock_lookup, method).return_value = pd.DataFrame()

        SearchServiceServicer().Lookup(search_pb2.LookupRequest(query="test", type=pb_type, count=5), Mock())

        getattr(mock_lookup, method).assert_called_once_with(count=5)

    def test_lookup_empty_query_returns_invalid_argument(self):
        context = Mock()
        SearchServiceServicer().Lookup(search_pb2.LookupRequest(query=""), context)
        context.abort.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT, ANY)

    @patch("yfinance_grpc_server.search.yf.Lookup")
    def test_lookup_exception_returns_internal_error(self, mock_lookup_cls):
        mock_lookup_cls.side_effect = Exception("API error")
        context = Mock()
        SearchServiceServicer().Lookup(search_pb2.LookupRequest(query="Apple"), context)
        context.abort.assert_called_once_with(grpc.StatusCode.INTERNAL, ANY)
