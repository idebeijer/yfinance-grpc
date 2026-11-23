"""SectorService: wraps yfinance.Sector and yfinance.Industry."""

import grpc
import pandas as pd
import yfinance as yf
from yfinance_grpc.v1alpha1 import sector_pb2, sector_pb2_grpc

from yfinance_grpc_server.convert import safe_float, safe_int, safe_str
from yfinance_grpc_server.errors import require, rpc


def _rows(df: pd.DataFrame | None):
    """Iterate (index, row) pairs, treating None and empty frames alike."""
    if df is None or df.empty:
        return iter(())
    return df.iterrows()


def _overview(overview: dict | None) -> sector_pb2.DomainOverview:
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


def _top_companies(df: pd.DataFrame | None) -> list[sector_pb2.DomainCompany]:
    return [
        sector_pb2.DomainCompany(
            symbol=safe_str(symbol),
            name=safe_str(row.get("name")),
            rating=safe_str(row.get("rating")),
            market_weight=safe_float(row.get("market weight")),
        )
        for symbol, row in _rows(df)
    ]


def _str_map(mapping: dict | None) -> dict[str, str]:
    return {k: safe_str(v) for k, v in (mapping or {}).items() if k}


class SectorServiceServicer(sector_pb2_grpc.SectorServiceServicer):
    @rpc
    def GetSector(
        self, request: sector_pb2.GetSectorRequest, context: grpc.ServicerContext
    ) -> sector_pb2.GetSectorResponse:
        sector = yf.Sector(require(request.key, "key"))
        industries = [
            sector_pb2.IndustryInfo(
                key=safe_str(key),
                name=safe_str(row.get("name")),
                symbol=safe_str(row.get("symbol")),
                market_weight=safe_float(row.get("market weight")),
            )
            for key, row in _rows(sector.industries)
        ]
        return sector_pb2.GetSectorResponse(
            key=safe_str(sector.key),
            name=safe_str(sector.name),
            symbol=safe_str(sector.symbol),
            overview=_overview(sector.overview),
            top_companies=_top_companies(sector.top_companies),
            top_etfs=_str_map(sector.top_etfs),
            top_mutual_funds=_str_map(sector.top_mutual_funds),
            industries=industries,
        )

    @rpc
    def GetIndustry(
        self, request: sector_pb2.GetIndustryRequest, context: grpc.ServicerContext
    ) -> sector_pb2.GetIndustryResponse:
        industry = yf.Industry(require(request.key, "key"))
        top_performing = [
            sector_pb2.TopPerformingCompany(
                symbol=safe_str(symbol),
                name=safe_str(row.get("name")),
                ytd_return=safe_float(row.get("ytd return")),
                last_price=safe_float(row.get("last price")),
                target_price=safe_float(row.get("target price")),
            )
            for symbol, row in _rows(industry.top_performing_companies)
        ]
        top_growth = [
            sector_pb2.TopGrowthCompany(
                symbol=safe_str(symbol),
                name=safe_str(row.get("name")),
                ytd_return=safe_float(row.get("ytd return")),
                growth_estimate=safe_float(row.get("growth estimate")),
            )
            for symbol, row in _rows(industry.top_growth_companies)
        ]
        return sector_pb2.GetIndustryResponse(
            key=safe_str(industry.key),
            name=safe_str(industry.name),
            symbol=safe_str(industry.symbol),
            sector_key=safe_str(industry.sector_key),
            sector_name=safe_str(industry.sector_name),
            overview=_overview(industry.overview),
            top_companies=_top_companies(industry.top_companies),
            top_performing_companies=top_performing,
            top_growth_companies=top_growth,
        )
