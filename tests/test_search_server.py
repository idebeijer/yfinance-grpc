"""Unit tests for SearchService (Search and Lookup RPCs)."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import pandas as pd
import grpc

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

from src.search_server import SearchServiceServicer
from yfinance_grpc.v1 import search_pb2


class TestSearchServiceSearch:
    @patch("src.search_server.yf.Search")
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

    @patch("src.search_server.yf.Search")
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
        response = SearchServiceServicer().Search(
            search_pb2.SearchRequest(query=""), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)
        assert isinstance(response, search_pb2.SearchResponse)

    @patch("src.search_server.yf.Search")
    def test_search_exception_returns_internal_error(self, mock_search_cls):
        mock_search_cls.side_effect = Exception("network error")
        context = Mock()
        response = SearchServiceServicer().Search(
            search_pb2.SearchRequest(query="Apple"), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)
        assert isinstance(response, search_pb2.SearchResponse)

    @patch("src.search_server.yf.Search")
    def test_search_empty_results(self, mock_search_cls):
        mock_result = Mock()
        mock_result.quotes = []
        mock_result.news = []
        mock_search_cls.return_value = mock_result

        response = SearchServiceServicer().Search(
            search_pb2.SearchRequest(query="xyzxyzxyz"), Mock()
        )

        assert response.quotes == []
        assert response.news == []


class TestSearchServiceLookup:
    @patch("src.search_server.yf.Lookup")
    def test_lookup_success(self, mock_lookup_cls):
        mock_lookup = Mock()
        mock_lookup_cls.return_value = mock_lookup
        mock_lookup._get_data.return_value = pd.DataFrame(
            {
                "shortName": ["Apple Inc."],
                "exchange": ["NMS"],
                "quoteType": ["EQUITY"],
                "score": [1893881.0],
            },
            index=pd.Index(["AAPL"], name="symbol"),
        )

        context = Mock()
        request = search_pb2.LookupRequest(
            query="Apple", type=search_pb2.LOOKUP_TYPE_EQUITY, count=10
        )

        response = SearchServiceServicer().Lookup(request, context)

        mock_lookup._get_data.assert_called_once_with("equity", 10)
        assert len(response.results) == 1
        assert response.results[0].symbol == "AAPL"
        assert response.results[0].name == "Apple Inc."
        assert response.results[0].exchange == "NMS"
        assert response.results[0].quote_type == "EQUITY"
        assert response.results[0].score == 1893881.0

    @patch("src.search_server.yf.Lookup")
    def test_lookup_type_all_is_default(self, mock_lookup_cls):
        mock_lookup = Mock()
        mock_lookup_cls.return_value = mock_lookup
        mock_lookup._get_data.return_value = pd.DataFrame()

        SearchServiceServicer().Lookup(
            search_pb2.LookupRequest(query="Apple"), Mock()
        )

        mock_lookup._get_data.assert_called_once_with("all", 25)

    @patch("src.search_server.yf.Lookup")
    def test_lookup_all_type_variants(self, mock_lookup_cls):
        mock_lookup = Mock()
        mock_lookup_cls.return_value = mock_lookup
        mock_lookup._get_data.return_value = pd.DataFrame()
        servicer = SearchServiceServicer()

        type_map = {
            search_pb2.LOOKUP_TYPE_ALL: "all",
            search_pb2.LOOKUP_TYPE_EQUITY: "equity",
            search_pb2.LOOKUP_TYPE_MUTUALFUND: "mutualfund",
            search_pb2.LOOKUP_TYPE_ETF: "etf",
            search_pb2.LOOKUP_TYPE_INDEX: "index",
            search_pb2.LOOKUP_TYPE_FUTURE: "future",
            search_pb2.LOOKUP_TYPE_CURRENCY: "currency",
            search_pb2.LOOKUP_TYPE_CRYPTOCURRENCY: "cryptocurrency",
        }
        for pb_type, yf_str in type_map.items():
            mock_lookup._get_data.reset_mock()
            servicer.Lookup(
                search_pb2.LookupRequest(query="test", type=pb_type, count=5), Mock()
            )
            mock_lookup._get_data.assert_called_once_with(yf_str, 5)

    def test_lookup_empty_query_returns_invalid_argument(self):
        context = Mock()
        SearchServiceServicer().Lookup(search_pb2.LookupRequest(query=""), context)
        context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)

    @patch("src.search_server.yf.Lookup")
    def test_lookup_exception_returns_internal_error(self, mock_lookup_cls):
        mock_lookup_cls.side_effect = Exception("API error")
        context = Mock()
        SearchServiceServicer().Lookup(
            search_pb2.LookupRequest(query="Apple"), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)
