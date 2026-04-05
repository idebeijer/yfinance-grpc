"""Unit tests for MarketService (GetMarketStatus and GetMarketSummary RPCs)."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timezone

import pytest
import grpc

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

from src.market_server import MarketServiceServicer
from yfinance_grpc.v1alpha1 import market_pb2


class TestMarketServiceGetMarketStatus:
    @patch("src.market_server.yf.Market")
    def test_get_market_status_success(self, mock_market_cls):
        mock_market = Mock()
        mock_market_cls.return_value = mock_market
        mock_market.status = {
            "type": "REGULAR",
            "open": datetime(2025, 1, 15, 9, 30, tzinfo=timezone.utc),
            "close": datetime(2025, 1, 15, 16, 0, tzinfo=timezone.utc),
            "timezone": {"short": "EST", "gmtoffset": -18000000},
        }

        response = MarketServiceServicer().GetMarketStatus(
            market_pb2.GetMarketStatusRequest(market="us_market"), Mock()
        )

        mock_market_cls.assert_called_once_with("us_market")
        assert response.status.market_type == "REGULAR"
        assert response.status.timezone_short == "EST"
        assert response.status.timezone_gmtoffset == -18000000
        assert response.status.open.seconds > 0
        assert response.status.close.seconds > 0

    def test_get_market_status_empty_market_returns_invalid_argument(self):
        context = Mock()
        MarketServiceServicer().GetMarketStatus(
            market_pb2.GetMarketStatusRequest(market=""), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)

    @patch("src.market_server.yf.Market")
    def test_get_market_status_no_data_returns_not_found(self, mock_market_cls):
        mock_market = Mock()
        mock_market_cls.return_value = mock_market
        mock_market.status = None

        context = Mock()
        MarketServiceServicer().GetMarketStatus(
            market_pb2.GetMarketStatusRequest(market="xx_market"), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.NOT_FOUND)

    @patch("src.market_server.yf.Market")
    def test_get_market_status_exception_returns_internal_error(self, mock_market_cls):
        mock_market_cls.side_effect = Exception("API error")
        context = Mock()
        MarketServiceServicer().GetMarketStatus(
            market_pb2.GetMarketStatusRequest(market="us_market"), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)


class TestMarketServiceGetMarketSummary:
    @patch("src.market_server.yf.Market")
    def test_get_market_summary_success(self, mock_market_cls):
        mock_market = Mock()
        mock_market_cls.return_value = mock_market
        mock_market.summary = {
            "^GSPC": {
                "shortName": "S&P 500",
                "regularMarketPrice": 4800.0,
                "regularMarketChange": 25.5,
                "regularMarketChangePercent": 0.53,
            },
            "^DJI": {
                "shortName": "Dow Jones",
                "regularMarketPrice": 37500.0,
                "regularMarketChange": -50.0,
                "regularMarketChangePercent": -0.13,
            },
        }

        response = MarketServiceServicer().GetMarketSummary(
            market_pb2.GetMarketSummaryRequest(market="us_market"), Mock()
        )

        mock_market_cls.assert_called_once_with("us_market")
        assert "^GSPC" in response.summary
        assert response.summary["^GSPC"].short_name == "S&P 500"
        assert response.summary["^GSPC"].regular_market_price == 4800.0
        assert response.summary["^GSPC"].regular_market_change == 25.5
        assert response.summary["^GSPC"].regular_market_change_percent == 0.53
        assert "^DJI" in response.summary
        assert response.summary["^DJI"].regular_market_change == -50.0

    def test_get_market_summary_empty_market_returns_invalid_argument(self):
        context = Mock()
        MarketServiceServicer().GetMarketSummary(
            market_pb2.GetMarketSummaryRequest(market=""), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)

    @patch("src.market_server.yf.Market")
    def test_get_market_summary_no_data_returns_empty_response(self, mock_market_cls):
        mock_market = Mock()
        mock_market_cls.return_value = mock_market
        mock_market.summary = None

        response = MarketServiceServicer().GetMarketSummary(
            market_pb2.GetMarketSummaryRequest(market="us_market"), Mock()
        )

        assert len(response.summary) == 0

    @patch("src.market_server.yf.Market")
    def test_get_market_summary_finance_error_key_returns_empty_response(self, mock_market_cls):
        mock_market = Mock()
        mock_market_cls.return_value = mock_market
        mock_market.summary = {"finance": {"result": None, "error": {"code": "Bad Request", "description": "invalid broad market region"}}}

        response = MarketServiceServicer().GetMarketSummary(
            market_pb2.GetMarketSummaryRequest(market="us_market"), Mock()
        )

        assert len(response.summary) == 0

    @patch("src.market_server.yf.Market")
    def test_get_market_summary_exception_returns_internal_error(self, mock_market_cls):
        mock_market_cls.side_effect = Exception("API error")
        context = Mock()
        MarketServiceServicer().GetMarketSummary(
            market_pb2.GetMarketSummaryRequest(market="us_market"), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)
