"""SearchService: wraps yfinance.Search and yfinance.Lookup."""

import grpc
import yfinance as yf
from google.protobuf.timestamp_pb2 import Timestamp
from yfinance_grpc.v1alpha1 import search_pb2, search_pb2_grpc

from yfinance_grpc_server.convert import safe_float, safe_str
from yfinance_grpc_server.errors import require, rpc

# LookupType -> name of the public yfinance.Lookup method that serves it.
_LOOKUP_METHODS = {
    search_pb2.LOOKUP_TYPE_UNSPECIFIED: "get_all",
    search_pb2.LOOKUP_TYPE_ALL: "get_all",
    search_pb2.LOOKUP_TYPE_EQUITY: "get_stock",
    search_pb2.LOOKUP_TYPE_MUTUALFUND: "get_mutualfund",
    search_pb2.LOOKUP_TYPE_ETF: "get_etf",
    search_pb2.LOOKUP_TYPE_INDEX: "get_index",
    search_pb2.LOOKUP_TYPE_FUTURE: "get_future",
    search_pb2.LOOKUP_TYPE_CURRENCY: "get_currency",
    search_pb2.LOOKUP_TYPE_CRYPTOCURRENCY: "get_cryptocurrency",
}


class SearchServiceServicer(search_pb2_grpc.SearchServiceServicer):
    @rpc
    def Search(
        self, request: search_pb2.SearchRequest, context: grpc.ServicerContext
    ) -> search_pb2.SearchResponse:
        result = yf.Search(
            query=require(request.query, "query"),
            max_results=request.max_results if request.max_results > 0 else 8,
            news_count=request.news_count if request.news_count > 0 else 8,
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
            for q in result.quotes or []
        ]

        news = []
        for n in result.news or []:
            item = search_pb2.SearchNewsItem(
                uuid=safe_str(n.get("id", n.get("uuid"))),
                title=safe_str(n.get("title")),
                publisher=safe_str(n.get("publisher")),
                link=safe_str(n.get("link")),
                type=safe_str(n.get("type")),
            )
            if pub_time := n.get("providerPublishTime"):
                ts = Timestamp()
                ts.FromSeconds(int(pub_time))
                item.provider_publish_time.CopyFrom(ts)
            news.append(item)

        return search_pb2.SearchResponse(quotes=quotes, news=news)

    @rpc
    def Lookup(
        self, request: search_pb2.LookupRequest, context: grpc.ServicerContext
    ) -> search_pb2.LookupResponse:
        lookup = yf.Lookup(query=require(request.query, "query"))
        get = getattr(lookup, _LOOKUP_METHODS.get(request.type, "get_all"))
        df = get(count=request.count if request.count > 0 else 25)

        results = []
        if df is not None and not df.empty:
            for symbol, row in df.iterrows():
                results.append(
                    search_pb2.LookupResult(
                        symbol=safe_str(symbol),
                        name=safe_str(row.get("shortName", row.get("longName", row.get("name")))),
                        exchange=safe_str(row.get("exchange")),
                        quote_type=safe_str(row.get("quoteType", row.get("typeDisp"))),
                        score=safe_float(row.get("score")),
                    )
                )
        return search_pb2.LookupResponse(results=results)
