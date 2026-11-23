"""MarketService: wraps yfinance.Market."""

import grpc
import yfinance as yf
from yfinance_grpc.v1alpha1 import market_pb2, market_pb2_grpc

from yfinance_grpc_server.convert import safe_float, safe_int, safe_str, to_timestamp
from yfinance_grpc_server.errors import not_found, require, rpc


class MarketServiceServicer(market_pb2_grpc.MarketServiceServicer):
    @rpc
    def GetMarketStatus(
        self, request: market_pb2.GetMarketStatusRequest, context: grpc.ServicerContext
    ) -> market_pb2.GetMarketStatusResponse:
        market = require(request.market, "market")
        status = yf.Market(market).status
        if not status:
            raise not_found(f"No status data for market '{market}'")

        tz = status.get("timezone") if isinstance(status.get("timezone"), dict) else {}
        msg = market_pb2.MarketStatus(
            market_type=safe_str(status.get("type")),
            timezone_short=safe_str(tz.get("short")),
            timezone_gmtoffset=safe_int(tz.get("gmtoffset")),
        )
        for field in ("open", "close"):
            if ts := to_timestamp(status.get(field)):
                getattr(msg, field).CopyFrom(ts)

        return market_pb2.GetMarketStatusResponse(status=msg)

    @rpc
    def GetMarketSummary(
        self, request: market_pb2.GetMarketSummaryRequest, context: grpc.ServicerContext
    ) -> market_pb2.GetMarketSummaryResponse:
        market = require(request.market, "market")
        summary = yf.Market(market).summary
        # yfinance returns {'finance': {'result': None, 'error': ...}} when the
        # market identifier is not valid for the summary endpoint.
        if not summary or "finance" in summary:
            raise not_found(f"No summary data for market '{market}'")

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
