"""Unit tests for SectorService (GetSector and GetIndustry RPCs)."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import pandas as pd
import grpc

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

from src.sector_server import SectorServiceServicer
from yfinance_grpc.v1alpha1 import sector_pb2


class TestSectorServiceGetSector:
    @patch("src.sector_server.yf.Sector")
    def test_get_sector_success(self, mock_sector_cls):
        mock_sector = Mock()
        mock_sector_cls.return_value = mock_sector
        mock_sector.key = "technology"
        mock_sector.name = "Technology"
        mock_sector.symbol = "XLK"
        mock_sector.overview = {
            "companies_count": 75,
            "market_cap": 15000000000000.0,
            "description": "Technology sector",
            "industries_count": 8,
            "market_weight": 0.29,
            "employee_count": 2500000.0,
        }
        mock_sector.top_etfs = {"XLK": "Technology Select Sector SPDR"}
        mock_sector.top_mutual_funds = {"VITAX": "Vanguard IT Index"}
        mock_sector.top_companies = pd.DataFrame(
            {"name": ["Apple Inc."], "rating": ["Buy"], "market weight": [0.22]},
            index=pd.Index(["AAPL"], name="symbol"),
        )
        mock_sector.industries = pd.DataFrame(
            {"name": ["Consumer Electronics"], "symbol": ["XLK"], "market weight": [0.35]},
            index=pd.Index(["consumer-electronics"], name="key"),
        )

        response = SectorServiceServicer().GetSector(
            sector_pb2.GetSectorRequest(key="technology"), Mock()
        )

        mock_sector_cls.assert_called_once_with("technology")
        assert response.key == "technology"
        assert response.name == "Technology"
        assert response.symbol == "XLK"
        assert response.overview.companies_count == 75
        assert response.overview.market_weight == 0.29
        assert response.overview.description == "Technology sector"
        assert len(response.top_companies) == 1
        assert response.top_companies[0].symbol == "AAPL"
        assert response.top_companies[0].name == "Apple Inc."
        assert response.top_etfs["XLK"] == "Technology Select Sector SPDR"
        assert response.top_mutual_funds["VITAX"] == "Vanguard IT Index"
        assert len(response.industries) == 1
        assert response.industries[0].key == "consumer-electronics"
        assert response.industries[0].name == "Consumer Electronics"

    def test_get_sector_empty_key_returns_invalid_argument(self):
        context = Mock()
        SectorServiceServicer().GetSector(
            sector_pb2.GetSectorRequest(key=""), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)

    @patch("src.sector_server.yf.Sector")
    def test_get_sector_exception_returns_internal_error(self, mock_sector_cls):
        mock_sector_cls.side_effect = Exception("API error")
        context = Mock()
        SectorServiceServicer().GetSector(
            sector_pb2.GetSectorRequest(key="technology"), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)

    @patch("src.sector_server.yf.Sector")
    def test_get_sector_no_optional_data(self, mock_sector_cls):
        mock_sector = Mock()
        mock_sector_cls.return_value = mock_sector
        mock_sector.key = "technology"
        mock_sector.name = "Technology"
        mock_sector.symbol = "XLK"
        mock_sector.overview = {}
        mock_sector.top_etfs = {}
        mock_sector.top_mutual_funds = {}
        mock_sector.top_companies = None
        mock_sector.industries = None

        response = SectorServiceServicer().GetSector(
            sector_pb2.GetSectorRequest(key="technology"), Mock()
        )

        assert response.industries == []
        assert response.top_companies == []


class TestSectorServiceGetIndustry:
    @patch("src.sector_server.yf.Industry")
    def test_get_industry_success(self, mock_industry_cls):
        mock_industry = Mock()
        mock_industry_cls.return_value = mock_industry
        mock_industry.key = "consumer-electronics"
        mock_industry.name = "Consumer Electronics"
        mock_industry.symbol = "^CSELEC"
        mock_industry.sector_key = "technology"
        mock_industry.sector_name = "Technology"
        mock_industry.overview = {
            "companies_count": 20,
            "market_cap": 3500000000000.0,
            "description": "Consumer electronics industry",
            "industries_count": 0,
            "market_weight": 0.12,
            "employee_count": 800000.0,
        }
        mock_industry.top_companies = pd.DataFrame(
            {"name": ["Apple Inc."], "rating": ["Buy"], "market weight": [0.60]},
            index=pd.Index(["AAPL"], name="symbol"),
        )
        mock_industry.top_performing_companies = pd.DataFrame(
            {
                "name": ["Apple Inc."],
                "ytd return": [0.15],
                "last price": [185.0],
                "target price": [210.0],
            },
            index=pd.Index(["AAPL"], name="symbol"),
        )
        mock_industry.top_growth_companies = pd.DataFrame(
            {
                "name": ["Samsung Electronics"],
                "ytd return": [0.08],
                "growth estimate": [0.12],
            },
            index=pd.Index(["005930.KS"], name="symbol"),
        )

        response = SectorServiceServicer().GetIndustry(
            sector_pb2.GetIndustryRequest(key="consumer-electronics"), Mock()
        )

        mock_industry_cls.assert_called_once_with("consumer-electronics")
        assert response.key == "consumer-electronics"
        assert response.name == "Consumer Electronics"
        assert response.sector_key == "technology"
        assert response.sector_name == "Technology"
        assert response.overview.companies_count == 20
        assert response.overview.market_weight == 0.12
        assert len(response.top_companies) == 1
        assert response.top_companies[0].symbol == "AAPL"
        assert len(response.top_performing_companies) == 1
        assert response.top_performing_companies[0].symbol == "AAPL"
        assert response.top_performing_companies[0].ytd_return == 0.15
        assert response.top_performing_companies[0].last_price == 185.0
        assert response.top_performing_companies[0].target_price == 210.0
        assert len(response.top_growth_companies) == 1
        assert response.top_growth_companies[0].symbol == "005930.KS"
        assert response.top_growth_companies[0].growth_estimate == 0.12

    def test_get_industry_empty_key_returns_invalid_argument(self):
        context = Mock()
        SectorServiceServicer().GetIndustry(
            sector_pb2.GetIndustryRequest(key=""), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)

    @patch("src.sector_server.yf.Industry")
    def test_get_industry_exception_returns_internal_error(self, mock_industry_cls):
        mock_industry_cls.side_effect = Exception("API error")
        context = Mock()
        SectorServiceServicer().GetIndustry(
            sector_pb2.GetIndustryRequest(key="consumer-electronics"), context
        )
        context.set_code.assert_called_once_with(grpc.StatusCode.INTERNAL)

    @patch("src.sector_server.yf.Industry")
    def test_get_industry_no_company_data(self, mock_industry_cls):
        mock_industry = Mock()
        mock_industry_cls.return_value = mock_industry
        mock_industry.key = "consumer-electronics"
        mock_industry.name = "Consumer Electronics"
        mock_industry.symbol = "^CSELEC"
        mock_industry.sector_key = "technology"
        mock_industry.sector_name = "Technology"
        mock_industry.overview = {}
        mock_industry.top_companies = None
        mock_industry.top_performing_companies = None
        mock_industry.top_growth_companies = None

        response = SectorServiceServicer().GetIndustry(
            sector_pb2.GetIndustryRequest(key="consumer-electronics"), Mock()
        )

        assert response.top_companies == []
        assert response.top_performing_companies == []
        assert response.top_growth_companies == []
