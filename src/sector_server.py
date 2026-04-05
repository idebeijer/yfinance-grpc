"""SectorService gRPC implementation. Wraps yfinance.Sector and yfinance.Industry."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

import grpc
import logging

import yfinance as yf
import pandas as pd

from yfinance_grpc.v1alpha1 import sector_pb2, sector_pb2_grpc

logger = logging.getLogger(__name__)


def safe_float(val, default: float = 0.0) -> float:
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return float(val)
    except (TypeError, ValueError):
        return default


def safe_int(val, default: int = 0) -> int:
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return int(val)
    except (TypeError, ValueError):
        return default


def safe_str(val, default: str = "") -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return default
    return str(val)


def _parse_overview(overview: dict) -> sector_pb2.DomainOverview:
    if not overview:
        return sector_pb2.DomainOverview()
    return sector_pb2.DomainOverview(
        companies_count=safe_int(overview.get("companies_count")),
        market_cap=safe_float(overview.get("market_cap")),
        description=safe_str(overview.get("description")),
        industries_count=safe_int(overview.get("industries_count")),
        market_weight=safe_float(overview.get("market_weight")),
        employee_count=safe_float(overview.get("employee_count")),
    )


def _parse_top_companies(df) -> list:
    if df is None or df.empty:
        return []
    return [
        sector_pb2.DomainCompany(
            symbol=safe_str(symbol),
            name=safe_str(row.get("name")),
            rating=safe_str(row.get("rating")),
            market_weight=safe_float(row.get("market weight")),
        )
        for symbol, row in df.iterrows()
    ]


class SectorServiceServicer(sector_pb2_grpc.SectorServiceServicer):
    def GetSector(self, request, context):
        if not request.key:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("key must not be empty")
            return sector_pb2.GetSectorResponse()
        try:
            sector = yf.Sector(request.key)

            industries = []
            ind_df = sector.industries
            if ind_df is not None and not ind_df.empty:
                for key, row in ind_df.iterrows():
                    industries.append(sector_pb2.IndustryInfo(
                        key=safe_str(key),
                        name=safe_str(row.get("name")),
                        symbol=safe_str(row.get("symbol")),
                        market_weight=safe_float(row.get("market weight")),
                    ))

            top_etfs = {k: safe_str(v) for k, v in (sector.top_etfs or {}).items() if k}
            top_mfs = {k: safe_str(v) for k, v in (sector.top_mutual_funds or {}).items() if k}

            return sector_pb2.GetSectorResponse(
                key=safe_str(sector.key),
                name=safe_str(sector.name),
                symbol=safe_str(sector.symbol),
                overview=_parse_overview(sector.overview),
                top_companies=_parse_top_companies(sector.top_companies),
                top_etfs=top_etfs,
                top_mutual_funds=top_mfs,
                industries=industries,
            )
        except Exception as e:
            logger.error(f"Error in GetSector for '{request.key}': {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching sector: {e}")
            return sector_pb2.GetSectorResponse()

    def GetIndustry(self, request, context):
        if not request.key:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("key must not be empty")
            return sector_pb2.GetIndustryResponse()
        try:
            industry = yf.Industry(request.key)

            top_performing = []
            tp_df = industry.top_performing_companies
            if tp_df is not None and not tp_df.empty:
                for symbol, row in tp_df.iterrows():
                    top_performing.append(sector_pb2.TopPerformingCompany(
                        symbol=safe_str(symbol),
                        name=safe_str(row.get("name")),
                        ytd_return=safe_float(row.get("ytd return")),
                        last_price=safe_float(row.get("last price")),
                        target_price=safe_float(row.get("target price")),
                    ))

            top_growth = []
            tg_df = industry.top_growth_companies
            if tg_df is not None and not tg_df.empty:
                for symbol, row in tg_df.iterrows():
                    top_growth.append(sector_pb2.TopGrowthCompany(
                        symbol=safe_str(symbol),
                        name=safe_str(row.get("name")),
                        ytd_return=safe_float(row.get("ytd return")),
                        growth_estimate=safe_float(row.get("growth estimate")),
                    ))

            return sector_pb2.GetIndustryResponse(
                key=safe_str(industry.key),
                name=safe_str(industry.name),
                symbol=safe_str(industry.symbol),
                sector_key=safe_str(industry.sector_key),
                sector_name=safe_str(industry.sector_name),
                overview=_parse_overview(industry.overview),
                top_companies=_parse_top_companies(industry.top_companies),
                top_performing_companies=top_performing,
                top_growth_companies=top_growth,
            )
        except Exception as e:
            logger.error(f"Error in GetIndustry for '{request.key}': {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching industry: {e}")
            return sector_pb2.GetIndustryResponse()
