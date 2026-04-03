"""
SearchService, MarketService, and SectorService gRPC implementations.

Wraps yfinance.Search, yfinance.Lookup, yfinance.Market, yfinance.Sector,
and yfinance.Industry.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

import grpc
import logging
from datetime import datetime

import yfinance as yf
import pandas as pd

from yfinance_grpc.v1 import search_pb2, search_pb2_grpc, market_pb2, market_pb2_grpc, sector_pb2, sector_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers (mirrors server.py, kept local to avoid circular imports)
# ---------------------------------------------------------------------------

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


def _dt_to_ts(dt) -> Timestamp | None:
    if dt is None:
        return None
    if isinstance(dt, pd.Timestamp):
        dt = dt.to_pydatetime()
    if isinstance(dt, datetime):
        ts = Timestamp()
        ts.FromDatetime(dt)
        return ts
    return None


# ---------------------------------------------------------------------------
# LookupType enum → yfinance string
# ---------------------------------------------------------------------------

_LOOKUP_TYPE_STR = {
    search_pb2.LOOKUP_TYPE_UNSPECIFIED: "all",
    search_pb2.LOOKUP_TYPE_ALL: "all",
    search_pb2.LOOKUP_TYPE_EQUITY: "equity",
    search_pb2.LOOKUP_TYPE_MUTUALFUND: "mutualfund",
    search_pb2.LOOKUP_TYPE_ETF: "etf",
    search_pb2.LOOKUP_TYPE_INDEX: "index",
    search_pb2.LOOKUP_TYPE_FUTURE: "future",
    search_pb2.LOOKUP_TYPE_CURRENCY: "currency",
    search_pb2.LOOKUP_TYPE_CRYPTOCURRENCY: "cryptocurrency",
}


# ---------------------------------------------------------------------------
# SearchServiceServicer
# ---------------------------------------------------------------------------

class SearchServiceServicer(search_pb2_grpc.SearchServiceServicer):
    def Search(self, request, context):
        if not request.query:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("query must not be empty")
            return search_pb2.SearchResponse()
        try:
            max_results = request.max_results if request.max_results > 0 else 8
            news_count = request.news_count if request.news_count > 0 else 8
            result = yf.Search(
                query=request.query,
                max_results=max_results,
                news_count=news_count,
                enable_fuzzy_query=request.enable_fuzzy_query,
            )

            quotes = [
                search_pb2.SearchQuote(
                    symbol=safe_str(q.get("symbol")),
                    short_name=safe_str(q.get("shortName")),
                    long_name=safe_str(q.get("longName")),
                    exchange=safe_str(q.get("exchange")),
                    quote_type=safe_str(q.get("quoteType")),
                    sector=safe_str(q.get("sector")),
                    industry=safe_str(q.get("industry")),
                    type_disp=safe_str(q.get("typeDisp")),
                    score=safe_float(q.get("score")),
                )
                for q in (result.quotes or [])
            ]

            news = []
            for n in result.news or []:
                item = search_pb2.SearchNewsItem(
                    uuid=safe_str(n.get("id", n.get("uuid", ""))),
                    title=safe_str(n.get("title")),
                    publisher=safe_str(n.get("publisher")),
                    link=safe_str(n.get("link")),
                    type=safe_str(n.get("type")),
                )
                pub_time = n.get("providerPublishTime")
                if pub_time:
                    ts = Timestamp()
                    ts.FromSeconds(int(pub_time))
                    item.provider_publish_time.CopyFrom(ts)
                news.append(item)

            return search_pb2.SearchResponse(quotes=quotes, news=news)
        except Exception as e:
            logger.error(f"Error in Search for '{request.query}': {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error searching: {e}")
            return search_pb2.SearchResponse()

    def Lookup(self, request, context):
        if not request.query:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("query must not be empty")
            return search_pb2.LookupResponse()
        try:
            lookup_type = _LOOKUP_TYPE_STR.get(request.type, "all")
            count = request.count if request.count > 0 else 25

            lookup = yf.Lookup(query=request.query)
            df = lookup._get_data(lookup_type, count)

            results = []
            if df is not None and not df.empty:
                for symbol, row in df.iterrows():
                    results.append(search_pb2.LookupResult(
                        symbol=safe_str(symbol),
                        name=safe_str(row.get("shortName", row.get("longName", row.get("name", "")))),
                        exchange=safe_str(row.get("exchange", "")),
                        quote_type=safe_str(row.get("quoteType", row.get("typeDisp", ""))),
                        score=safe_float(row.get("score")),
                    ))
            return search_pb2.LookupResponse(results=results)
        except Exception as e:
            logger.error(f"Error in Lookup for '{request.query}': {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error looking up: {e}")
            return search_pb2.LookupResponse()


# ---------------------------------------------------------------------------
# MarketServiceServicer
# ---------------------------------------------------------------------------

class MarketServiceServicer(market_pb2_grpc.MarketServiceServicer):
    def GetMarketStatus(self, request, context):
        if not request.market:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("market must not be empty")
            return market_pb2.GetMarketStatusResponse()
        try:
            status = yf.Market(request.market).status
            if not status:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"No status data for market '{request.market}'")
                return market_pb2.GetMarketStatusResponse()

            tz = status.get("timezone") if isinstance(status.get("timezone"), dict) else {}
            msg = market_pb2.MarketStatus(
                market_type=safe_str(status.get("type")),
                timezone_short=safe_str(tz.get("short")),
                timezone_gmtoffset=safe_int(tz.get("gmtoffset")),
            )
            for field, attr in (("open", "open"), ("close", "close")):
                dt_val = status.get(attr)
                ts = _dt_to_ts(dt_val)
                if ts:
                    getattr(msg, field).CopyFrom(ts)

            return market_pb2.GetMarketStatusResponse(status=msg)
        except Exception as e:
            logger.error(f"Error in GetMarketStatus for '{request.market}': {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching market status: {e}")
            return market_pb2.GetMarketStatusResponse()

    def GetMarketSummary(self, request, context):
        if not request.market:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("market must not be empty")
            return market_pb2.GetMarketSummaryResponse()
        try:
            summary = yf.Market(request.market).summary
            if not summary:
                return market_pb2.GetMarketSummaryResponse()

            items = {
                exchange: market_pb2.MarketSummaryItem(
                    short_name=safe_str(data.get("shortName")),
                    regular_market_price=safe_float(data.get("regularMarketPrice")),
                    regular_market_change=safe_float(data.get("regularMarketChange")),
                    regular_market_change_percent=safe_float(data.get("regularMarketChangePercent")),
                )
                for exchange, data in summary.items()
            }
            return market_pb2.GetMarketSummaryResponse(summary=items)
        except Exception as e:
            logger.error(f"Error in GetMarketSummary for '{request.market}': {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching market summary: {e}")
            return market_pb2.GetMarketSummaryResponse()


# ---------------------------------------------------------------------------
# SectorServiceServicer helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# SectorServiceServicer
# ---------------------------------------------------------------------------

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
