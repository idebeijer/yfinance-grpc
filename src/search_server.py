"""SearchService gRPC implementation. Wraps yfinance.Search and yfinance.Lookup."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gen"))

import grpc
import logging

import yfinance as yf
import pandas as pd

from yfinance_grpc.v1alpha1 import search_pb2, search_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

logger = logging.getLogger(__name__)


def safe_float(val, default: float = 0.0) -> float:
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return float(val)
    except (TypeError, ValueError):
        return default


def safe_str(val, default: str = "") -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return default
    return str(val)


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
